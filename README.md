# UniXNU-sheng / iPadOS 27 构建与排错指南

面向 Xiaomi Pad 6S Pro 12.4（`sheng` / SM8550）的社区经验整理，基于一次实际完成的 iPadOS 27.0.1（24A446）构建、保留的失败日志、Git 修改和静态验收结果。本文档不是 UniXNU 官方发布，也不提供可直接刷入的系统镜像。

**目前可以复查成功版本、按原顺序准备源码并理解每项修复；还不能承诺全新用户通过公开文件一键复现。** 原成功流程依赖历史预链接证据与个人安装输入；其中 corecrypto 的许可证也限制使用目的与再分发。先读[复现条件与缺口](docs/REPRODUCIBILITY_GAPS.md)和[第三方声明](THIRD_PARTY_NOTICES.md)，再开始下载或构建。

## 已确认的结果

| 层次 | 结果与边界 |
| --- | --- |
| 完整构建 | 个人 fork 的 [run 41 / 43805045606](https://github.com/KuriyamaMirai08/UniXNU-sheng/actions/runs/43805045606) 成功；设备提交 `a9f0500af098f8aee87c86a571638daee92caf26` |
| 静态验收 | 原流程单 DTB 镜像通过源码、绑定、布局、完整性、信任材料、镜像结构与实际 loader parser 的限定检查 |
| 实机观察 | 用户报告另行生成的**八 DTB 变体**进入系统；这不等于单 DTB 版已实机通过 |
| 运行问题 | 动画卡顿；2.4 GHz Wi-Fi 正常，5 GHz 网络可见但连接失败；原因仍未确认 |
| 本教程复核 | 在独立副本复现准备修改，结果与 run 41 一致；6 项 reference publication、5 项下载缓存、36 项原预链接引擎检查通过；本次未重新全量编译 |

最终构建使用固定的 UniXNU framework 和 UEFI。修复存于[个人 fork](https://github.com/KuriyamaMirai08/UniXNU-sheng)，不能据此声称[官方设备仓库](https://github.com/UniXNU/UniXNU-sheng)已合入这些修复。

## 快速开始

1. 阅读[复现条件](docs/REPRODUCIBILITY_GAPS.md)，确认工具链、合法使用的依赖和自己的安装输入。
2. 按[中文完整教程](docs/BUILD_CN.md)或[English build guide](docs/BUILD_EN.md)建立独立目录，固定源码，先运行准备与预检查。
3. 如使用云端构建，阅读[GitHub Actions 教程](docs/GITHUB_ACTIONS.md)。历史工作流不能直接迁移个人 Secret 或旧 artifact 到另一个 fork。
4. 按[Bug 修复目录](docs/BUG_FIXES.md)处理与自己版本对应的问题。成功提交已经包含的修复不要再重复应用。
5. 完成后按[验收指南](docs/VERIFICATION.md)核对产物，把“命令成功”“静态通过”“设备进入系统”分别记录。

这里没有刷机命令或自动设备操作。首次生成 Data seed 与写入设备是两件不同的事。

## 文档导航

| 文件 | 内容 |
| --- | --- |
| [BUILD_CN.md](docs/BUILD_CN.md) | 中文教程：环境、源码、输入、补丁、构建、产物 |
| [BUILD_EN.md](docs/BUILD_EN.md) | 对应英文教程，使用相同版本与命令顺序 |
| [BUG_FIXES.md](docs/BUG_FIXES.md) | 24 项已确认的历史问题，区分有效修复、失败尝试及未解决问题 |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | 按关键错误文本快速定位 |
| [GITHUB_ACTIONS.md](docs/GITHUB_ACTIONS.md) | 成功运行入口、迁移门槛、缓存与日志保存 |
| [VERIFICATION.md](docs/VERIFICATION.md) | boot.img 结构、产物哈希、预链接、签名与验证范围 |
| [KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md) | 性能、Wi-Fi、安装软件及其他限制 |
| [SOURCES_AND_VERSIONS.md](docs/SOURCES_AND_VERSIONS.md) | 完整版本索引、工具链与依赖来源 |
| [EVIDENCE.md](docs/EVIDENCE.md) | 证据编号、失败运行、采纳与推翻的方案 |
| [REPRODUCIBILITY_GAPS.md](docs/REPRODUCIBILITY_GAPS.md) | 公开资料目前无法补齐的输入与尚未验证的路径 |
| [AUTHORING_VALIDATION.md](docs/AUTHORING_VALIDATION.md) | 本教程自身的验证结果与限制 |
| [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) | 作者归属、许可证与不能附带的内容 |

`evidence/` 仅包含脱敏的版本、顺序、哈希和验收事实；没有第三方源码、编译对象、私有日志或镜像。`scripts/` 是本教程原创的只读产物检查工具，检查范围见验收文档。

## 成功基线

| 项目 | 固定值 |
| --- | --- |
| 系统 / 配置 | `ipados-27.0.1-24A446` / `sheng_ipados27` |
| 设备 fork | `a9f0500af098f8aee87c86a571638daee92caf26` |
| UniXNU | `97437dcf7389484a0eeaa8067725ce743aff18ef` |
| uefi-sheng | `66421cb7bb5694843aec8de1ca3d1de4c20cca38` |
| XnuPrelink | `8f4f3866545727e2dc3d2c8cb60f8a87a9539c12` |
| 内核 / comparison / UEFI | DEVELOPMENT / RELEASE-LTO / DEBUG CLANGPDB |
| 原流程 boot.img | 185,733,120 字节；SHA-256 `55f9099fb3a56a68d929bcdc6780755799d008de2910034d2ad37a42d4740b43` |
| 八 DTB 变体 | 189,480,960 字节；SHA-256 `fbf22394963b8ebcc3530c5eefa94da3249c0c35326dcfd9c8342f844c2932af` |

这些哈希标识历史文件，不是其他用户自己的设备输入构建出的镜像必须达到的哈希。修改身份、Data UUID、参数或工具链后，需要重新验收自己的产物。

文档整理日期：2026-11-17。原创文档与检查脚本采用 [MIT](LICENSE)；第三方材料的权利仍由各自许可证决定。本仓库未发布系统或镜像，未完成一套去除历史输入依赖的新构建系统。
