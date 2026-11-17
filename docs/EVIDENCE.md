# 证据索引与历史方案判定

本教程优先使用最后成功构建的工程、命令、源码准备结果和实际产物，其次用历史日志解释失败。没有把旧报告的“待验证”或“已尝试”自动升级为“最终成功”。

原始完结归档在本机保存，名称为 `UniXNU-sheng-20261116-完结归档`。本公开目录只保留脱敏元数据，完整日志与镜像均不附带。证据标签用于让每项结论能够追溯，并不声称所有私人证据都有公开下载。

## 证据标签

| 标签 | 实际来源 | 用途与公开范围 |
| --- | --- | --- |
| E01 | 完结入口 `00-结项与后续入口.md`、`ARCHIVE-COMPLETE.json`、Git snapshot 与归档 SHA 清单 | 确认真正最终成功版本及本地归档完整性；仅脱敏事实公开 |
| E02 | `run38-recovery/run37-lto-build.log`、`run38-lto-build.log`、恢复记录与文档失败日志 | run 37/38 的真实内层 compiler/linker 首错，排除 secondary exception |
| E03 | [成功设备 SHA](https://github.com/KuriyamaMirai08/UniXNU-sheng/tree/a9f0500af098f8aee87c86a571638daee92caf26)及固定 framework/UEFI Git，实际准备 diff 和源码 receipt | 确认最终脚本、配置与补丁，而非失败工作树 |
| E04 | run 39 保留的 `mach.release…`、`native-archive-diagnostics.json`和 nm 原输出、修复记录 | 四个 private N_SECT 真实存在，错误在检查器 |
| E05 | `run40-fix/run40-original-error.log`、修复 helper 安装与隔离 subprocess 回归 | ModuleNotFoundError 发生在 early framework tests |
| E06 | run 41 完整 Actions 日志、`evidence/environment.log`、`toolchain.json`、`stages.json`、`source-status.log`、`release.log`、各 compile-command 与 inner logs | 固定版本、34 主控阶段、95 patch plan、实际 archive/reference/native 构建 |
| E07 | `static-01/RESULT.json`、`structure/RESULT.json`、strict prelink receipt、签名与 HMAC 检查、实际 payload 成员 | 17 准备源码、21 槽、49 fileset 成员、布局、产物、安装输入与信任边界 |
| E08 | `loader-01`、`loader-02/RESULT.json`、实际 DarwinBoot PE/map，3 个损坏负例 | 实际 parser 指令模拟；终止于 ADT 分配之前；早期 map 格式错误被保留 |
| E09 | `stock-dtb/manifest.json`、`device-test-20261116`及用户的屏幕/使用反馈 | 八 DTB 变体的 byte identity 和用户报告进系统，性能/Wi-Fi 未解决 |
| E10 | 成功 SHA 下历史 reports：`m4-xnu-corecrypto.md`、`m4-manual-release.md`、`package29-prelink.md`、`package30-prebuild-audit.md`、`m4-prelink.md`等 | 更早环境/header/cache/DATA/weak import 历史；不是 run 41 的新结果 |
| E11 | [文档成功 run 43794301757](https://github.com/KuriyamaMirai08/UniXNU-sheng/actions/runs/43794301757)、固定 `porting.toml`和记录工具 | 结构与变更 ownership 通过，不能当成 boot 发布 |
| E12 | 教程独立副本的 preparation receipts、6 publication/5 cache/36 engine checks与原创 checker 正负例 | 本次本地复核；没有新 Apple 全量编译或设备操作 |
| E13 | 2026-11-17 实际读取的固定 LICENSE、APPLE_LICENSE、corecrypto `License.txt`与 README | 许可与作者署名；本地保存原文研究副本，公开必要声明和链接 |

## 四份公开机器可读记录

- [source-pins.json](../evidence/source-pins.json)：三个顶层仓库、全部 direct gitlinks、10 个 feeds 的实际 revision。
- [patch-order.json](../evidence/patch-order.json)：成功 95 项 patch plan，带路径、size、SHA-256。
- [stages.json](../evidence/stages.json)：34 项主控阶段与真实 argv/cwd/耗时，私人路径替换成变量；不包含所有内部子步骤。
- [baseline.json](../evidence/baseline.json)：环境、三个产物、嵌入内核、八 DTB 变体与验证边界。

resolver status 中某些模块的 `pin`与实际 `revision`不同。最终采用真实 checkout revision 及父仓库 gitlink，而非只抄 `pin`字段。所有差异保留在原 status 证据；没有用最新远端分支推测当时版本。

## 最后几轮构建

| Run | 构建提交 | 结果 / 首错 |
| --- | --- | --- |
| 37 / [43747167997](https://github.com/KuriyamaMirai08/UniXNU-sheng/actions/runs/43747167997) | `e404b6c768cbd728a746b620cf838ca790168879` | 真实 DEVELOPMENT archive 的 UBSan 与 mach_assert 依赖未在 RELEASE reference 选中 |
| 38 / [43755649212](https://github.com/KuriyamaMirai08/UniXNU-sheng/actions/runs/43755649212) | `bad20ac2099400d4e446e00c358c249ccb46a7af` | 全局 mach_assert 引起 `os_log_valid`未声明与 ipc_port 160/144 ABI 冲突 |
| 文档 / [43755647089](https://github.com/KuriyamaMirai08/UniXNU-sheng/actions/runs/43755647089) | 以该次日志为准 | 新 reference fixture 路径未登记 owner；与 release 首错无关 |
| 39 / [43794012575](https://github.com/KuriyamaMirai08/UniXNU-sheng/actions/runs/43794012575) | `86e63369f0fe0e914c14bbab72c629415fdcec7b` | 真实 RELEASE 已链接，`nm -g`漏掉 private section providers |
| 40 / [43802194750](https://github.com/KuriyamaMirai08/UniXNU-sheng/actions/runs/43802194750) | `ef14de119733f072f338ace7cdd34334df790937` | early framework test 找不到 `reference_diagnostics` helper；未开始 native 编译 |
| 41 / [43805045606](https://github.com/KuriyamaMirai08/UniXNU-sheng/actions/runs/43805045606) | `a9f0500af098f8aee87c86a571638daee92caf26` | 完整成功；随后独立静态验收和八 DTB 设备试验 |

run 38 的完整 18.4 GB 云端现场当时没有全部下载；恢复保留并逐项核验了覆盖错误、源码和 archives 的紧凑现场。最终 run 41 完整构建归档另外落地到本机，不能混写为“run 38 全量现场已本地保存”。

## 失败尝试与最终采用方案

| 历史做法 | 最终判定 | 推荐处理 |
| --- | --- | --- |
| 四个 weak 定义改 strong，使 chained imports 从 4 变 0 | 仅解决链接表现，后被认定为假 optional 实现，已撤销 | 缺席 provider 保持缺席，实际 guarded consumer + capability 检查 |
| 转写 Mach-O fixups 后绕过 parser imports 拒绝 | 仅离线实验，不是最终编译流程 | 编译真实代码，由原 parser 拒绝 imports/binds |
| 拓大 native DATA、重排 hole、删 USB roots | 失败或不解决同一布局约束 | 把真实诊断 table 移到 lazy allocation，完整 roots 保留 |
| 全局启用 reference mach_assert | run 38 确证引入 RELEASE ABI 冲突 | 两处原 debug.c guard，完整真实 lifecycle + minimal UBSan |
| reference 首次链接非零就拒绝 | 阻断原 object-derived forced-export reconciliation | 保留首错、对象导出分析，最终真实链接必须通过 |
| callable hook 用 scalar/空实现替代 | 最终流程拒绝 | same-run real storage/display/GPU/Image4 archives |
| 用 PYTHONPATH让本地 tests 找到 device helper | 掩盖 early framework dependency 缺失 | 安装 helper 在 tests 之前，清 Python 环境的 subprocess 验证 |
| 仅 `--check`后直接测 tree | 主控错误，check 不组 tree | 明确执行原 `unixnu tree`命令 |
| 跳过 Mesa patch、Cargo/Ninja、ABI、hash 检查 | 没有被采用为成功流程 | 固定真实 pins，保持 dependency/source 验证 |
| 把八 DTB 系统进入当成单 DTB 全通过 | 证据不支持 | 分别报告镜像、byte identity、用户观察与未解释差异 |

## 归档与可复查范围

原 run 41 完整 ZIP 是 11,068,522,795 字节，SHA-256 `b5c31d9788088054099222758a0c661a9d666d43b48840230328186b429a1658`；内部 `attempt.tar.gz`是 11,068,522,312 字节，SHA-256 `bf367b0b8cfe4a946faadc428a75ea3bb7d06b528171a722e8899c15f95e2bed`。

这些 hash 已由原归档验收记录验证；本教程没有为了编写文档再次遍历重哈希 11 GB。归档不含 `.git`，Git bundles 独立保存。producer 仅在双向内容/来源 hash 验证后省去已保留明文对应的 AEA 密文，省略 receipt 仍保留；“完整构建现场”不应解释为还含每个重复密文。

原研究树中的未提交修改仍保留。只有在最终 run 41 使用并有实际源码/receipt 证明的修改被写作有效修复；独立研究改动没有自动合入教程推荐路径。
