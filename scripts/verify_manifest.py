#!/usr/bin/env python3
"""Read and hash the three named outputs against a UniXNU package manifest.

Only output sizes/hashes are checked. The manifest is not authenticated by this
tool. Runtime identity, seed details, paths and kernel arguments are not printed.
No files are written. Python 3.11+; standard library only.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys


OUTPUTS = {"boot.img": "boot/boot.img", "payload.img": "payload/payload.img",
           "kernel.macho": "kernel/kernel.macho"}


def inspect(root, manifest):
    root = root.resolve(strict=True)
    if manifest.stat().st_size > 8 * 1024**2:
        raise ValueError("Manifest exceeds checker budget")
    document = json.loads(manifest.read_text(encoding="utf-8"))
    declared = document["outputs"]
    if set(declared) != set(OUTPUTS):
        raise ValueError("Expected exactly boot.img, payload.img and kernel.macho")
    rows = {}
    for name, relative in OUTPUTS.items():
        path = (root / relative).resolve(strict=True)
        if not path.is_relative_to(root):
            raise ValueError("Output resolves outside selected root: " + name)
        before = path.stat()
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ValueError("Output changed during read: " + name)
        expected = declared[name]
        if expected["bytes"] != after.st_size or expected["sha256"] != digest:
            raise ValueError("Output size/hash differs: " + name)
        rows[name] = {"bytes": after.st_size, "sha256": digest}
    return {"status": "output_sizes_and_hashes_match_manifest",
            "manifest_authenticated": False, "full_static_acceptance": False,
            "outputs": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = inspect(args.output_root, args.manifest)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("Manifest output check failed: " + str(error), file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
