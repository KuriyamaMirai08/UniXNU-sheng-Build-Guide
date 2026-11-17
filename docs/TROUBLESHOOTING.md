# 按报错排查

先确定失败阶段和构建 SHA，保存完整内层日志。Actions 最末异常可能只是次生错误。下面编号链接到包含原因、操作、源码位置与验证方法的完整问题卡片。

| 关键表现 | 优先处理 |
| --- | --- |
| kern/clock.h、kern/assert.h 缺失 | [BUG-001](BUG_FIXES.md#bug-001)：生成 headers/stamp，不能只看 startup record |
| Ath12k clone/tag/sparse 失败 | [BUG-002](BUG_FIXES.md#bug-002)：固定 commit、non-cone sparse、有界网络重试 |
| bootstrap undefined symbols | [BUG-003](BUG_FIXES.md#bug-003)：只接受精确 bootstrap 集合，不能忽略最终链接错误 |
| chained imports、weak lookup ordinal -3 | [BUG-004](BUG_FIXES.md#bug-004)：删除假 optional 定义，保持实际缺席语义 |
| DATA 0x1ec000 vs 0x1e8000 | [BUG-005](BUG_FIXES.md#bug-005)：诊断 table lazy allocation |
| missing/stubbed/unproven binding | [BUG-006](BUG_FIXES.md#bug-006)：核对固定 baseline、实际接口和严格契约 |
| display helper、IOHID、keyboard input 缺失 | [BUG-007](BUG_FIXES.md#bug-007)：明确根目录并预取完整依赖 |
| UEFI submodule 长时间获取 | [BUG-008](BUG_FIXES.md#bug-008)：只初始化板需要的 direct gitlinks |
| Xcode exit 70 / CoreSimulator.framework | [BUG-009](BUG_FIXES.md#bug-009)：管理员完成 Xcode 首次初始化 |
| retained unixnu.lock 被拒绝 | [BUG-010](BUG_FIXES.md#bug-010)：核对已审查 lock，不能放行任意 dirty |
| native-stubs.c 或缺真实 reference archive | [BUG-011](BUG_FIXES.md#bug-011)：同轮真实 archives |
| initial-undefines 首次链接非零 | [BUG-012](BUG_FIXES.md#bug-012)：原对象导出对账后最终真实链接必须成功 |
| UBSan / mach_assert_jump_key 未定义 | [BUG-013](BUG_FIXES.md#bug-013)：选择真实诊断实现并配套下一项 |
| os_log_valid 未声明 / ipc_port 160 vs 144 | [BUG-014](BUG_FIXES.md#bug-014)：恢复 global RELEASE ABI，仅两处 private guard |
| reference 缺 providers 但 nm 只查 global | [BUG-015](BUG_FIXES.md#bug-015)：检查真实 N_SECT 定义和实现字节 |
| ModuleNotFoundError: reference_diagnostics | [BUG-016](BUG_FIXES.md#bug-016)：early tests 前安装 helper |
| numeric port / nullptr 类型错误 | [BUG-017](BUG_FIXES.md#bug-017)：numeric Mach name 判断 |
| Z_SET_NOTSHARED / XML allocator flag | [BUG-018](BUG_FIXES.md#bug-018)：匹配真实 headers 与生成 parser |
| Native code would collide with collection data | [BUG-019](BUG_FIXES.md#bug-019)：六函数 minsize，重新验证实际布局 |
| porting record unowned path | [BUG-020](BUG_FIXES.md#bug-020)：登记 area.paths 并检查真实 base |
| 一再下载 / 归档上传很慢 | [BUG-021](BUG_FIXES.md#bug-021)：逐文件验证下载缓存，避免二次压缩 |
| 静态通过但回 Fastboot / loader 模型拒绝 | [BUG-022](BUG_FIXES.md#bug-022)：区分 outer DTB、模型输入和硬件观察 |
| check done 后 tree 不存在 | [BUG-023](BUG_FIXES.md#bug-023)：独立执行 unixnu tree |
| Seed UUID、u64 身份失配 | [BUG-024](BUG_FIXES.md#bug-024)：使用自己的完整身份与原 Seed |

## 避免重复一小时构建

先跑能复现问题的最短相关检查。修 helper 安装无需先重编 XNU；文档 ownership 失败也不需要重新 release。真实源码或工具链变化后，仍需相关对象和完整集成验证。新 dispatch 使用新提交；对旧 run 点击 Re-run 使用的仍是旧版本。

缺少历史 baseline、自己的 Seed 或符合用途的授权时，按[复现缺口](REPRODUCIBILITY_GAPS.md)记录未完成阶段。不要通过删检查或改 expected hash 让其显示成功。
