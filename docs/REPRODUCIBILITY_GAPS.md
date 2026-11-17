# 复现条件与尚未补齐的部分

成功 run 41 已有完整工程、日志、镜像和验收记录，但把私人实验转换成供任何新设备使用的公开构建流程，需要额外条件。本教程没有隐去这些条件，也没有为了“一键成功”删除校验或加入占位实现。

## 1. 原成功工作流的个人输入

`device/scripts/prepare-sheng-candidate-inputs.py`读取特定个人 AES-GCM 输入与 Secret，按固定 contract 恢复原安装的 Data seed 和 unique-chip-id。普通用户没有这份安装状态，也不应该使用其他设备的 Seed 或身份。

本教程仅引用该文件路径和作用，不复制密文、解密材料、个人 UUID、输入 contract 内容或 Seed hash。fork 原仓库时，也应单独审查它已有的个人输入与历史记录，不能由本教程的公开检查推导原 fork 全仓库已经脱敏。

自己的输入应通过普通接口提供：

- `UNIXNU_UNIQUE_CHIP_ID`：自己的非零 u64 十六进制值，1–16 位，可有 `0x` 前缀。
- `--data-ramdisk FILE`：自己的现有安装 Seed。
- `--init-data`：仅首次生成自己的 Seed；与上一参数互斥。

替换为自己的输入属于新配置，需要重新验证。Secret 的名称可以公开，实际值不能进入教程或公开日志。

## 2. strict prelink 依赖旧 native 证据

run 41 主控要求 `--baseline-archive`，历史 Actions 从 run `43729102858` 的 `layout-inputs-43715522445-43729102858`取得 `layout-inputs.tar.gz`。接受的两份历史封存 SHA-256 为：

```text
76f8549e40c2657ec71149b82b83c696d3ccfeefcc00d8742e409cad67d5a01b
f9328464d2f664a2b526a0d91bd3f35659cdfd9e2f26a5fa7696cf5f40c442ba
```

其中仅提取 hash 匹配的旧 native 与旧 `kernel.py`作比较证据。**它不恢复旧 `.o`、`.a`来代替干净编译。** `sheng-strict-prelink.py`必须看到固定 native；regression check 必须看到固定旧脚本。

本机完结归档保留了这些证据；本教程不分发 native 二进制。历史 artifact 有保存期限，其他 fork 的 run ID 也不继承。本轮检查成功源码链接可访问，没有承诺该旧 artifact 仍可向公众下载。

因此从空机器且没有有权使用的 baseline 开始，可完成源码准备与部分预检，但**不能按现有固定 strict contract 完成最后预链接验收**。建立不依赖旧 native 的新证据契约属于后续开发，本任务没有完成。

## 3. 新 Seed、参数和存储布局

原 `runtime.prepare`在编译内核前读取 Data UUID，写入工作区生成 `.config`。新的 Seed 会改变这个 UUID，可能改变源码生成物、函数形状与最终二进制。现有 strict contract 固定 17 项准备源码及历史函数/重定位结构，不能仅更新几个 hash 就证明新输入合格。

run 41 使用保留 Seed，并未验证首次 `--init-data`的完整成功路径。教程给出该接口与正确顺序，但不会声称第一次安装已在这个成功 run 中验证。

同样，设备板配置中的 `data_gib = 215`、userdata LBA、RAM/owned memory、ADT、根策略都属于当前板适配参数。不能把它们当作所有容量版本或任意 Android 分区布局的保证。现有安装的 Seed 不是完整当前 Data 备份。

## 4. 环境并未完全可锁定下载

成功环境的 Xcode、SDK、Apple Clang hash、Rust 和其他工具版本已记录。历史工作流使用 `macos-26`与 Homebrew 实时公式，不是不可变主机快照。

本地可在匹配的 Apple arm64 主机安装固定 Xcode/Rust，手动准备同版其他依赖。教程记录的 `brew install`命令来自成功工作流，但当前执行未必得到同样版本。没有可靠的已验证命令可凭空重建旧 runner image；不能声称选择 `macos-26`就一定得到原 image。

严格 compiler/hash 检查失配应停下核对工具链，不能改预期值掩盖未验收的新编译器。

## 5. 许可门槛

特别是 [corecrypto 内部使用许可](../THIRD_PARTY_NOTICES.md)，历史第三方快照并不自动授权普通社区移植和产物发布。本教程完整披露技术依赖，不提供扩展许可，不提供源码或镜像。

这项限制来自实际读取的许可证，不是推测。尚未确认合法覆盖该用途时，不应把后续含 corecrypto 的命令描述为人人可自由使用的推荐系统发布流程。

## 6. 验收工具的可移植性

原完结工程的部分独立验收工具绑定本机归档路径、实际 DarwinBoot PE/map、输入和原 hash。它们并非全部可直接拷贝给第三方使用。本教程只新写有限的只读检查器，核对外层镜像与 manifest；不声称替代 21 槽 ABI、POST 或实际 loader parser 的完整验收。

| 路径 | 本次达到的范围 |
| --- | --- |
| 历史成功 run 41 | 完整干净编译、打包和随后静态验收 |
| 独立 Windows 副本 | 准备修改与 run 41 一致；6 + 5 + 36 项指定检查通过 |
| 全新 macOS + 公开文件 + 新设备输入 | 未全量构建验证；上述证据、身份与许可条件需满足 |
| 首次安装 | 给出真实入口；没有宣称 run 41 覆盖了此路径 |
| 八 DTB 变体 | 历史该设备用户报告进入系统；不保证所有 sheng 都需要相同变体 |

如果缺少必须输入，应保留准确错误与未完成阶段。不要选 `--allow-missing`、替换 fake provider、禁用回归、替换别人的身份或手工把验收标志改成通过。
