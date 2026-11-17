#!/usr/bin/env python3
"""Read a sheng Android v0 image; check only its outer packaging structure.

This original checker does not establish XNU ABI, cryptographic trust, device
identity, AVB acceptance, loader handoff, or hardware behavior. It writes no
files and never invokes a device tool. Python 3.11+; standard library only.
"""

import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
import zlib


class InvalidImage(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidImage(message)


def align(value, page):
    return (value + page - 1) // page * page


def check_fat(payload):
    require(len(payload) >= 512, "Payload boot sector truncated")
    require(payload[510:512] == b"\x55\xaa", "FAT boot-sector signature missing")
    sector_bytes = struct.unpack_from("<H", payload, 11)[0]
    cluster_sectors = payload[13]
    reserved = struct.unpack_from("<H", payload, 14)[0]
    fats = payload[16]
    root_entries = struct.unpack_from("<H", payload, 17)[0]
    total16 = struct.unpack_from("<H", payload, 19)[0]
    fat16 = struct.unpack_from("<H", payload, 22)[0]
    total32 = struct.unpack_from("<I", payload, 32)[0]
    require(sector_bytes in (512, 1024, 2048, 4096), "Unsupported FAT sector size")
    require(cluster_sectors in (1, 2, 4, 8, 16, 32, 64, 128), "Invalid FAT cluster size")
    require(reserved > 0 and fats in (1, 2), "Invalid FAT reserved/FAT counts")
    require(not (total16 and total32), "Ambiguous FAT volume length")
    sectors = total16 or total32
    require(sectors > 0 and sectors * sector_bytes == len(payload), "FAT length differs from ramdisk extent")
    fat_sectors = fat16 or struct.unpack_from("<I", payload, 36)[0]
    root_sectors = (root_entries * 32 + sector_bytes - 1) // sector_bytes
    data_sectors = sectors - reserved - fats * fat_sectors - root_sectors
    require(fat_sectors > 0 and data_sectors > 0, "Invalid FAT region geometry")
    clusters = data_sectors // cluster_sectors
    kind = "FAT12" if clusters < 4085 else "FAT16" if clusters < 65525 else "FAT32"
    if kind == "FAT32":
        require(not fat16 and not root_entries, "FAT32 BPB uses FAT16 fields")
    else:
        require(fat16 > 0 and root_entries > 0, "FAT12/16 BPB fields missing")
    return {"kind": kind, "bytes": len(payload), "sector_bytes": sector_bytes,
            "cluster_sectors": cluster_sectors, "geometry_checked_only": True}


def check_dtbs(tail):
    offset = 0
    rows = []
    while offset < len(tail):
        require(len(tail) - offset >= 40, "Appended FDT header truncated")
        fields = struct.unpack_from(">10I", tail, offset)
        magic, total, structure, strings, reserve, version, compatible, _, string_size, structure_size = fields
        require(magic == 0xD00DFEED, "Invalid appended FDT magic")
        require(total >= 40 and offset + total <= len(tail), "FDT total length exceeds tail")
        require(version >= 17 and compatible <= 17, "Unsupported FDT version")
        require(structure % 4 == 0 and reserve % 8 == 0, "FDT block alignment differs")
        for start, size in ((structure, structure_size), (strings, string_size)):
            require(start >= 40 and start + size <= total, "FDT block exceeds declared extent")
        require(40 <= reserve <= total - 16, "FDT reservation-map bounds")
        cursor = reserve
        while cursor + 16 <= total:
            address, size = struct.unpack_from(">2Q", tail, offset + cursor)
            cursor += 16
            if not address and not size:
                break
        else:
            raise InvalidImage("FDT reservation map has no terminator")
        blob = tail[offset:offset + total]
        rows.append({"offset": offset, "bytes": total,
                     "sha256": hashlib.sha256(blob).hexdigest()})
        offset += total
    require(bool(rows), "No appended outer DTB")
    return rows


def inspect(path, expected_dtbs=None, max_bytes=512 * 1024**2):
    size = path.stat().st_size
    require(1632 <= size <= max_bytes, "Image length outside checker budget")
    data = path.read_bytes()
    require(len(data) == size, "Image changed during read")
    require(data[:8] == b"ANDROID!", "Android boot magic missing")
    kernel_size, kernel_address, ramdisk_size, ramdisk_address, second_size, second_address, tags, page, version, _ = struct.unpack_from("<10I", data, 8)
    require(version == 0, "Only Android boot header v0 is supported")
    require(page == 4096, "Expected sheng outer page size 4096")
    require(kernel_address == 0x8000 and tags == 0x1E00000, "Expected sheng load offsets differ")
    require(ramdisk_address == 0x1000000, "Expected sheng ramdisk address differs")
    require(not second_size and not second_address, "Unexpected second stage")
    require(kernel_size > 0 and ramdisk_size > 0, "Kernel/payload extent is empty")
    kernel_end = page + kernel_size
    ramdisk_start = page + align(kernel_size, page)
    ramdisk_end = ramdisk_start + ramdisk_size
    expected_end = ramdisk_start + align(ramdisk_size, page)
    require(expected_end == len(data) and kernel_end <= ramdisk_start <= ramdisk_end <= len(data), "Extent, file length, or trailing data differs")
    require(not any(data[1632:page]), "Nonzero v0 header padding")
    require(not any(data[kernel_end:ramdisk_start]), "Nonzero kernel padding")
    require(not any(data[ramdisk_end:expected_end]), "Nonzero ramdisk padding")
    kernel = data[page:kernel_end]
    payload = data[ramdisk_start:ramdisk_end]
    identity = hashlib.sha1()
    for section in (kernel, payload, b""):
        identity.update(section)
        identity.update(struct.pack("<I", len(section)))
    require(data[576:608] == identity.digest() + bytes(12), "Android v0 SHA-1 image ID differs")
    unpacker = zlib.decompressobj(16 + zlib.MAX_WBITS)
    firmware = unpacker.decompress(kernel, 16 * 1024**2 + 1)
    require(len(firmware) <= 16 * 1024**2 and not unpacker.unconsumed_tail, "Firmware decompression exceeds checker budget")
    require(unpacker.eof, "Gzip stream truncated or invalid")
    require(firmware[56:60] == b"ARM\x64", "BootShim ARM64 image header missing")
    require(len(firmware) == 192 + 0x300000, "Expected run 41 shim + 3 MiB FD length differs")
    load_base, image_bytes = struct.unpack_from("<2Q", firmware, 8)
    require(load_base == 0xA7100000 and image_bytes == len(firmware), "BootShim load/size fields differ")
    dtbs = check_dtbs(unpacker.unused_data)
    if expected_dtbs is not None:
        require(len(dtbs) == expected_dtbs, "Appended DTB count differs")
    fat = check_fat(payload)
    return {"status": "limited_outer_checks_passed",
            "scope": "Android v0 extents, ID, zero padding, gzip/shim header, FDT bounds, FAT BPB geometry",
            "full_static_acceptance": False, "hardware_tested": False,
            "bytes": size, "sha256": hashlib.sha256(data).hexdigest(),
            "header_version": version, "page_size": page, "kernel_bytes": kernel_size,
            "firmware_bytes": len(firmware), "firmware_sha256": hashlib.sha256(firmware).hexdigest(),
            "dtb_count": len(dtbs), "dtbs": dtbs,
            "payload_sha256": hashlib.sha256(payload).hexdigest(), "payload": fat}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--expected-dtbs", type=int, choices=(1, 8))
    args = parser.parse_args()
    try:
        report = inspect(args.image, args.expected_dtbs)
    except (OSError, ValueError, zlib.error, struct.error) as error:
        print("Outer image check failed: " + str(error), file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
