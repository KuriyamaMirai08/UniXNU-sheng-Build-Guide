# Building iPadOS 27.0.1 (24A446) for sheng

This guide follows the order actually used by successful run 41. Commands are adapted from retained build records, with private absolute paths replaced by variables. **The documentation audit reproduced source preparation and selected checks; it did not perform another full build on a new Mac.** Read [reproduction gaps](REPRODUCIBILITY_GAPS.md) and [third-party notices](../THIRD_PARTY_NOTICES.md) first.

The target is Xiaomi Pad 6S Pro 12.4, `sheng` / SM8550, OS profile `ipados-27.0.1-24A446`, defconfig `sheng_ipados27_defconfig`, output directory name `sheng_ipados27`. Different OS versions, storage layouts, toolchains or installation inputs need their own qualification.

Commands below run in **Bash on macOS**, not Windows PowerShell. Keep the same shell and variables across sections. Use a new isolated directory and preserve successful builds and private inputs.

## 1. Prepare the host

Run 41 used an Apple arm64 host, macOS 26.7.2 (25G332), Xcode 26.6 (17F113), iPhoneOS SDK 26.5 and Apple Clang 21.0.0 (`clang-2100.1.1.101`). Rust was 1.98.0 and Python was 3.15.2. See [the version index](SOURCES_AND_VERSIONS.md) for the complete table.

Allow at least 100 GiB free; 150 GiB or more is advisable when retaining full archives. These are recommendations, not measured minimums. The successful hosted machine had 3 cores, 7 GiB RAM and used `-j 3`; it had approximately 94.36 GiB free before fetch. Use an APFS directory with working symbolic links.

Install the full, matching Xcode through an authorized source. Command Line Tools alone are insufficient. Adjust the path to your actual installation:

```bash
export DEVELOPER_DIR=/Applications/Xcode_26.6.app/Contents/Developer
test -d "$DEVELOPER_DIR"
xcodebuild -version
xcrun --sdk iphoneos --show-sdk-version
xcrun --sdk iphoneos clang --version
xcrun --sdk iphoneos --find clang | xargs shasum -a 256
```

The compiler SHA-256 is `d2e4bf622758eee1bf7267c060497fb2c41e098d37b0fca8be73898dc7e14eda`. A working `xcodebuild -version` does not prove all Xcode system components are installed. If the historical missing CoreSimulator / exit 70 error occurs, the Mac administrator must complete `sudo xcodebuild -runFirstLaunch`; see [BUG-009](BUG_FIXES.md#bug-009).

Install Homebrew through its official instructions. The following dependency command was used by the successful workflow, but **does not freeze formula or bottle versions**:

```bash
export HOMEBREW_NO_AUTO_UPDATE=1
brew install dtc llvm lld cmake mtools ninja glslang shaderc spirv-tools bison pkgconf rustup blacktop/tap/ipsw
rustup toolchain install 1.98.0 --profile minimal --component rust-src
export RUSTUP_TOOLCHAIN=1.98.0
```

Compare `brew list --versions` with the version index. In particular, run 41 had LLVM/LLD 23.1.4, dtc 1.8.1, cmake 4.4.5, ninja 1.13.2, mtools 4.0.50 and bison 3.8.2. Prepare matching versions using your authorized installers, formula snapshots or existing environment. This audit did not validate a command that reconstructs the old Homebrew/runner image from scratch.

## 2. Create an isolated workspace

Start at this guide repository's root:

```bash
export GUIDE_ROOT="$PWD"
export BUILD_ROOT="$HOME/UniXNU-sheng-run41-study"
test ! -e "$BUILD_ROOT"
mkdir -m 700 "$BUILD_ROOT"
mkdir "$BUILD_ROOT/evidence" "$BUILD_ROOT/caches"

python3 --version
python3 -m venv "$BUILD_ROOT/.venv"
"$BUILD_ROOT/.venv/bin/pip" install cryptography==50.0.2 cffi==2.1.1 pycparser==3.12
export PATH="$BUILD_ROOT/.venv/bin:$HOME/.cargo/bin:/opt/homebrew/opt/bison/bin:/opt/homebrew/opt/lld/bin:/opt/homebrew/opt/llvm/bin:/opt/homebrew/bin:$PATH"
unset PYTHONPATH PYTHONHOME CC CXX CFLAGS CXXFLAGS LDFLAGS BASH_ENV
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export ZERO_AR_DATE=1
export UNIXNU_SHENG_BOOT_CANDIDATE=1
export UNIXNU_SHENG_AUTHOR_AUDIT=1
for name in TMPDIR XDG_CACHE_HOME CLANG_MODULE_CACHE_PATH CARGO_TARGET_DIR; do
  mkdir "$BUILD_ROOT/caches/$name"
  export "$name=$BUILD_ROOT/caches/$name"
done
set -euo pipefail
```

Check that `python3` is the intended version before creating the venv. The original harness also removes every `CCACHE_`/`SCCACHE_` variable; use a clean shell if you have such settings. Do not print a full environment or use `set -x` with private inputs.

The PATH entries expose LLVM tools needed by EDK and inspection. Mach-O/XNU recipes still select Xcode's Apple compiler. Making `lld-link` available is not a reason to replace all Apple Clang invocations with Homebrew Clang.

## 3. Fetch exactly the successful source revisions

The final device fixes live in a personal fork. Credit the [official device repository](https://github.com/UniXNU/UniXNU-sheng), but do not assume its current `main` contains the fork's fixes.

```bash
export DEVICE_SHA=a9f0500af098f8aee87c86a571638daee92caf26
export FRAMEWORK_SHA=97437dcf7389484a0eeaa8067725ce743aff18ef
export UEFI_SHA=66421cb7bb5694843aec8de1ca3d1de4c20cca38

git init "$BUILD_ROOT/device"
git -C "$BUILD_ROOT/device" fetch --depth 1 https://github.com/KuriyamaMirai08/UniXNU-sheng.git "$DEVICE_SHA"
git -C "$BUILD_ROOT/device" checkout --detach "$DEVICE_SHA"
git -C "$BUILD_ROOT/device" submodule update --init --recursive

git init "$BUILD_ROOT/UniXNU"
git -C "$BUILD_ROOT/UniXNU" fetch --depth 1 https://github.com/UniXNU/UniXNU.git "$FRAMEWORK_SHA"
git -C "$BUILD_ROOT/UniXNU" checkout --detach "$FRAMEWORK_SHA"
git -C "$BUILD_ROOT/UniXNU" submodule update --init --recursive

git init "$BUILD_ROOT/uefi-sheng"
git -C "$BUILD_ROOT/uefi-sheng" fetch --depth 1 https://github.com/UniXNU/uefi-sheng.git "$UEFI_SHA"
git -C "$BUILD_ROOT/uefi-sheng" checkout --detach "$UEFI_SHA"

test "$(git -C "$BUILD_ROOT/device" rev-parse HEAD)" = "$DEVICE_SHA"
test "$(git -C "$BUILD_ROOT/UniXNU" rev-parse HEAD)" = "$FRAMEWORK_SHA"
test "$(git -C "$BUILD_ROOT/uefi-sheng" rev-parse HEAD)" = "$UEFI_SHA"
export UNIXNU_DEVICE="$BUILD_ROOT/device"
export UNIXNU_ROOT="$BUILD_ROOT/UniXNU"
export UNIXNU_UEFI="$BUILD_ROOT/uefi-sheng"
```

Keep these three sibling names: `device/board.toml` selects `../UniXNU`. Fixed feeds are fetched later by the resolver. Do not replace them with latest XNU, SoC or corecrypto sources.

Do **not** recursively initialize all UEFI submodules here. The firmware builder initializes only four direct board-required paths; Mu_Basecore comes from the feed and Binaries/sheng comes from the firmware import. See [BUG-008](BUG_FIXES.md#bug-008) and [source-pins.json](../evidence/source-pins.json).

## 4. Qualify inputs before downloads and compilation

Confirm that you have permission covering the intended use of corecrypto and other dependencies. Its internal-use license does not automatically authorize a community OS port or binary redistribution. This repository supplies no restricted source, firmware, system image or installation state.

Use your own private directory outside this guide/source tree. The following names describe already-existing inputs; they do not create them:

```bash
export PRIVATE_INPUTS="$HOME/UniXNU-private-inputs"
export PRIVATE_DATA_SEED="$PRIVATE_INPUTS/data.dbr"
export UNIXNU_SHENG_BASELINE_NATIVE="$PRIVATE_INPUTS/baseline-native.macho"
export UNIXNU_SHENG_REGRESSION_SOURCE="$PRIVATE_INPUTS/baseline-kernel.py"
test -f "$UNIXNU_SHENG_BASELINE_NATIVE"
test -f "$UNIXNU_SHENG_REGRESSION_SOURCE"
```

The baseline must be the exact retained comparison evidence, with authorized access. It is not an object cache and cannot be replaced by your new native. Verify it against the fixed contract:

```bash
python3 - <<'PY'
import hashlib, json, os
from pathlib import Path
c = json.loads((Path(os.environ['UNIXNU_DEVICE']) / 'scripts/clean-prelink-contract.json').read_text())
for variable, expected in (
    ('UNIXNU_SHENG_BASELINE_NATIVE', c['inputs']['native']),
    ('UNIXNU_SHENG_REGRESSION_SOURCE', c['regression_source_sha256']),
):
    with Path(os.environ[variable]).open('rb') as f:
        actual = hashlib.file_digest(f, 'sha256').hexdigest()
    if actual != expected:
        raise SystemExit(variable + ': baseline identity differs')
print('Two baseline evidence hashes match')
PY
```

Without that retained native, the current strict contract cannot complete qualification. Historical Actions artifacts expire and are not inherited by another fork; see [reproduction gaps](REPRODUCIBILITY_GAPS.md).

Set `UNIXNU_UNIQUE_CHIP_ID` privately to **your device's** nonzero hexadecimal u64. The historical device source was `/sys/devices/soc0/serial_number`; no device probing is performed by this tutorial. Keep all high bits and leading zeroes. This platform value is distinct from a Data UUID or seed file.

```bash
python3 - <<'PY'
import os, re
s = os.environ.get('UNIXNU_UNIQUE_CHIP_ID', '')
if not re.fullmatch(r'(?:0[xX])?[0-9a-fA-F]{1,16}', s) or not int(s, 16):
    raise SystemExit('Set your own nonzero hexadecimal u64 UNIXNU_UNIQUE_CHIP_ID privately')
print('Platform identity syntax accepted; value not printed')
PY
```

For an existing installation, retain your original `data.dbr` and its private integrity record. First seed generation uses `--init-data`; it is mutually exclusive with `--data-ramdisk`. **Run 41 tested retained seed use only.** New UUIDs can change generated configuration, source hashes and function shape; the fixed qualification contract may reject them. Updating expected hashes alone would not establish correctness.

Board parameters come from `board.toml`, `configs/sheng_ipados27_defconfig`, and the selected OS/SoC profiles. Keep the selected archives, roots and boot arguments for the recorded baseline. `data_gib = 215`, userdata LBAs and memory geometry are not guarantees for every storage variant. This guide performs no userdata image creation or installation.

## 5. Apply preparation once, in the successful order

The selected device commit already contains its patches; do not cherry-pick all historical fixes again. The isolated framework and selected submodules still need their controlled transformations:

```bash
cd "$UNIXNU_DEVICE"
python3 scripts/prepare-package-ci.py --unixnu "$UNIXNU_ROOT"

python3 - <<'PY'
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(os.environ['UNIXNU_DEVICE']) / 'scripts/repro'))
from preserve import apply
apply(Path(os.environ['UNIXNU_ROOT']), Path(os.environ['BUILD_ROOT']) / 'evidence')
PY

git -C "$UNIXNU_ROOT" apply --check "$UNIXNU_DEVICE/patches/build/sheng-reference-archive.patch"
git -C "$UNIXNU_ROOT" apply "$UNIXNU_DEVICE/patches/build/sheng-reference-archive.patch"
python3 scripts/prepare-sheng-author-audit.py --unixnu "$UNIXNU_ROOT" --evidence "$BUILD_ROOT/evidence"
git -C "$UNIXNU_ROOT" diff --binary > "$BUILD_ROOT/evidence/framework-diff.patch"

cd "$UNIXNU_ROOT"
python3 scripts/test-fileset-reference.py -v
cd "$UNIXNU_DEVICE"
python3 scripts/test-author-audit-reference.py --builder "$UNIXNU_ROOT/scripts/build-fileset-release-reference.py"
```

Preparation checks exact revisions and source markers. It fixes the Ath12k commit/non-cone fetcher and generated-header bootstrap condition, retains failed patch/prelink evidence, installs a narrow bootstrap guard, adds real archive inputs, installs the reference verifier **before early tests**, and preserves absent optional providers and RELEASE assertion ABI.

Keep `preservation-transforms.json`, `optional-source-transforms.json`, and the actual diff. The original four framework tests remain enabled; six publication tests cover final-link failure and clean-environment helper installation. Reapplying these single-use transformations to an already-prepared tree can deliberately fail; diagnose its state rather than deleting a successful tree.

## 6. Fetch feeds, select configuration and assemble the tree

```bash
printf '[build]\n' > "$BUILD_ROOT/build.toml"
common=(--os 27 --out "$BUILD_ROOT/out" --config "$BUILD_ROOT/build.toml" --uefi "$UNIXNU_UEFI" -j 3)

cd "$BUILD_ROOT"
python3 "$UNIXNU_ROOT/unixnu" fetch -D "$UNIXNU_DEVICE" "${common[@]}"
cd "$UNIXNU_DEVICE"
bash scripts/package.sh "${common[@]}" --no-deps --check
cd "$BUILD_ROOT"
python3 "$UNIXNU_ROOT/unixnu" status -D "$UNIXNU_DEVICE" "${common[@]}" --json > "$BUILD_ROOT/evidence/source-status.json"
python3 "$UNIXNU_ROOT/unixnu" tree -D "$UNIXNU_DEVICE" "${common[@]}"
export WORK="$BUILD_ROOT/out/sheng/ipados-27.0.1-24A446/sheng_ipados27"
export TREE="$WORK/tree"
```

Status must select `sheng_ipados27_defconfig`, the intended OS, actual pinned revisions and **95 patches**. `--check` only lists configuration/patches; it does not assemble the tree, so the separate `tree` invocation is required ([BUG-023](BUG_FIXES.md#bug-023)).

Confirm the fresh tree has no `.o`, `.a`, `.cpo`, or `kernel.macho`; run 41 recorded an empty precompile inventory. Then run:

```bash
cd "$TREE/kits/XnuPrelink"
python3 -m unittest test_fileset_emit test_fileset_layout test_fileset_match test_fileset_shape
cd "$UNIXNU_DEVICE"
python3 scripts/check-sheng-optional-providers.py --tree "$TREE" --output "$BUILD_ROOT/evidence/optional-link"
```

The unchanged prelink engine has 36 tests in this selection. Optional-provider tests exercise actual guarded consumers and require an enabled-but-missing provider to fail. Test peers are never production native/reference inputs.

Do not manually apply all XNU patches in an arbitrary order. The resolver follows the selected arch/SoC/OS/device plan. Final entries 93–95 are `driverkit-platform-function.patch`, `sheng-image4-normal-runtime.patch`, and `sheng-image4-size.patch`. The last patch adds six local minsize attributes. Mesa has a separate 17-patch plan; do not disable its identity checks.

## 7. Fetch prerequisites before building archives

The real Image4 normal PAL archive needs the exact KernelCache before archive recipes run:

```bash
cd "$BUILD_ROOT"
python3 "$UNIXNU_ROOT/unixnu" ipsw fetch KernelCache -D "$UNIXNU_DEVICE" "${common[@]}"
export UNIXNU_KERNELCACHE="$BUILD_ROOT/out/ipsw/24A446/kernelcache.decompressed"
test -f "$UNIXNU_KERNELCACHE"
shasum -a 256 "$UNIXNU_KERNELCACHE"

cd "$UNIXNU_DEVICE"
python3 scripts/extract-files.py
bash drivers/Ath12kWifi/tools/fetch-sources.sh
python3 drivers/QcaBluetooth/tools/prepare-linux.py
python3 scripts/stage-bluetooth-firmware.py .cache/bt-stage --fetch
python3 scripts/download-sheng-firmware.py --connections 16
python3 scripts/extract-sheng-firmware.py --delete-archive
python3 scripts/import-sheng-uefi.py
```

The fixed profile uses the official IPSW URL and reads required ZIP members. Confirm 27.0.1 / 24A446 / iPad17,3 / j820ap and kernelcache SHA-256 `38e6d9fa5f789b8228f4617ef4c6d2a3fd8ab564abdc9b62920f1db53fc1780a`.

Touch/keyboard, Wi-Fi, Bluetooth and stock firmware each retain their source checks and receipts. Stock firmware is OS3.0.305.0.WNXMIXM, 7,609,308,281 bytes, SHA-256 `c6259e1c8dd89b5b16d086cbdda5d21083c2ca445dd4cde4c8917139f490c7ed`. UEFIExtract A76 is hash-checked by the importer.

`--delete-archive` removes the script's downloaded copy only after verified extraction. It does not remove your original ROM backup. Later invocations verify retained extraction and provenance rather than trusting file existence.

DTS/GPU preparation in the archive plan and firmware preflight remain enabled; their dependency checks are not removed as “duplicates.” The outer FDT/DTB and inner Apple ADT serve different consumers and are not interchangeable.

## 8. Run the original release entry

For a retained installation seed:

```bash
test -f "$PRIVATE_DATA_SEED"
cd "$UNIXNU_DEVICE"
bash scripts/package.sh "${common[@]}" --no-deps --data-ramdisk "$PRIVATE_DATA_SEED" 2>&1 | tee "$BUILD_ROOT/evidence/release.log"
```

For first seed generation, the real interface is:

```bash
# FIRST seed generation only; not the run 41 tested path.
cd "$UNIXNU_DEVICE"
bash scripts/package.sh "${common[@]}" --no-deps --init-data 2>&1 | tee "$BUILD_ROOT/evidence/first-install-release.log"
```

**Choose exactly one.** `--init-data` creates installation state but does not flash a device. Never use it to handle an existing installation's cache miss. Preserve a generated seed even if later compilation fails, and use `--data-ramdisk` next time. The fixed strict contract may still reject new input shapes; this guide does not claim that first-install reproduction has passed.

Keep kernel compilation inside `release`, after runtime preparation. The internal sequence is:

1. Preflight, defconfig and ordered tree; `runtime.prepare` reads the seed UUID and binds the generated configuration, then prepares GPU/audio/Wi-Fi/Bluetooth/AppSync and trust inputs.
2. XNU header/object bootstrap. Only the exact recorded missing-board-archive first link is conditionally accepted; compiler errors and final-link failures are not accepted.
3. Real corecrypto plain/namespaced, ArmDTPlatform, ArmCpu, storage, RamBlock, GPU, display and Image4 archives; a real RELEASE-LTO comparison using the same-run archives.
4. Real DEVELOPMENT native link, unchanged XnuPrelink engine plus strict wrapper, 17 prepared-source checks, 21 binding slots, historical ABI/shape/relocation checks, zero missing and zero stubbed.
5. UniXNU/DarwinBoot package, FAT payload, ADT, diagnostic edits and POST sealing, followed by DEBUG CLANGPDB UEFI firmware.
6. gzip(BootShim + FD), appended outer DTB, original Android v0 writer, pipeline output/hash/command-line/capacity verification and manifest.

Run 41's release stage took approximately 45m54s; preparation and archive upload took additional time. Hosted run 41 did not reuse XNU objects. The download cache was saved from a cold run; warm whole-build acceleration was not measured. See [Actions](GITHUB_ACTIONS.md).

## 9. Inspect outputs and qualify them separately

| Path | Meaning |
| --- | --- |
| `$WORK/kernel/kernel.macho` | Complete prelinked fileset before payload diagnostic/POST modifications |
| `$WORK/payload/payload.img` | FAT payload with actual sealed kernel, ADT and selected sidecars |
| `$WORK/boot/boot.img`, `boot.json` | Android v0 outer image; header “kernel” is compressed firmware + DTB, ramdisk is the payload |
| `$WORK/package.manifest.json` | Output sizes/hashes, revisions, patches and runtime input summary; contains private installation information |
| `$WORK/logs/`, `$TREE/build/` | Full compiler, archive, reference, prelink and firmware evidence |
| `$UNIXNU_UEFI/Build/shengPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd` | 3 MiB board firmware volume |

Run the original guide's limited read-only checkers:

```bash
python3 "$GUIDE_ROOT/scripts/verify_manifest.py" --output-root "$WORK" --manifest "$WORK/package.manifest.json"
python3 "$GUIDE_ROOT/scripts/verify_boot_v0.py" "$WORK/boot/boot.img" --expected-dtbs 1
shasum -a 256 "$WORK/boot/boot.img" "$WORK/payload/payload.img" "$WORK/kernel/kernel.macho"
```

Exit 0 means these limited checks passed, not complete static acceptance or boot success. Review strict receipts, POST/HMAC, signatures, identity/root policy, binding/layout evidence and loader scope separately. See [VERIFICATION.md](VERIFICATION.md).

The one-DTB image was the original release output. The eight-DTB image was a separate, bounded entry experiment using the original writer, changing only the outer DTBs and required header length/ID. The user reported system entry with that variant; the root cause of the entry difference remains unproven.

## 10. Retain evidence and avoid unnecessary rebuilds

Record commits, environment, preparation diffs/receipts, effective status, patch order, full inner errors and output hashes. Find the first real compiler/linker error, not just a final secondary `FileNotFoundError`. A retained archive without Git metadata is not automatically a safe resumable checkout.

Historical persistent M4 corecrypto reuse was dependency/hash-validated (529/529 twice). That is not a validated whole-build object cache for run 41. Reuse verified downloads or properly qualified local objects; never reduce build time by disabling tests, adding fake providers or changing expected acceptance values.

Keep your seed, images, manifests and complete logs private. Public reports should contain redacted first errors, versions and necessary small diffs. No flashing, upstream PR or public system release is performed by this guide.
