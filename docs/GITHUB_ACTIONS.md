# GitHub Actions 构建与节省等待成本

**本教程仓库不包含 `.github/workflows` 工作流，不会因 push 或 fork 自动构建、读取设备 Secret、上传安装输入或发布镜像。** 下文只解释历史构建仓库的流程；不要将其私人输入恢复与 artifact 上传步骤照搬到公开仓库。

## 真实成功入口

run 41 使用设备提交 `a9f0500af098f8aee87c86a571638daee92caf26` 的 `.github/workflows/prebuild-audit.yml`，输入 `full_release=true`，调用同提交的 reusable `.github/workflows/sheng-clean-release.yml`。

runner 为 macos-26 arm64，成功 image 为 20261102.0473.1，Xcode 26.6。release job timeout 350 分钟，主控执行预算 300 分钟。环境完整版本见[版本索引](SOURCES_AND_VERSIONS.md)。选择浮动 macos-26 不保证今后仍是该 image；Homebrew 命令也不冻结版本。

## 在自己的仓库使用前

原 workflow 是个人实验入口，不能直接作为通用模板发布：

1. `prepare-sheng-candidate-inputs.py`恢复个人加密 Seed/身份，需要原 Secret。不要复制或索取该人的密钥/Seed。
2. 原 workflow 下载 run 43729102858 的固定 baseline artifact；新 fork 不拥有同一 run，artifact 也可能过期。检查[复现缺口](REPRODUCIBILITY_GAPS.md)。
3. 使用自己的安装输入后，要重新确认 strict contract，而不是删除 hash/shape/ABI 检查。
4. 原归档与 delivery 含系统文件、固件、镜像、私人安装摘要，不能照搬到公开 artifact 上传。本教程不附带可直接发布这些内容的 workflow。

建议先在独立私有构建仓库，以[中文教程](BUILD_CN.md)中的真实命令完成输入迁移与预检查，确认许可、私有存储与输出留存，再手动启动长构建。公开教程仓库仅存文档和原创检查器。迁移后的 workflow 尚未由本次全量构建验证，不能标为一键成功。

## 调用已具备原条件的历史入口

仅适用于拥有匹配输入、baseline、环境和仓库权限的历史工程；不是新用户无输入的快速开始：

```bash
# Set these to your authorized build repository and reviewed branch.
gh workflow run prebuild-audit.yml --repo "$BUILD_REPOSITORY" --ref "$BUILD_BRANCH" -f full_release=true
```

启动前核对分支实际 SHA 与固定源码。新 workflow 只在实验分支尚未被默认分支注册时，历史通过已经注册的 prebuild-audit 调用同 commit reusable workflow解决；不需要擅改稳定分支。GitHub token 仅供当前授权仓库下载/API，不写入日志。

## 缓存与耗时

原 `scripts/repro/download_cache.py`按目标、固件清单、framework、kernelcache和实现 hash生成 key，恢复时逐文件重hash，source downloader继续校验来源。只缓存下载输入，不缓存 native objects、archives、runtime或 Seed。

run41为 cold miss，结束保存2,011文件、9,984,049,658字节；warm整轮提速没有测量。脚本称 public downloads是输入来源分类，不表示 Apple/固件可公开再分发。普通 GitHub cache不是私人安装材料的存储位置；公开仓库的缓存也不能用来保密，应先确认访问和许可范围。

归档 gzip level1，已压缩artifact upload compression-level0。重复AEA密文只有在明文及其来源双向校验后才省略，receipt保留。不要为节省空间删错误源码、objects或完整内层日志。

run41 release阶段约45m54s；此前 preparation和之后归档上传另计。一小时的大部分编译不会因避免重复下载全部消失。持久M4的corecrypto对象复用曾独立验证，但该主机已退租，run41没有整轮对象缓存。

## 错误留存与人工看守

保存每阶段日志、stages.json、准备diff/receipts、inner lto-build.log、compile-command、strictreceipt及manifest。release完成只表示构建通过，继续按[验收](VERIFICATION.md)检查。

手动查看 Actions 页面即可。没有其他任务只剩等待时停止反复轮询；由使用者待运行结束后继续审查。失败先下载最小必要错误证据，不重复已通过的短对象检查或无改动 release。完整场景保存到自己的私有位置，公开问题报告只附脱敏首错。
