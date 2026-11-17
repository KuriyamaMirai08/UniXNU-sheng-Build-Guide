# 来源、作者与许可证

本仓库提供原创教程、故障分析、少量命令与原创检查脚本。没有附带 Apple 系统文件、修改后的完整 XNU、第三方实现、镜像、专有固件或设备安装状态。本文的 MIT 许可证只适用于本仓库原创内容，不为链接指向的材料提供额外许可。

## UniXNU 与设备适配

感谢 [UniXNU contributors](https://github.com/UniXNU)、[UniXNU 主项目](https://github.com/UniXNU/UniXNU)、[官方 UniXNU-sheng](https://github.com/UniXNU/UniXNU-sheng)及所有设备、SoC 和驱动作者。最终修复证据来自[栗山未来 / KuriyamaMirai08 的设备 fork](https://github.com/KuriyamaMirai08/UniXNU-sheng)。这是社区整理，不代表上述作者认可本教程或提供官方系统版本。

固定 framework 的 [LICENSE](https://github.com/UniXNU/UniXNU/blob/97437dcf7389484a0eeaa8067725ce743aff18ef/LICENSE)、固定设备 fork 的 [LICENSE](https://github.com/KuriyamaMirai08/UniXNU-sheng/blob/a9f0500af098f8aee87c86a571638daee92caf26/LICENSE)及固定 [XnuPrelink LICENSE](https://github.com/UniXNU/XnuPrelink/blob/8f4f3866545727e2dc3d2c8cb60f8a87a9539c12/LICENSE)采用 **BSD-2-Clause-Patent**，版权声明为 `Copyright (c) 2026, UniXNU contributors. All rights reserved.`。完整许可保留于 [LICENSES/BSD-2-Clause-Patent.txt](LICENSES/BSD-2-Clause-Patent.txt)，以便保留必要声明。

构建命令调用的代码仍来自各项目。引用短错误消息、文件路径、提交与修复思路，不等于把整份被修改源码纳入本仓库许可。

## UEFI、Mu 与镜像工具

[uefi-sheng 的固定 LICENSE](https://github.com/UniXNU/uefi-sheng/blob/66421cb7bb5694843aec8de1ca3d1de4c20cca38/LICENSE)是两条款 BSD 声明集合。其声明列出 Andrei Warkentin、Apple、ARM、Bingxing Wang、DuoWoA、Intel、Linaro、Microsoft、Samuel Tulach、Android Open Source Project、Linux Foundation、Travis Geiselbrecht 等作者。Microsoft Mu、Project-Silicium、EDK II、OpenSSL 的子项目须分别依据自身及文件级许可证使用。

UEFI checkout 中的 `Resources/Scripts/mkbootimg.py` 标注 Android Open Source Project 2015 版权和 Apache-2.0。本教程只调用该工具，没有复制其实现。原创镜像检查器按公开 Android header 格式独立编写，不替代该工具或设备启动验证。

## Apple XNU 与系统输入

固定 [XNU APPLE_LICENSE](https://github.com/apple-oss-distributions/xnu/blob/ac9718fb1af618d5ce8678d0dc6e8a58f252216f/APPLE_LICENSE)为 **APSL 2.0**。XNU 内部还有文件级第三方许可，不能把整个 XNU 或所有驱动当作 BSD。其他 Apple OSS 仓库同样要查自身声明。

IPSW、提取的 kernelcache、系统镜像、trust cache 等是构建输入。本教程提供官方来源与校验方法，不分发这些文件，也不授予 Apple 系统软件的使用或再分发权。

## corecrypto 的实质限制

历史构建使用 [ONLYA/corecrypto-2023](https://github.com/ONLYA/corecrypto-2023) 的固定快照。该仓库是第三方来源，未通过 Apple 原始下载包认证。本次读取的文件名是 **`License.txt`**，不是 `LICENSE`。

[固定 License.txt](https://github.com/ONLYA/corecrypto-2023/blob/11fba65b12d8830630e248dfa8344caf8b065f26/License.txt)标题为 **CORECRYPTO INTERNAL USE LICENSE AGREEMENT**。其条文把许可限制为下载后 90 天、组织内部、自己拥有或控制的设备、仅验证安全特性与正确运行，明确禁止直接或间接再分发；其他目的或环境需要 Apple 事先书面许可。

**第三方仓库公开可见，并不授权普通系统移植、社区发布或镜像分发。** 本教程如实记录这个依赖，不提供该源码、对象、归档或可规避限制的替代实现。在执行含此依赖的步骤前，使用者需要确认自己具有覆盖该用途的许可；本次整理没有证明普通社区用途满足该许可。

## Linux、FreeBSD、Wi-Fi 与图形依赖

[Ath12kWifi](https://github.com/UniXNU/Ath12kWifi) 的固定顶层没有独立 `LICENSE` 文件；README 描述了实际 Linux、FreeBSD 与 wpa_supplicant 来源。不能由其他 UniXNU 仓库的 BSD 声明推导所有来源均是 BSD。

Linux 材料须查 GPL-2.0 与文件 SPDX；FreeBSD、wpa_supplicant、Mesa、metal2vulkan、SoftFloat 和 QcaBluetooth 等按各自选中代码与文件级许可处理。本仓库只记录 pins 和调用关系，不附带这些来源。图形参考仓库与实际 Mesa 编译仓库的区别见[版本索引](docs/SOURCES_AND_VERSIONS.md)。

## 小米、高通固件与私人安装输入

小米 stock ROM、高通设备固件和从 UEFI 中提取的模块不随本仓库发布。用户应从自己有权使用的来源获取，按固定文件大小与哈希核对。缓存复用不改变许可，也不意味着缓存内容可以公开分享。

个人 unique-chip-id、Data seed、Data UUID、输入加密密钥、访问令牌、签名私钥、设备日志及含这些信息的 manifest 均不进入公开目录。历史产物的文件哈希仅用于标识已验收文件；没有公开安装身份与 Seed 的哈希。

许可证与主要链接查验日期：2026-11-17。网络位置可能变更，许可结论以固定提交的原文为依据。
