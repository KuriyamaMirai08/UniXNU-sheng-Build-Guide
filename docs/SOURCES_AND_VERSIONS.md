# 源码、依赖与工具链版本

本页记录成功 run 41 实际使用的版本。完整 Git 子模块与 feed 清单在 [source-pins.json](../evidence/source-pins.json)；补丁顺序与文件哈希在 [patch-order.json](../evidence/patch-order.json)。不要用当前 `main`、最新 tag 或旧报告中的 pins 替换这些值，然后仍沿用原验收结论。

## 1. 三个顶层仓库

| 名称 / 本教程目录名 | 仓库 | 成功构建提交 |
| --- | --- | --- |
| 设备适配 / `device` | [KuriyamaMirai08/UniXNU-sheng](https://github.com/KuriyamaMirai08/UniXNU-sheng) | `a9f0500af098f8aee87c86a571638daee92caf26` |
| 主框架 / `UniXNU` | [UniXNU/UniXNU](https://github.com/UniXNU/UniXNU) | `97437dcf7389484a0eeaa8067725ce743aff18ef` |
| 固件 / `uefi-sheng` | [UniXNU/uefi-sheng](https://github.com/UniXNU/uefi-sheng) | `66421cb7bb5694843aec8de1ca3d1de4c20cca38` |

设备的[官方仓库](https://github.com/UniXNU/UniXNU-sheng)仍应署名并引用。最终修复来自 fork，不能把官方共同祖先 `82d9e23ade933aa9d6c9ea2f4f40045e2d985479` 当作成功修复版本或作者发布的二进制。

归档中的后续 HEAD `feda913f92554e18b75e4992e17fe5fb040006da`记录验收与交付结果；**run 41 的构建 SHA 是 `a9f0500…`**。更早的 run 43731472664 与它的产物不是本教程最终基线。

## 2. resolver 获取的固定 feeds

| 来源 | 版本或用途 | Commit |
| --- | --- | --- |
| [UniXNU-sm8550-common](https://github.com/UniXNU/UniXNU-sm8550-common) | SM8550 SoC、DTS 与补丁 | `97665e28578483082b674e8375a8fa65f4cf49cf` |
| [Apple xnu](https://github.com/apple-oss-distributions/xnu) | `xnu-12377.121.6` | `ac9718fb1af618d5ce8678d0dc6e8a58f252216f` |
| [libplatform](https://github.com/apple-oss-distributions/libplatform) | `375.120.2` | `b7ed7cf5cf7dd12b98672435db2225a860f199d8` |
| [libdispatch](https://github.com/apple-oss-distributions/libdispatch) | `1542.100.32` | `701f4d1a24ae9c6863901bbbb22624b7d1b87321` |
| [AvailabilityVersions](https://github.com/apple-oss-distributions/AvailabilityVersions) | `157.2` | `149b1777f3e8c2133042d8e188f72e3adf6a7110` |
| [mu_basecore](https://github.com/microsoft/mu_basecore) | EDK II 核心 | `cfb93724a06ff86ff5ba971413368a7809ee42a5` |
| [libpthread](https://github.com/apple-oss-distributions/libpthread) | `539.100.4` | `1f4f5265b319111142f1bf3a27d4484ef5a98314` |
| [corecrypto-2023 第三方快照](https://github.com/ONLYA/corecrypto-2023) | 有特殊许可限制，见第三方声明 | `11fba65b12d8830630e248dfa8344caf8b065f26` |
| [IOStorageFamily](https://github.com/apple-oss-distributions/IOStorageFamily) | `337.100.1` | `7edb88fbae296fb7c8ce2f64e115e116e566d51c` |
| [IOHIDFamily](https://github.com/apple-oss-distributions/IOHIDFamily) | `2238.120.5` | `e31e90a24c27ad6cbe981650d12a1a4124065b03` |

这些 Apple OSS 版本提供源接口，不能仅凭来源一致就认为它们与去符号的 24A446 二进制 ABI 相同；历史项目另外做了类布局、RPC、PAC 与符号绑定验收。

固定 OS profile 使用 xnu-12377 加 27 兼容补丁。它并不声称使用了已经公开的 Darwin 26 完整 XNU 源码。profile 中 Darwin 字段为 `25.5.0`，编译 deployment target 为 `27.0`，IPSW 产品版本为 `27.0.1`；三者不能混写。

## 3. 关键子模块

| 项目 | 路径所属仓库 | Commit |
| --- | --- | --- |
| XnuPrelink | `UniXNU/kits/XnuPrelink` | `8f4f3866545727e2dc3d2c8cb60f8a87a9539c12` |
| DarwinBoot | `UniXNU/drivers/DarwinBoot` | `5243c68ec332a227fe3680cd5da6d5a0e127035c` |
| ArmDTPlatform | `UniXNU/drivers/ArmDTPlatform` | `e8bd8d5de395c6cbc00d762c1bef57dbd15a448d` |
| Adreno740 | `UniXNU/drivers/Adreno740` | `4a3921a2b94632002cd31a7af9a82cf809806bec` |
| AdrenoMetal | `UniXNU/drivers/AdrenoMetal` | `20be9f966a0b947238f80dec22a91bf6c9dfc0a0` |
| Ath12kWifi | `device/drivers/Ath12kWifi` | `48e23bf15fc21bbd30d5583b42b9c09ad65537db` |
| QcaBluetooth | `device/drivers/QcaBluetooth` | `b2fbab61615e0811c076b6f17df5b37c651f339d` |
| QcomDwc3 | `device/drivers/QcomDwc3` | `e4efe95c903a737e0f5955e5b50a8fb4d2a7d718` |
| ShengUfs | `device/drivers/ShengUfs` | `b11de87c234cf4b8f80a8160fb15e6f37a8e5d0c` |

其余 Sheng 输入与预检组件、RamBlock、ArmCpu、GPU kits、UEFI direct gitlinks 的完整 URL 和 SHA 在 JSON 中。初始化子模块应检出父仓库记录的 gitlink，不执行 `submodule update --remote`。

UEFI 只初始化本板要求的四个直接路径：`Common/Mu`、`Common/Mu_OEM_Sample`、`Silicium-ACPI`、`Silicon/Silicium/OpensslPkg/Library/OpensslLib/openssl`。其中 Mu_Basecore 来自上面的 feed，`Binaries/sheng`由固件导入步骤生成。没有必要再递归拉取另一份 Mu_Basecore、设备二进制库或 OpenSSL 的测试/模糊测试依赖。

## 4. 驱动下载输入与 GPU 来源区别

| 输入 | 实际固定值 | 权威位置 |
| --- | --- | --- |
| Ath12k Linux | v7.0.14 / `458c6079fc1d41d564c37679c8ace02cd83ee817` | 固定 Ath12kWifi 的 `tools/source-lock.json` |
| Ath12k FreeBSD | releng/15.1 / `95719d8a895bf8170851e9844d9b4092b1d2b6fe` | 同上 |
| wpa_supplicant | 2.12；archive SHA-256 `08e23937e16d0155e55cab2b51f51fbe10d80a1aa91c4e15442645059b737ef6` | 同上 |
| 实际 Mesa / Turnip 编译 | `85fda3b36405bcaea8bffc64aa4f2651dc90770d` | `UniXNU/scripts/data/adreno-compiler-inputs.json` |
| metal2vulkan | development / `963f0e64f103d2e682cd0cc454a8fe50f52c8cbb` | `UniXNU/scripts/data/gpu-metal-vulkan-inputs.json` 的 translator |
| 图形参考 Mesa | `c823a83e8f373a5c36c2b9ed1d7dc98a4f3360ee` | 同文件的 mesa；**不是实际 Turnip 编译 pin** |
| SoftFloat 参考 | 3e / `a0c6494cdc11865811dec815d5c0049fba9d82a8` | `adreno-compiler-inputs.json` |
| 板级 Linux GPU/IOMMU 参考 | `42f3b40c702abbc37c3a04c95af008cd283aeaf3` | `gpu-metal-vulkan-inputs.json`；不构建整套 Linux |
| 蓝牙固件来源清单 | ianchb/sheng-firmware / `053da477a5c338ac28d7c1c869e8c3ff7ca24d11` | 设备固件准备脚本及生成 receipt |

Mesa 的实际编译清单含 **17 个有序补丁**，与 XNU/resolver 的 **95 个补丁**是两份不同清单。保留 Mesa patch identity 检查。不要加 `--latest` 把 metal2vulkan 固定版本更新为远端分支头。

## 5. 系统与固件输入

| 输入 | 固定值 / 校验 |
| --- | --- |
| Apple IPSW | iPadOS `27.0.1` / `24A446`，产品 `iPad17,3`，device class `j820ap`；官方 URL 在固定 `UniXNU/profiles/os/ipados-27.0.1-24A446/profile.toml` |
| kernelcache.decompressed | SHA-256 `38e6d9fa5f789b8228f4617ef4c6d2a3fd8ab564abdc9b62920f1db53fc1780a` |
| 小米 stock archive | `OS3.0.305.0.WNXMIXM`，7,609,308,281 字节；官方 URL 在固定 `device/board.toml` 的 `[firmware.image]` |
| stock archive SHA-256 | `c6259e1c8dd89b5b16d086cbdda5d21083c2ca445dd4cde4c8917139f490c7ed` |
| UEFIExtract | LongSoft A76 universal mac；SHA-256 `f3c5ca9402df3c14b28242dcd04b527791a12c1c0bf3c1cbbb3d1a0445168ec5`；由 `import-sheng-uefi.py`校验 |
| 历史 baseline native | SHA-256 `2d1071d451f27bcd330a688a2579bd789b9c5795b1d5e670239850629ec665d9`；仅证据输入，不作编译对象缓存 |
| 历史 regression kernel.py | SHA-256 `d60bc0abf45b1ce05ae74932ba26092e1c6c5a113a2b8ced7741178b6d3d2107` |

这里只记录 hash，不随仓库提供系统、固件或 native 二进制。baseline 的获取限制见[复现缺口](REPRODUCIBILITY_GAPS.md)。

## 6. 成功运行的工具链

| 类别 | 观察到的版本 |
| --- | --- |
| 主机 | macOS 26.7.2，build 25G332；Apple arm64 |
| Hosted runner | `macos-26`，image `20261102.0473.1` |
| Xcode | 26.6，build 17F113 |
| Apple Clang | 21.0.0，`clang-2100.1.1.101` |
| 编译器 SHA-256 | `d2e4bf622758eee1bf7267c060497fb2c41e098d37b0fca8be73898dc7e14eda` |
| iPhoneOS SDK / target | SDK 26.5 / `arm64e-apple-ios27.0` |
| Homebrew LLVM / LLD | 23.1.4 / 23.1.4 |
| Rust | 1.98.0，安装 `rust-src` |
| Python / venv | 3.15.2；cryptography 50.0.2、cffi 2.1.1、pycparser 3.12 |
| dtc / cmake / ninja | 1.8.1 / 4.4.5 / 1.13.2 |
| mtools / bison / pkgconf | 4.0.50 / 3.8.2 / 3.0.10 |
| glslang / shaderc / spirv-tools | 16.6.0 / 2026.4 / 1.4.363.0 |
| ipsw | 3.1.749 |
| 资源 | 3 核，7 GiB RAM，`-j 3`；开始 fetch 前约 94.36 GiB 空闲 |

这些数字来自 run 41 的环境日志、编译命令和 Actions 工具安装记录，不是目前 Homebrew 自动安装结果的保证。`HOMEBREW_NO_AUTO_UPDATE=1`只禁自动更新，不锁公式、bottle 或预装 runner。

推荐同架构本地 Mac，预留 **至少 100 GiB 可用空间**，保存完整归档时宜有 150 GiB 以上；这是整理后的空间建议，不是测得的峰值或最低要求。215 GiB 的 Data 逻辑容量也不等于本机要完整分配 215 GiB。成功脚本的 12 GiB 提前拒绝阈值不是完整构建所需空间。

构建 XNU 使用 Xcode Apple Clang；LLVM/LLD 提供 EDK、归档和检查工具。先查 `xcrun --sdk iphoneos --find clang`及 hash；不要为了找到 `lld-link`而把所有 Mach-O 编译改为 Homebrew Clang。
