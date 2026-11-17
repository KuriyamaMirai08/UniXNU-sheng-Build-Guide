# iPadOS 27.0.1（24A446）/ sheng 中文构建教程

本文按成功 run 41 的执行顺序整理。环境与命令来自实际记录；个人路径被替换成变量。**本次只复现了源码准备和指定预检查，没有在全新 Mac 上重新完整构建。** 历史 baseline、自己的安装输入与许可条件必须先满足，详见[复现缺口](REPRODUCIBILITY_GAPS.md)。

适用 Xiaomi Pad 6S Pro 12.4（sheng / SM8550），固定 profile `ipados-27.0.1-24A446`，defconfig `sheng_ipados27_defconfig`，输出目录名 `sheng_ipados27`。其他系统、容量、分区布局或编译器不继承这次验收结论。

以下命令在 **macOS 的 Bash** 执行，不是 Windows PowerShell。每节使用上一节定义的变量；在独立新目录执行，不对成功工程运行 `clean`、`reset --hard`或批量删除。

## 1. 环境准备

成功主机是 Apple arm64、macOS 26.7.2（25G332），Xcode 26.6（17F113），iPhoneOS SDK 26.5，Apple Clang 21.0.0（clang-2100.1.1.101）。Rust 固定 1.98.0；Python 实际为 3.15.2。完整表见[版本索引](SOURCES_AND_VERSIONS.md)。

推荐至少 100 GiB 可用空间，保留完整工程与归档宜预留 150 GiB 以上。成功 hosted 主机为 3 核 / 7 GiB，使用 `-j 3`；这不是峰值资源测量。选择 APFS 本地磁盘与支持符号链接的目录。

从官方渠道安装完整 Xcode 26.6；仅有 Command Line Tools 不足。设定自己实际安装的位置：

```bash
export DEVELOPER_DIR=/Applications/Xcode_26.6.app/Contents/Developer
test -d "$DEVELOPER_DIR"
xcodebuild -version
xcrun --sdk iphoneos --show-sdk-version
xcrun --sdk iphoneos clang --version
xcrun --sdk iphoneos --find clang | xargs shasum -a 256
```

clang SHA-256 应为 `d2e4bf622758eee1bf7267c060497fb2c41e098d37b0fca8be73898dc7e14eda`。Xcode 回答版本并不代表系统插件完整；若遇到历史 CoreSimulator 缺失 / exit 70，管理员在这台 Mac 完成 `sudo xcodebuild -runFirstLaunch`后再检查，见 [BUG-009](BUG_FIXES.md#bug-009)。

Homebrew 应先按其官方安装说明准备。历史工作流安装命令如下；**该命令本身不固定公式版本**：

```bash
export HOMEBREW_NO_AUTO_UPDATE=1
brew install dtc llvm lld cmake mtools ninja glslang shaderc spirv-tools bison pkgconf rustup blacktop/tap/ipsw
rustup toolchain install 1.98.0 --profile minimal --component rust-src
export RUSTUP_TOOLCHAIN=1.98.0
```

核对 `brew list --versions`与版本表，特别是 LLVM/LLD 23.1.4、dtc 1.8.1、cmake 4.4.5、ninja 1.13.2、mtools 4.0.50、bison 3.8.2。需要用自己的合法安装包、公式快照或已有环境准备匹配版本；本教程没有验证重建旧 Homebrew 快照的命令。不要把失配环境称为原环境。

## 2. 建立独立目录与日志位置

在教程仓库根目录执行：

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

Python 3.15.2 是成功记录值，`python3 --version`必须核对；这里没有让 `venv`替换 Python 本体。历史主控也清除所有 `CCACHE_`/`SCCACHE_`变量；本地有这些设置时应使用无这些变量的新 shell。

`PATH`让工具可见；XNU builder 仍使用 Xcode SDK/Apple Clang。不得把 `xcrun`指定的 Mach-O 编译器统一替换成 Homebrew Clang。不要打印完整环境或开启含 Secret 的 `set -x`。

## 3. 获取固定源码

成功设备修复在个人 fork，UniXNU 与 uefi-sheng 来自官方项目；官方设备仓库作为来源引用，不能只 clone 它的最新 `main`就声称包含本教程修复。

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

目录必须是相邻的 `device`、`UniXNU`、`uefi-sheng`；`device/board.toml`的 `[package] unixnu = "../UniXNU"`依赖此关系。feeds 在后面由 `unixnu fetch`按固定配置取得；不另取最新 XNU、SoC 或 corecrypto 替代。

**UEFI 此时不递归初始化。** 正式 firmware builder 会按板配置只拉四个直接 submodules，Mu_Basecore 来自固定 feed，Binaries/sheng 来自固件导入。详见 [BUG-008](BUG_FIXES.md#bug-008)。

## 4. 准备自己的输入并检查前提

在下载 corecrypto 前先确认[第三方许可证](../THIRD_PARTY_NOTICES.md)覆盖自己的用途。没有授权的源码/固件/系统文件不由本仓库提供。

自己的私有目录应在教程与源码目录之外。填写现有文件路径；以下内容是接口模板，不会生成或复制其他设备的输入：

```bash
export PRIVATE_INPUTS="$HOME/UniXNU-private-inputs"
export PRIVATE_DATA_SEED="$PRIVATE_INPUTS/data.dbr"
export UNIXNU_SHENG_BASELINE_NATIVE="$PRIVATE_INPUTS/baseline-native.macho"
export UNIXNU_SHENG_REGRESSION_SOURCE="$PRIVATE_INPUTS/baseline-kernel.py"
test -f "$UNIXNU_SHENG_BASELINE_NATIVE"
test -f "$UNIXNU_SHENG_REGRESSION_SOURCE"
```

baseline 两个文件必须是自己有权使用的历史证据，并匹配固定 contract。不能用新编译 native 替代旧比较证据，也不能从其他安装复制 Seed。可用短检查核对 baseline，不输出私人身份：

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

`UNIXNU_UNIQUE_CHIP_ID`应私下设为**自己设备**的非零 u64 十六进制值。历史 M4 文档来源是设备的 `/sys/devices/soc0/serial_number`，这里不连接设备或代填数值。它不是 Data UUID，也不是 seed 文件。

```bash
python3 - <<'PY'
import os, re
s = os.environ.get('UNIXNU_UNIQUE_CHIP_ID', '')
if not re.fullmatch(r'(?:0[xX])?[0-9a-fA-F]{1,16}', s) or not int(s, 16):
    raise SystemExit('Set your own nonzero hexadecimal u64 UNIXNU_UNIQUE_CHIP_ID privately')
print('Platform identity syntax accepted; value not printed')
PY
```

保留现有安装时必须有自己的 `data.dbr`，记录它的本地 hash，后面用 `--data-ramdisk`。首次生成用 `--init-data`并保留生成 Seed，二者互斥。**run 41 只验证保留 Seed；新 Seed/新身份路径的完整成功尚未复现。** 新 Data UUID 可能触发 strict source/shape contract，见[复现缺口第 3 节](REPRODUCIBILITY_GAPS.md#3-新-seed参数和存储布局)。

固定板参数已在 `board.toml`、`configs/sheng_ipados27_defconfig`及 OS/SoC profile 中。保留 run 41 的默认选中组件、prelink roots、原 kernel arguments；不要为了尺寸删 USB roots。`data_gib = 215`是本次板配置，userdata LBA 必须与自己的布局核对；本教程不执行 userdata 生成或安装。

## 5. 按成功顺序应用准备修改

成功设备提交已经包含设备补丁，不再 cherry-pick 每个历史修复。framework/submodule 的受控准备修改仍须执行；顺序如下，且每个只在全新副本执行一次：

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

各步作用：

| 步骤 | 保留的效果 / 如何判断 |
| --- | --- |
| `prepare-package-ci` | 检查固定源码；修 Ath12k commit/non-cone fetch 与 XNU 生成 headers 的 bootstrap 条件 |
| `preserve.apply` | 保存失败 patch/prelink 现场，安装只接受特定缺 archive 的 bootstrap guard；生成 `preservation-transforms.json` |
| reference patch | 给原 builder 加真实 archive 接口；`apply --check`先成功 |
| author audit preparation | **在 early tests 前安装 verifier**，保护实际缺席的 optional provider，保持 RELEASE assertion ABI；生成 `optional-source-transforms.json` |
| framework tests | 原 4 项保持启用；publication 6 项通过，包含清除 Python 环境后 helper 仍可导入 |

准备脚本严格核对来源和 marker。第二次重复执行可能因“已经存在”拒绝；这不是要求清空历史工程再运行。准备 receipt 与 Git diff 要保留，任何失配都应先查版本和未登记修改。

## 6. fetch、配置、tree 与预链接预检查

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

`status`应显示 `configuration = sheng_ipados27_defconfig`、预期 OS/profile、实际模块 revision 与 **95 项** patch plan。所有固定 feeds 与子模块见版本 JSON。`--check`只列配置/补丁，**不创建 tree**；必须保留独立 `tree`命令，见 [BUG-023](BUG_FIXES.md#bug-023)。

确认 tree 尚无 `.o`、`.a`、`.cpo`与 `kernel.macho`，run 41 的 `precompile-objects.json`为空；baseline 证据不在编译对象目录。然后执行：

```bash
cd "$TREE/kits/XnuPrelink"
python3 -m unittest test_fileset_emit test_fileset_layout test_fileset_match test_fileset_shape
cd "$UNIXNU_DEVICE"
python3 scripts/check-sheng-optional-providers.py --tree "$TREE" --output "$BUILD_ROOT/evidence/optional-link"
```

原引擎 36 项检查通过。optional link 检查运行真实 guarded consumers，验证已启用但缺 provider 必须失败；测试 peer 只用于测试，不能进入最终 native/reference。

不要手动乱序 `git apply`全部 XNU patch。resolver 按 ARM64/SoC/OS/device 的实际合并顺序应用；末尾第 93/94/95 项分别是 `driverkit-platform-function.patch`、`sheng-image4-normal-runtime.patch`、`sheng-image4-size.patch`。最后 size patch 只加六个函数的 minsize。完整顺序与 hash 可逐项对照 JSON。

## 7. 在 archive 编译之前取齐输入

KernelCache 必须先取得，真实 Image4 normal PAL archive 需要它：

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

这些是成功记录中的原命令，不是新下载系统。IPSW 由固定 profile 的官方 URL 按需读取成员；检查 27.0.1 / 24A446 / iPad17,3 / j820ap 与 kernelcache hash。touch/keyboard、Wi-Fi、蓝牙、stock ROM 与 UEFI import 均有其对应 source/receipt 检查。固件尺寸、hash 和 UEFIExtract pin 见版本索引。

`--delete-archive`只在官方脚本完成校验与提取后删除它自己的下载副本；不对用户原 ROM 备份或完结归档操作。已验证提取物及来源 receipt 保存后，固件 downloader 再次运行会核对并复用；不是只凭文件存在跳过。

内核 archives 中的 DTS/GPU generators 仍按板配置运行，firmware preflight 也仍运行。这些是正式依赖/来源检查，不是应从 release 中删掉的“重复步骤”。outer `sheng.dtb`与内层 Apple ADT 是不同对象，不能互换。

## 8. 正式 release

保留自己的现有安装 Seed：

```bash
test -f "$PRIVATE_DATA_SEED"
cd "$UNIXNU_DEVICE"
bash scripts/package.sh "${common[@]}" --no-deps --data-ramdisk "$PRIVATE_DATA_SEED" 2>&1 | tee "$BUILD_ROOT/evidence/release.log"
```

首次 Seed 的真实接口为：

```bash
# FIRST seed generation only; not the run 41 tested path.
cd "$UNIXNU_DEVICE"
bash scripts/package.sh "${common[@]}" --no-deps --init-data 2>&1 | tee "$BUILD_ROOT/evidence/first-install-release.log"
```

**两段只选择一段**。`--init-data`不刷设备，但创建新的安装状态，不能用于修复已有安装的 cache miss。新 Seed 生成后，即使后续构建失败也应私下保存；下次通过 `--data-ramdisk`复用。新增 Seed/自己的输入仍可能被固定 strict contract 拒绝，这里不保证首次路径完成。

不要手动把 `build kernel`提前到 Seed 准备之前。成功 `release`内部依次：

1. preflight、defconfig、ordered tree；`runtime.prepare`读取 Seed UUID并将其绑定生成配置，构建 GPU/audio/Wi-Fi/Bluetooth/AppSync 与 trust inputs。
2. XNU bootstrap 生成 headers 与对象。只有符合精确条件的缺 board archive 首轮链接可以继续，之后真实 archives 和最终 native 链接必须成功。
3. corecrypto 普通/namespace、ArmDTPlatform、ArmCpu、storage、RamBlock、GPU、display、Image4 normal PAL 等真实 archives；同一轮生成 RELEASE-LTO comparison。
4. 真正 DEVELOPMENT native 链接、unchanged XnuPrelink 引擎与 strict wrapper 预链接，检查 17 项准备源码、21 槽绑定、历史 ABI/形状/重定位与零 missing/stub。
5. 构建 UniXNU/DarwinBoot package、payload FAT、ADT、诊断修补与 POST 密封，再构建 DEBUG CLANGPDB UEFI FD。
6. BootShim + FD 压缩并追加 outer DTB，以官方 writer 生成 Android v0 boot.img，原 pipeline 校验 hash、命令行与容量，写 manifest。

run 41 release 阶段约 45 分 54 秒，主控预处理另需数分钟，完整云端归档上传还需时间。普通 hosted runner不复用 XNU 对象。下载缓存和归档方式见 [Actions 教程](GITHUB_ACTIONS.md)，warm cache 的整轮提速没有实测。

## 9. 产物与成功判断

| 路径 | 用途 / 成功信号 |
| --- | --- |
| `$WORK/kernel/kernel.macho` | 未经 payload 诊断/POST 密封修改的 complete fileset |
| `$WORK/payload/payload.img` | FAT payload，含最终 kernel、ADT、trust/runtime sidecars 与 boot entry |
| `$WORK/boot/boot.img`、`boot.json` | 外层 Android v0，gzip(BootShim + UEFI FD) + DTB，ramdisk 是 payload |
| `$WORK/package.manifest.json` | 三个产物 size/hash、pins、patches、runtime输入摘要；**包含私人安装信息，不能原样公开** |
| `$WORK/logs/`、`$TREE/build/` | 完整编译、archive、reference、prelink和 firmware证据 |
| `$UNIXNU_UEFI/Build/shengPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd` | 固定板的 3 MiB UEFI FD |

命令退出 0只是构建通过。先使用本教程只读工具：

```bash
python3 "$GUIDE_ROOT/scripts/verify_manifest.py" --output-root "$WORK" --manifest "$WORK/package.manifest.json"
python3 "$GUIDE_ROOT/scripts/verify_boot_v0.py" "$WORK/boot/boot.img" --expected-dtbs 1
shasum -a 256 "$WORK/boot/boot.img" "$WORK/payload/payload.img" "$WORK/kernel/kernel.macho"
```

工具只完成有限检查，完整范围见 [VERIFICATION.md](VERIFICATION.md)。必须另外读 strict prelink receipts、原签名/POST/绑定验收，不能把本教程的 outer checker 当作完整静态合格证书。

单 DTB 是本节原成功流程的产物。八 DTB 是后续独立入口实验，采用官方 writer，仅换外层 DTB和必要 header ID/长度。其历史操作与边界见验收文档；没有自动把它作为所有用户推荐镜像。

## 10. 保存记录，避免重复长构建

保存精确提交、环境、准备 diff/receipt、source status、patch order、完整内层错误日志和产物 hash。失败时先查第一条实质 compiler/linker error，别仅看末尾 `FileNotFoundError`。不要把历史 `.git`缺失的归档直接视为可续跑工程。

本地持久目录允许依赖校验后的对象复用；历史 M4 corecrypto 529/529 复用确曾验证，但当前 run 41 hosted 路径是干净构建，不能把该经验当作已经可用的整轮对象缓存。绝不通过删检查、假 provider 或修改验收值压缩耗时。

自己的 Seed、镜像、manifest 与完整日志保存在私有位置。公开 issue 只提供脱敏首错、阶段、版本与必要小段 diff。不要上传 IPSW、固件、Data seed 或未授权第三方材料。
