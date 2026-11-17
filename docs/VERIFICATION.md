# 产物验收与已验证范围

## 分层记录结果

| 层次 | 成功历史结果 | 不能推出的结论 |
| --- | --- | --- |
| 构建 | run41 原release退出0并写manifest | 不证明硬件启动 |
| 静态 | 17准备源码、21绑定槽、49fileset成员、零missing/stubbed/unproven、布局/签名/POST/身份/结构通过 | 不证明所有运行功能 |
| loader | actual DarwinBoot ARM64 PE parser指令接受实际kernel，3个损坏负例拒绝 | 模拟止于ADT分配前，不证明ExitBootServices或kernelentry |
| 设备 | 用户报告八DTB变体进入系统 | 不证明单DTB版进入系统、性能/Wi-Fi问题已解决 |

原 `loadable=false`、`runtime_qualified=false` 保留。作者二进制字节等同、runtime POST执行和完整驱动资格化均未证明。

## 文件标识

| 文件 | 字节数 | SHA-256 |
| --- | --- | --- |
| 原流程 boot.img | 185733120 | `55f9099fb3a56a68d929bcdc6780755799d008de2910034d2ad37a42d4740b43` |
| 八DTB变体 boot.img | 189480960 | `fbf22394963b8ebcc3530c5eefa94da3249c0c35326dcfd9c8342f844c2932af` |
| payload.img | 184549376 | `e4e4fd50c85e38f5fd76f946132a7e08f00669998e85c3fa66781f26eb2312f4` |
| kernel/kernel.macho | 96665600 | `d9a27c37dec3227d0f5147686cebc50f8f3f3fdd078cda4bebbdc252f00fe5e7` |
| payload内实际kernel | 96665600 | `757f2297213314790f97a1339f1ce446b21fdb1ae686aa88574f22be8c4f83ed` |

kernel源码产物与payload内kernel之间680个word差异限于原诊断修补与POST密封范围。这不是随意忽略hash差异的许可；自己的构建必须逐项证明修改范围。新身份/Seed的产物不要求等于这些历史hash。

## boot.img 实际结构

Android header v0，page4096，base0，kernel_offset0x8000，ramdisk_offset0x1000000，tags_offset0x1e00000，无second。header的“kernel”是gzip(BootShim192bytes + 3MiB UEFI FD)后追加outerFDT；真正XNU位于ramdisk承载的176MiB FAT32 payload内。

原流程outerDTB为一项140142bytes；八DTB集合来自历史匹配stock输入。payload包括kernel、Apple ADT、trust/runtime sidecars和boot entry。outer DTB不是内层ADT，不能互换。

构建时 original pipeline验证输出hash、kernelargs长度（小于1000bytes）及板配置boot容量。独立验收另外检查AndroidID、零padding、FAT成员、边界、实际固件、签名和历史分区容量。历史容量记录不能代替另一设备当前布局确认。

## 使用本教程只读工具

在构建教程定义变量的环境中：

```bash
python3 "$GUIDE_ROOT/scripts/verify_manifest.py" --output-root "$WORK" --manifest "$WORK/package.manifest.json"
python3 "$GUIDE_ROOT/scripts/verify_boot_v0.py" "$WORK/boot/boot.img" --expected-dtbs 1
```

八DTB输入使用`--expected-dtbs 8`。脚本不写文件、不调用设备；manifest工具只查三个固定输出size/hash，不打印runtime身份，也不认证manifest来源。outer工具检查Androidv0边界/ID/零padding、gzip/BootShimheader、FDTblockbounds和FAT BPB几何。

**两工具不检查完整FAT文件链、XNU ABI/绑定、密码学签名、POST、Seed/rootpolicy身份、AVB认证或硬件行为。** 其JSON明确`full_static_acceptance=false`。不能把有限检查绿色当作全部验收完成。

## 完整静态复核应保留的证据

1. 固定源码/gitlinks和准备receipt；17项preparedsources实际bytes/hash。
2. 同轮真实archive/native/reference，四optionalfunctions缺席、零chainedimports，无native-stubs.c。
3. strict原引擎identity、21实际槽与typed/PAC/closure/形状/重定位证明；zero missing/stubbed/unproven。
4. codeend与DATAstart均为0xfffffff00b834000，overlap0、headroom0。新增代码必须重新测量。
5. 最终payloadkernel的POST HMAC及篡改拒绝、trustcache/addon/detachedcache页签名、身份/SeedUUID/rootpolicy一致性。原manifest含私人安装信息，不原样公开。
6. 原writer输出roundtrip、真实payload成员、firmware/DTB边界、bootcapacity与loaderparser证据。

这些完整工具的一部分依赖本机归档/输入，不是本仓库两个短checker的功能。本教程没有发布一套可移植的全静态验收替代系统。

## 八DTB变体的限定重包记录

原实验保留压缩firmware及整个payload的byteidentity，仅替换outerDTB集合，使用固定UEFI原writer写入新路径。具备自己有权使用且已核对的`kernel-with-matching-dtbs`、原payload和独立输出路径时，原命令参数为：

```bash
python3 "$UNIXNU_UEFI/Resources/Scripts/mkbootimg.py"   --kernel "$VARIANT_KERNEL" --ramdisk "$ORIGINAL_PAYLOAD"   --base 0 --kernel_offset 0x8000 --ramdisk_offset 0x1000000   --tags_offset 0x1e00000 --pagesize 4096 --header_version 0   --output "$NEW_VARIANT_OUTPUT"
```

这是原参数记录，输入拆包与DTB来源资格化不能省略；本仓库不提供DTB/镜像或自动变体生成入口。必须先确保新输出不存在，不能覆盖成功镜像。outer改动只能继承byteidentical内层材料的静态结论，不能继承未进行的硬件测试。
