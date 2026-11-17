# 已确认问题与实际修复

本页的 24 张问题卡片按真实记录编写，包含编译阻断、构建主控错误、环境问题和部分验证的入口问题。**不是 24 项均已实机修复。** 每项的状态和适用条件分别说明。证据 E01–E13 的来源见 [EVIDENCE.md](EVIDENCE.md)。

默认源码基线：设备 fork `a9f0500af098f8aee87c86a571638daee92caf26`，framework `97437dcf7389484a0eeaa8067725ce743aff18ef`，UEFI `66421cb7bb5694843aec8de1ca3d1de4c20cca38`，24A446。以下路径以对应仓库为根；`$TREE`是完整教程定义的 assembled tree。修复提交用于追溯，成功 commit 已包含的修改不再重复 cherry-pick。**这些实验修复在个人 fork 或由其脚本作用于隔离副本，没有宣称官方 GitHub 已合入。**

## 问题索引

| 编号 | 问题 | 最终状态 |
| --- | --- | --- |
| [001](#bug-001) | 旧 startup 记录掩盖缺少 XNU headers | 编译修复已验证 |
| [002](#bug-002) | Ath12k tag / sparse / 网络获取不兼容 | 固定获取路径已验证 |
| [003](#bug-003) | bootstrap 与真正 compiler/final-link 错误混淆 | 精确 guard 已验证 |
| [004](#bug-004) | chained weak imports 与假 optional 定义 | 最终缺席语义已验证 |
| [005](#bug-005) | static DATA 多出 16 KiB | 真实 table lazy allocation 已验证 |
| [006](#bug-006) | 预链接未解析调用、数据对象与 ABI | 固定 21 槽静态已验证 |
| [007](#bug-007) | display root / IOHID / keyboard/GPU prerequisites | 成功流程已包含 |
| [008](#bug-008) | UEFI 全递归获取耗时/卡住 | direct gitlinks 路径已验证 |
| [009](#bug-009) | Xcode 系统组件不完整 | 历史主机修复已验证 |
| [010](#bug-010) | 持久构建 generated lock 被误判 dirty | 本地 guard 与 fixture 验证；非 run 41 入口 |
| [011](#bug-011) | reference 真实 archive 缺失 / placeholder | 同轮真实 archives 已验证 |
| [012](#bug-012) | forced exports 首次链接被过早拒绝 | 最终真实 link 已验证 |
| [013](#bug-013) | DEVELOPMENT diagnostics 未在 RELEASE 提供 | 与 014 配套已验证 |
| [014](#bug-014) | run 38 全局 mach_assert 破坏 ABI | 修复后 run 41 验证 |
| [015](#bug-015) | run 39 nm 漏掉 private section definitions | 实际二进制 + 6 负例验证 |
| [016](#bug-016) | run 40 early helper 未安装 | 隔离安装 + run 41 验证 |
| [017](#bug-017) | RPC numeric port 与 kernel pointer 常量混用 | 对象与静态绑定验证；runtime 未资格化 |
| [018](#bug-018) | XML allocator flag 与生成 header 不符 | 实际源码/对象已验证 |
| [019](#bug-019) | Image4 4 字节跨页引起代码碰撞 | minsize + 最终布局已验证，余量 0 |
| [020](#bug-020) | porting record 路径 ownership 缺失 | 文档云端检查已通过 |
| [021](#bug-021) | 重复下载、归档 CPU 与完整错误留存 | 缓存冷填充验证；warm 提速未测 |
| [022](#bug-022) | outer DTB 入口差异与 loader 模型 map | 部分验证；根因未证明 |
| [023](#bug-023) | `--check`不组 tree | 主控修复已验证 |
| [024](#bug-024) | u64 身份和 Data seed/UUID混淆 | 原输入验证；新用户路径未完整复现 |

## BUG-001

**XNU 生成 headers 缺失，但 startup.o.json 已存在**

- **出现阶段：** XNU bootstrap 后、corecrypto archive 编译前，尤其 fresh runner 恢复旧 compile-record cache 时。
- **错误表现：** `kern/clock.h`等生成 Kernel.framework headers 缺失，corecrypto 大量源文件编译失败；仅看到 `startup.o.json`存在就跳过 bootstrap。
- **根本原因：** startup 编译记录、XNU 对象与完整安装 headers/stamp 是不同依赖。恢复前两者不能证明后两者完整。
- **错误尝试：** 最初只检查 startup record；早期准备脚本还出现精确换行/marker 匹配错误，后续已纠正。批量清掉所有对象不是最终修复。
- **最终修复：** `prepare-package-ci.py`只修改固定 `kernel.py`的首个 bootstrap 条件，检查 `kern/assert.h`、`kern/clock.h`、`pexpert/pexpert.h`以及版本对应 installhdrs stamp；缺 headers 时只使不完整 stamp 失效，再跑真实 bootstrap/installhdrs。
- **操作步骤：** 在[教程第 5 节](BUILD_CN.md#5-按成功顺序应用准备修改)从干净固定副本执行 `python3 scripts/prepare-package-ci.py --unixnu "$UNIXNU_ROOT"`。保留 headers/stamp/compile 记录，不手工跳过 installhdrs。
- **涉及文件：** `device/scripts/prepare-package-ci.py`的 `transform_kernel_bootstrap`；`UniXNU/scripts/unixnu/kernel.py`首个 startup-record 条件；`$TREE/.cache/fakeroot/System/Library/Frameworks/Kernel.framework/Versions/A/{Headers,PrivateHeaders}`。
- **验证方法：** 日志缺少时明确强制 bootstrap，三份实际 headers存在，真实 corecrypto 两种 529-source variants编译与原目标检查通过。E06/E10 的运行记录和 compile-command 为依据。
- **适用条件：** 固定 framework；生成 SDK/cache不完整。新版本脚本 marker失配需重新审查，不扩大替换范围。
- **当前状态：** 编译修复已验证；corecrypto runtime POST仍未实测。相关最终 stamp 修复提交 `ddb3e7b410b5286b1cc96c4c44dccd63f99b8470`；中间失败 marker 修复不是额外步骤。

## BUG-002

**Ath12k 按 tag 克隆与 cone sparse 模式不兼容**

- **出现阶段：** Wi-Fi 源码获取。
- **错误表现：** 固定 ref/tag获取或 sparse路径操作失败，网络 timeout；脚本还需精确获取已锁定 commit而不是当时远端 ref。
- **根本原因：** 初始 `clone --branch source["ref"] --sparse`不适合该清单的文件级路径与实际网络来源；cone模式不能表达全部路径。
- **错误尝试：** 重跑未修的 fetcher；更早全局 Python改写会影响不相关逻辑；关闭来源检查没有采用。
- **最终修复：** 固定 fetcher transform：init仓库、`sparse-checkout set --no-cone`、按 `source["commit"]`浅 fetch，再 detached checkout；git.kernel.org与kernel.googlesource之间最多四次有界尝试。保留 hash/required inputs检查。
- **操作步骤：** 先执行 BUG-001 同一 `prepare-package-ci`步骤，然后 `bash drivers/Ath12kWifi/tools/fetch-sources.sh`。不要把 source-lock改为最新 tag；保留失败 deps现场用于分析。下载脚本可能重建它自己的失败依赖副本，只应在隔离构建目录使用。
- **涉及文件：** `device/scripts/prepare-package-ci.py`的 OLD/NEW与 `transform`；`device/drivers/Ath12kWifi/tools/fetch-sources.py`、`tools/source-lock.json`。
- **验证方法：** fetched commits与 source-lock相等，required Linux/FreeBSD/wpa材料存在且校验通过；run 41 `evidence/ath12k.log`阶段通过。E03/E06/E10。
- **适用条件：** Ath12k gitlink `48e23bf…`及固定 source-lock；不适用于任意新版 fetcher。
- **当前状态：** 获取与构建路径已验证；不代表 Wi-Fi运行问题全部解决。

## BUG-003

**把预期 bootstrap 缺 archive 的首轮链接与真正失败混为一谈**

- **出现阶段：** XNU bootstrap，board archives尚未构建。
- **错误表现：** 首轮 `LD mach.development.bcm2837.unstripped.noctf`只缺固定board符号；旧策略要么过早终止，要么只凭 startup record接受过宽失败。历史 M4 filter也曾漏认 `clang++: error: linker command failed`。
- **根本原因：** headers/objects bootstrap与最终完整链接的依赖不同；需要证明发生的是已审查的缺 archive链接，而非先前编译失败。
- **错误尝试：** 通用 `|| true`、任何存在 record就继续、把所有clang错误当 link-only；这些均不是最终接受策略。
- **最终修复：** `preserve.apply`安装精确 guard。24A446检查唯一 arm64e.kernel undefined block、唯一真实LD、之前无compiler/tool error、精确13symbols、当前轮非空link filelist及fresh实际objects；接受receipt写出原因。最终 native/reference/strict步骤仍要求成功。
- **操作步骤：** 原 `prepare-package-ci`后，在隔离副本执行 `preserve.apply`，如完整教程。发生 bootstrap失败时读 `$WORK/logs/bootstrap-guard.json`与完整 `kernel-bootstrap.log`。`accepted=false`必须保留首错并停止。
- **涉及文件：** `device/scripts/repro/bootstrap_guard.py`、`preserve.py`；生成 `UniXNU/scripts/unixnu/repro_bootstrap.py`与 `kernel.py`受控调用。
- **验证方法：** run 41接受实际13symbols和1,067 fresh objects的特定首轮链接，随后真实archives/native链接与预链接通过。错误集合、旧对象或先前compilererror均拒绝。E03/E06。
- **适用条件：** 固定24A446候选、原主控模式；guard没有授权接受final-link error。
- **当前状态：** 精确接受路径与最终构建已验证。

## BUG-004

**四个 chained weak imports，以及后来被推翻的“weak 改 strong”**

- **出现阶段：** native Mach-O完成后，XnuPrelink解析 chained fixups。
- **错误表现：** package29 / run42996277869存在四项 weak-lookup imports，ordinal -3，原 parser拒绝 imports/binds。四名为 `_sheng_ethernet_probe`、`_sheng_software_aes_probe`、`_ml_static_mfree_prepare`、`_iokit_physical_descriptor_close_notify`。
- **根本原因：** fork生成 weak定义，linker为本地引用仍产生 weak-lookup binds；后续审计又发现这些 empty/fixed-return定义让实际缺席可选接口冒充存在。
- **错误尝试：** weak改strong曾把imports从4变0，**后来撤销为不符合真实接口语义**；转写fixup的离线实验也不属于最终编译步骤。
- **最终修复：** 删除四个假定义，真实 provider缺席时保持缺席；依据实际源码/配置生成 capability header，只编译原 absent-provider branches。保留GPU untracked view lifetime/non-reuse等语义；已启用而缺provider必须失败。
- **操作步骤：** 检出成功设备SHA；执行 `prepare-sheng-author-audit.py`后组tree，运行 `check-sheng-optional-providers.py --tree "$TREE" --output …`。不要重新加入旧strong workaround。
- **涉及文件：** `device/scripts/build-gop-legacy-display-27.py`生成support；`prepare-sheng-author-audit.py`；`UniXNU/drivers/RamBlock/NativeRamBlock.cpp`、`drivers/Adreno740/NativeAdrenoPublish.cpp`；生成`build/sheng-optional-providers/provider-plan.json`。
- **验证方法：** run 41 `optional-final-native.json`四符号全部缺席，`kc_image.Image.fixups()`原检查通过，没有imports/binds。guarded consumer实链正负例通过，测试peer未进入production。E03/E06；E10旧weak/strong报告仅解释历史。
- **适用条件：** 当前24A446选中接口集合；macOS启用Ethernet/AES的配置不能直接沿用absent选择。
- **当前状态：** 最终缺席语义与完整构建静态验证通过。主要撤销/修复提交 `e404b6c768cbd728a746b620cf838ca790168879`。

## BUG-005

**native DATA 容量多出 16 KiB**

- **出现阶段：** fileset布局 /预链接，早于最后Image4 code碰撞。
- **错误表现：** native DATA约`0x1ec000`，历史容纳空间`0x1e8000`，多一16KiB页；改大空间会碰到其他member如Libm。
- **根本原因：** `package/BootUiTraceProbe.c`的1,024-entry CPU diagnostic history在static DATA/BSS中，占16KiB。它是诊断表而非必须嵌入静态映射的内核状态。
- **错误尝试：** 增大DATA/移动hole、删USB roots仍不解决相同原映射约束；这些实验未进入最终方案。
- **最终修复：** 保留完整table，改为首次诊断时通过`IOMallocAligned`分配并清零；allocation失败仅跳过诊断，不伪造状态。生成display archive的source key也加入脚本/support来源，避免复用旧生成代码。
- **操作步骤：** 使用成功设备SHA包含的修改；不要删roots或改emitter布局。可在macOS运行`python3 scripts/test-kcpu-allocation.py`短host检查，然后让完整native/prelink判定实际尺寸。
- **涉及文件：** `device/package/BootUiTraceProbe.c`的`struct bt_kcpu_seen`、`prepare_kcpu_seen`及`boot_kcpu_scan`；`scripts/build-gop-legacy-display-27.py`的sources清单。
- **验证方法：** host验证失败、zeroing、复用；历史native DATA降到`0x1e8000`，最终run41完整布局无overlap。E03/E06/E07/E10。
- **适用条件：** 固定诊断实现和24A446的保留collection布局。这里的16KiB页边界不改变arm64e profile 4KiB kernel页大小。
- **当前状态：** 构建/静态修复已验证。提交 `c4c0877a30e88c8cf88b5f52b904b1c57106df1c`；不是 runtime性能改善的实机证明。

## BUG-006

**真实预链接调用与数据对象不完整，不能用符号名字替代 ABI 证明**

- **出现阶段：** native与24A446 kernelcache匹配、PAC/调用/数据重绑定。
- **错误表现：** 严格emission遇missing/unmapped接口或无法证明的对象/重定位；早期预链接没有达到最终全部21binding slots合格。
- **根本原因：** 公共xnu12377与去符号24A446的真实调用接口、类布局和typed对象不能仅按相同symbol名称假定一致；后续还需要IOService dictionary RPC与四个正常Image4 PAL接口。
- **错误尝试：** `--allow-missing`、callable用scalar、固定成功return或猜`processor_info` flavor3语义未获最终采纳。不能把改expectedhash视为ABI证明。
- **最终修复：** 保留unchanged XnuPrelink引擎；strict wrapper按固定源hash、原function extents/shape、调用目标、PAC、typeddata、closure roots、original slot bytes审查。真实恢复RPC与normal Image4 PAL五接口，保留历史processor_info当前closure仅使用flavor1的条件。
- **操作步骤：** 检出成功SHA，执行完整准备、固定baseline check、同轮真实archive编译。由原release调用`sheng-strict-prelink.py`；不要另加allow-missing。缺baseline或source形状变化时按[缺口文档](REPRODUCIBILITY_GAPS.md)停止该验收，不自动放宽。
- **涉及文件：** `device/scripts/sheng-strict-prelink.py`、`clean-prelink-contract.json`、`clean-prelink-symbols.json`、`sheng-candidate-prelink-contract.json`、`m4_prelink_evidence.py`；真实补丁`driverkit-platform-function.patch`、`sheng-image4-normal-runtime.patch`。
- **验证方法：** 17preparedsources，21实际binding slots，missing/stubbed/unproven page references皆空；核对实际emittedimage而非fixture单独通过。E03/E06/E07。
- **适用条件：** 精确24A446 kernelcache、已审查closure/接口、匹配工具链及原baseline证据。不能对其他OS直接复用地址/契约。
- **当前状态：** 固定成功镜像静态已验证，runtime qualification仍false；新的用户身份/Seed/roots需要新验证。

## BUG-007

**display 根目录假设与未提前取得 IOHID / firmware / GPU 输入**

- **出现阶段：** 历史M4 native archive链，display、keyboard及GPU preparation。
- **错误表现：** run43063685115按`ROOT.parents[4]`找错shared helper；run43064254937缺IOHIDFamily checkout；run43064681233缺keyboard输入；另有GPU输入network timeout。
- **根本原因：** 持久`--out`不在framework checkout内，目录深度不是API；kernel-only bootstrap source subset不包含全部boardarchive prerequisites。
- **错误尝试：** 依赖旧树残留headers/firmware、继续根据parents层数找framework；仅重复bootstrap仍不会取得全部feed。
- **最终修复：** 明确`UNIXNU_ROOT`/`UNIXNU_DEVICE`；source-only准备取得固定references，真实touch/keyboard与Wi-Fi/Bluetooth输入前置；GPU读取有界重试但保留source/blob/hash。
- **操作步骤：** 按教程3节设定根变量，6节fetch完整feeds，7节预取输入，保持board archive generators顺序。不要在未准备输入的旧tree直接调用displaybuilder。
- **涉及文件：** `device/scripts/build-gop-legacy-display-27.py`shared helper定位；`UniXNU/scripts/build-sheng-source-drivers.py`；`device/scripts/extract-files.py`、fetch/preparation脚本；`board.toml`archives。
- **验证方法：** `UNIXNU_ROOT`实际指固定framework；IOHIDFamily实际revision正确；keyboard/GPU receipts/hash通过；run41相同完整archive链完成。E03/E06/E10。
- **适用条件：** 外置output目录或只运行kernel-only阶段的持久环境。
- **当前状态：** 最终流程已验证。显式根修复提交 `e0b31c59e6d9d35bc8dfe71caab87da854f22c94`；不证明触摸/显示runtime全部合格。

## BUG-008

**UEFI 全递归 submodule 获取无用测试依赖，构建准备长时间卡住**

- **出现阶段：** uefi-sheng checkout preparation，历史package66。
- **错误表现：** 递归走OpenSSL gost-engine、TLS tests、fuzz corpora及重复Mu_Basecore/Binaries；网络/git耗时，无必要板输入收益。
- **根本原因：** “有submodules”被解释为所有层都必须recursive，忽略选中OpensslLib/board实际inputs。
- **错误尝试：** 不加区别的`git submodule update --init --recursive`用于UEFI；删除正在进行的partial Git数据不是修复。
- **最终修复：** 固定firmware builder按`board.toml firmware.submodules`只更新四个direct gitlinks；feed供应Mu_Basecore，import步骤供应Binaries/sheng。历史持久preparation有界deadline，timeout停进程且保留仓库。
- **操作步骤：** UEFI top-level detached checkout后不recursive；让release firmware步骤执行原direct更新。若单独预取，只用板列出的四条路径且不加recursive。不要删旧Git/source或并行操作同一fetch。
- **涉及文件：** `device/board.toml [firmware] submodules`；`UniXNU/scripts/unixnu/firmware.py`；固定UEFI `.gitmodules`。
- **验证方法：** directgitlinks等于[source-pins.json](../evidence/source-pins.json)，release实际firmware完成；早期fixtures验证浅direct、非递归与timeout进程停止。E03/E06/E10。
- **适用条件：** 选中sheng DSC、OpensslLib及固定UEFI版本；不同板可能需要别的gitlinks。
- **当前状态：** run41构建路径已验证；无须恢复已退租M4主机。

## BUG-009

**Xcode 能回答版本，但 CoreSimulator 系统组件缺失**

- **出现阶段：** 历史M4 XNU firehose工具的xcodebuild。
- **错误表现：** run43057794006 exit70；`/Library/Developer/PrivateFrameworks/CoreSimulator.framework`不存在，IDESimulatorFoundation插件不能加载。
- **根本原因：** Xcode首启系统初始化未完成；单独clang和早期EDKsmoke不触发同插件。
- **错误尝试：** 只用`xcodebuild -version`/clang作为完整环境通过；继续编译不解决系统插件缺失。
- **最终修复：** Mac管理员完成官方`xcodebuild -runFirstLaunch`初始化，原sources/headers/objects保留。
- **操作步骤：** 选中正确`DEVELOPER_DIR`，在自己Mac管理员终端运行`sudo xcodebuild -runFirstLaunch`；再运行环境核对。不要存admin密码或把该命令写作无需管理员的自动保证。
- **涉及文件：** 主机Xcode安装与系统framework；历史`device/scripts/m4-xnu-corecrypto.py`准备逻辑；`reports/m4-xnu-corecrypto.md`记录。
- **验证方法：** 初始化后真实xcodebuild进入编译并完成已记录corecrypto阶段，而非仅版本输出。E10；run41主机直接完成相同生产链。
- **适用条件：** 系统组件不完整的macOS；与corecrypto源码本身无关。
- **当前状态：** 历史环境修复已验证；本次Windows文档轮没有运行管理员初始化。

## BUG-010

**持久 M4 的生成 unixnu.lock 被 checkout guard 当作未知 dirty 修改**

- **出现阶段：** package65 /run43153151789 checkout preparation，release之前。
- **错误表现：** `unixnu.lock`加入固定IOHIDFamily、解析IOStorageFamily后dirty，guard exit1。
- **根本原因：** 正常resolver生成的已审查lock变化未登记，持久路径应保留这两family解析结果。
- **错误尝试：** reset/删除lock会丢失现场；允许任意dirty或rewrite未知lock未采纳。
- **最终修复：** guard只接受原始lock或精确已审查两family版本，拒绝staged/其他未知修改；保留cache/privateSeed和lock原位。
- **操作步骤：** 历史持久路径按成功SHA中的guard使用；可运行`python3 scripts/test-m4-checkout.py`验证fixture。**不要把此持久checkoutguard搬进run41 fresh源码路径**，也不要Re-run旧workflow以期待新代码。
- **涉及文件：** `device/scripts/test-m4-checkout.py`、历史M4 preparation与`unixnu.lock`；`reports/m4-manual-release.md`记原/retainedlock blobs。
- **验证方法：** localGitfixtures重现exit1，已审查transition成功，unknown/stagededit拒绝，cache/Seed字节和时间不变。E03/E10。
- **适用条件：** 历史持久M4分支/两family生成lock；run41fresh入口不依赖此复用guard。
- **当前状态：** 本地guard已验证，不声称单独该提交跑过完整M4release。提交 `5bae136705758c1e8f9698b5d875b4615f9dd45e`。

## BUG-011

**RELEASE reference 用缺失或 synthesized provider，不能支撑真实匹配**

- **出现阶段：** 私有RELEASE-LTO comparison archive链接。
- **错误表现：** bring-upbuilder曾生成`native-stubs.c`，把callablehook用两个scalar替代；真实DEVELOPMENTarchive依赖未完全进入reference。
- **根本原因：** 比较native与原collection需要可解释的真实provider；用placeholder消除错误会改变接口/数据结构。
- **错误尝试：** 保留scalar/emptyhook或其他fakeimplementation；只看reference退出0而不检查来源。
- **最终修复：** 给原referencebuilder加`--force-archive`接口与内容cachekey，链接同轮实际Image4 normal、source-storage、Adreno740、late display archives；移除productionstub生成。
- **操作步骤：** 按教程第5节先`apply --check`/apply`patches/build/sheng-reference-archive.patch`，再authorpreparation。保持`board.toml`末尾referencearchive命令的四份真实archive，不手工换成oldstub。
- **涉及文件：** `device/patches/build/sheng-reference-archive.patch`、`board.toml [kernel] archives`、`prepare-sheng-author-audit.py`；`UniXNU/scripts/build-fileset-release-reference.py`。
- **验证方法：** receipt记录同轮archive输入与hash；实际finalreference定义成立；`build/xnu/fileset-reference`中无`native-stubs.c`；run41主控明确拒绝该文件。E03/E06/E07。
- **适用条件：** 固定comparison和24A446真实archive集合。
- **当前状态：** run41完整构建与strict验收通过，不能由此声称runtimeABI所有功能合格。关键提交 `e404b6c768cbd728a746b620cf838ca790168879`。

## BUG-012

**第一次 reference link 非零被拒绝，阻断原 forced-export reconciliation**

- **出现阶段：** reference第一次链接，`<initial-undefines>`forced exports。
- **错误表现：** 不可用forcedexports导致首link非零，过早退出使原object-derived pruning和第二次真实链接不能执行；历史成功比较记录67项移除。
- **根本原因：** 首次工具的试探/导出对账与最终链接被混为一个验收出口。不可用export清单不等于所有nativeundefined都可忽略。
- **错误尝试：** 任何首link非零立刻拒绝；反向允许任意未定义并生成stub同样未采纳。
- **最终修复：** 保留首linkundefined完整记录，按实际object符号对账原forcedexportlist，再要求finalreal link成功；编译失败没有filelist时保持原exit，不能继续对账。
- **操作步骤：** 成功SHA+第5节preparation已包含；读`first-link-undefineds.json`、`lto-build.log`和最后finalstatus。不要从native最终link删除未知undefined。
- **涉及文件：** `device/scripts/prepare-sheng-author-audit.py`referencetransform；`UniXNU/scripts/build-fileset-release-reference.py`forcedexport处理。
- **验证方法：** 六项publicationtests覆盖可对账与缺finalprovider的拒绝；run41最后实际reference link成功，originalexports移除清单保留。E02/E03/E06。
- **适用条件：** 固定原builder的object-derived privatecomparison；不放宽nativefinal或strictprelink。
- **当前状态：** 验证通过。提交 `2e3b1717601dbff6e2942017d39c703769439461`与后续preserved-exit修复。

## BUG-013

**run 37：真实 DEVELOPMENT archive 引入 diagnostics，RELEASE 未选择它们**

- **出现阶段：** run37 /43747167997 RELEASE reference最终链接。
- **错误表现：** 缺`___ubsan_handle_add_overflow_minimal`、`___ubsan_handle_negate_overflow_minimal`、`___ubsan_handle_sub_overflow_minimal`、`_mach_assert_jump_key`。
- **根本原因：** DEVELOPMENT真实archive带overflow instrumentation/assert引用，原RELEASE配置不选择对应真实runtime/statickey。
- **错误尝试：** 生成空UBSanhandler、把structuredkey用scalar替代，或禁consumerinstrumentation未采纳；首次全局mach_assert方案引发BUG-014。
- **最终修复：** 选中XNU原`san/memory/ubsan_minimal.c`，保留真实BTI/brk#ff00/ret及原lifecycle；只在原`debug.c`两guards启用genuinestatickey，不改变globalRELEASEassertABI。
- **操作步骤：** 使用最终preparation（不能只cherry-pick早期`1b6cdd…`）；archive命令保留`--native-diagnostics`，验收最终reference四项真实definitions及source/initializer。
- **涉及文件：** `prepare-sheng-author-audit.py`的`prepare_native_diagnostics`transform；referencecopy的`config/MASTER.arm64.bcm2837`、`osfmk/kern/debug.c`、原`san/memory/ubsan_minimal.c`。
- **验证方法：** actualreference `native-archive-diagnostics.json`记录原sourcehash、privateguard/selection、完整initializer与fourdefinedproviders；consumerinstrumentation未禁，run41通过。E02/E03/E06。
- **适用条件：** 同轮DEVELOPMENTarchives参与RELEASE-LTO；pureRELEASE其他用途不自动需要此选择。
- **当前状态：** 最终与014/015配套验证通过。早期提交 `1b6cdd48d65ecdfe81c5e8796b4ca6fd9b93bf5c`只解释历史失败。

## BUG-014

**run 38：全局 mach_assert 使 ipc_port 变大并启用未声明日志 assertion**

- **出现阶段：** run38 /43755649212 reference源码编译。
- **错误表现：** 内层log.c:517和529：`call to undeclared function 'os_log_valid'`；ipc_port.h:206：`sizeof(struct ipc_port) == 144`失败，实际160。末尾`nonltolink.filelist`缺失是secondaryexception。
- **根本原因：** 全局启用mach_assert改变RELEASE全局结构布局/条件声明，而真正需求只是archive引用的statickey及完整override lifecycle。
- **错误尝试：** 直接把144断言改160、补一个假`os_log_valid`、禁用assert/diagnostics、生成filelist以跳过compilererror，均未用于最终成功方案。
- **最终修复：** globalRELEASEassert配置保持原状；在固定原`debug.c`两处guard改为`#if MACH_ASSERT || XNU_REFERENCE_NATIVE_ASSERT`，privateflags加`-DXNU_REFERENCE_NATIVE_ASSERT=1`；保留真实UBSanminimal。compiler失败时不读不存在filelist，返回原buildexit。
- **操作步骤：** 运行成功SHA的authorpreparation，先短tests再fullrelease；核对referencecopyconfig与`native-archive-diagnostics.json`，不能手动全局启用mach_assert。
- **涉及文件：** `device/scripts/prepare-sheng-author-audit.py`；`scripts/fixtures/reference-native-diagnostics/{debug.c,MASTER.arm64.bcm2837}`；referencecopy原debug.c两guard与MASTER RELEASE选项。
- **验证方法：** run41实际Applecompile无两项首错，RELEASE ABI保持，真实四diagnosticsproviders合格；strict检查`global_assert_config_preserved`等receipt。E02/E03/E06/E07。
- **适用条件：** 固定RELEASEcomparison+DEVELOPMENTarchives；不是改变nativeDEVELOPMENT配置的patch。
- **当前状态：** 已验证修复。提交 `687fe3a0b7100c4e7ba54df294cc78c9b12f9b57`；run38失败方案已被替换。

## BUG-015

**run 39：nm -g 漏看真实 private section definitions**

- **出现阶段：** run39 /43794012575 reference链接后provider验收。
- **错误表现：** `Final RELEASE reference lacks genuine diagnostic definitions`，但实际binary四symbol的n_type均`0x1e`，section-backedprivateexternal definitions存在。
- **根本原因：** `nm -gUj`的globalonly筛选不是所有实际definitions集合。
- **错误尝试：** 因名字没出现就重新编写provider或绕过验收；会重复编译甚至加入假的symbols，不是修复。
- **最终修复：** 解析真实Mach-Osymtab/sections，只qualify有效N_SECT且有section/filebacking。三个handler检查实际BTI/brk#ff00/ret，key检查24byteoriginalenabledinitializer。debug、undefined、absoluteentries均不合格。
- **操作步骤：** 用成功SHA的`reference_diagnostics.py`。需单独复核时运行`python3 scripts/test-reference-diagnostics.py --binary "$TREE/build/xnu/fileset-reference/mach.release.bcm2837.unstripped.noctf" --output "$BUILD_ROOT/evidence/reference-provider-check.json"`。
- **涉及文件：** `device/scripts/reference_diagnostics.py`、`test-reference-diagnostics.py`、authorpreparation及copiedframeworkhelper。
- **验证方法：** 历史实际binary四definitions通过，6个损坏binary负例拒绝；productionreference字节未改。run41同helper通过。E04/E06。
- **适用条件：** 固定Mach-Oreference结构与qualifiedhandler/keybytes；不是通用“名字存在就通过”的parser。
- **当前状态：** 实际二进制与negative验证。提交 `c3c74d5c50d6b0c99f4b6759a36072d66c4493a7`。

## BUG-016

**run 40：reference_diagnostics 没有安装到 early framework tests 所在目录**

- **出现阶段：** run40 /43802194750 earlyframeworkregression，native编译前约两分钟。
- **错误表现：** `ModuleNotFoundError: No module named 'reference_diagnostics'`。
- **根本原因：** 已transform的frameworkbuilderimportdevicehelper，但helper直到treeassembly才会出现；本地临时PYTHONPATH掩盖遗漏。
- **错误尝试：** 在workflow补PYTHONPATH或跳过原frameworktests；两者未采纳。
- **最终修复：** authorpreparation首先把exactdevicehelper安装到`UniXNU/scripts/reference_diagnostics.py`，记录digest，再transform/runearlytests。subprocess清PYTHONPATH/PYTHONHOME并使用`python -E`验证实际依赖。
- **操作步骤：** 按教程第5节完整顺序，`prepare-sheng-author-audit`先于`test-fileset-reference`。不要只复制helper而漏receipt或sourcehashcheck。
- **涉及文件：** `device/scripts/prepare-sheng-author-audit.py`的`install_reference_verifier`、`test-author-audit-reference.py`；生成frameworkscripts/helper。
- **验证方法：** cleanenv子进程缺helper失败、安装helper后通过；6publicationtests通过；run41原4frameworktests也通过。本轮Windows只执行了六项publication和其他指定checks，没有冒称跑完macOS原4项。E05/E06/E12。
- **适用条件：** frameworkbuildertransformedbutearlytests在tree前执行。
- **当前状态：** 已验证修复。提交 `898c425a43ebba5ff31429df788ac42150963901`。

## BUG-017

**DriverKit RPC 的 numeric Mach port name 与 kernel pointer 常量混用**

- **出现阶段：** 恢复IOService dictionary platformfunctiontransport的真实arm64eobject编译。
- **错误表现：** numericportvalidity使用`MACH_PORT_VALID`宏，在kernelheader里与nullptr/portpointer常量的类型契约不符；不能靠用户态header掩盖。
- **根本原因：** `mach_port_name_t`数值namespace与kernel`ipc_port_t`指针不同，transport转换后的send-rightname需要数值0/dead判断。
- **错误尝试：** 以通用宏或替换header绕过类型错误；更早wrapper仅恢复IDL/methodID并不代表完整wire/ownership恢复。
- **最终修复：** 数值name采用`port == 0 || port == MACH_PORT_DEAD`明确拒绝；保留真实owning-taskobject转换、nestedcontainers、bit8wireflag、rollback及wrong-typeoutrelease。
- **操作步骤：** 成功设备SHA的`driverkit-platform-function.patch`已经在24A446series，第93项；不要重复apply。对其他源码移植要在IIG/generatedwrapper与IOUserServer transport处保持typed方法和ownership，而非只加同名函数。
- **涉及文件：** `device/patches/xnu-12377/driverkit-platform-function.patch`；prepared`iokit/DriverKit/IOService.iig`、`restore_platform_rpc.py`、`iokit/Kernel/IOService.cpp`、`IOUserServer.cpp`及headers。
- **验证方法：** 原IDL byteidentity、methodIDs、六真实Appletranslationunits与partiallink、原类fields/size/alignment、17sourcehash和最终RPCbinding。E03/E06/E07；未实机执行完整transport测试。
- **适用条件：** 24A446已观察的dictionaryRPC /numericrightnames。旧报告“patch未接入series”已过期。
- **当前状态：** 源码/对象/最终静态验证通过，runtimequalification未完成。提交 `8cb9c20f1686b21f2c049917ae4b258cab8a6bb6`。

## BUG-018

**OSUnserializeXML allocator flag 与实际生成 header 不符**

- **出现阶段：** XML恢复后的arm64e编译与sourcehashverification。
- **错误表现：** 旧生成版本使用`Z_SET_NOTSHARED`，与当前真实zoneheader所提供flag不一致；generatedparser与审查来源必须统一。
- **根本原因：** 生成parser/补丁使用了不同版本allocatorflag，不能按别的XNU版本的名字替换。
- **错误尝试：** 修改实际header提供旧flag、放宽sourcehash或只编`.y`而不核对生成`.cpp`；未采纳。
- **最终修复：** 恢复当前实际flag`Z_SET_NOT_EARLY`，保留原allocator与OSSerialize完整ABI；generatedXML/source均纳入17preparedhashes。
- **操作步骤：** 用成功SHA的第93patch；不重复手工改generatedfile。若重生成XML，使用匹配bison/source并核对`.y`、`.cpp`、sharedimplementationheaders与contract。
- **涉及文件：** `device/patches/xnu-12377/driverkit-platform-function.patch`；prepared`libkern/c++/OSUnserializeXML.{y,cpp}`、`OSSerializeBinary.cpp`及OSSerialize/OSUnserializeheaders；`sheng-candidate-prelink-contract.json`hashes。
- **验证方法：** actualgeneratedXMLunit编译，OSSerializefield/size/alignment匹配，所有selectedunits partiallink成功，run41源hash及strict通过。E03/E06/E07。
- **适用条件：** 固定xnu12377headers、24A446candidatepatches；不可对任意XNU使用同flag。
- **当前状态：** 已验证编译/静态修复。提交 `0df7b0708a2627dc21a2a9db5bd6f7675d6c35eb`。

## BUG-019

**Image4 代码仅多 4 字节，触发 16 KiB 取整后撞 collection DATA**

- **出现阶段：** run43715522445 strictprelink layout，native/reference已完成后。
- **错误表现：** `Native code would collide with collection data`；实际execsection末端只超旧容量4bytes，却跨了16KiB边界。
- **根本原因：** 保留collection的code/data布局无额外页，真实新增normalImage4adapter触发page-rounding。
- **错误尝试：** 移DATA/hole、删USBroots、放宽collision或整核优化/改功能语句不属于最终修复。
- **最终修复：** 仅六个真实Image4functions加Clang`__attribute__((minsize))`，不改C语句、锁、panic/errors、PACtypes、接口或全内核配置。
- **操作步骤：** 成功SHA的`sheng-image4-size.patch`必须在normal-runtimepatch之后（95/94）；让resolver应用。不要把sizepatch用于未有normaladapter的不同source。
- **涉及文件：** `device/patches/xnu-12377/sheng-image4-size.patch`；prepared`libkern/image4/image4_v2.c`六functions：register、copy_nonce_digest、set_nonce_digest、roll_nonce、load_diavlo_root_ca、load_local_policy。
- **验证方法：** 37existinghostchecks包括5panicnegative与realbackend/mirror；run41实际arm64ecompile+strictlayout：codeend与DATAstart同为`0xfffffff00b834000`，overlap0、headroom0。E03/E06/E07/E10。
- **适用条件：** 固定compiler、六adapter源与collection布局；换编译器/增加代码后重新测完整layout。
- **当前状态：** 静态修复已验证，**没有剩余codeheadroom**。提交 `1d0abd9fda19619997428dee020ccf609b473f12`；不能宣称所有未来改动都装得下。

## BUG-020

**文档 run43755647089：新增 fixture 没有 porting record owner**

- **出现阶段：** 独立文档/portingrecord检查，与release编译无关。
- **错误表现：** `scripts/fixtures/reference-native-diagnostics/MASTER.arm64.bcm2837`未归入已登记area；后续base比较也发现继承Adrenocapabilityflags/helper ownership缺口。
- **根本原因：** 新source/config/test路径需在`porting.toml`登记owner，workflow读取固定framework工具和当前真实变更。
- **错误尝试：** 只看记录结构不查与base变更、跳过ownership或使用最新frameworkchecker造成工具版本漂移；未采纳。
- **最终修复：** fixture登记configuration/diagnostics对应area，补compilerhelper与capabilityflags记录，保持17areas和固定checker。
- **操作步骤：** 修设备`porting.toml`准确area.paths/记录，运行`python3 "$UNIXNU_ROOT/scripts/porting-record.py" check --device "$UNIXNU_DEVICE" --base "$BASE_SHA"`。新shallowcheckout缺base时先有界fetch实际base，不凭空改checker。
- **涉及文件：** `device/porting.toml`、`.github/workflows/porting-record.yml`；framework`scripts/porting-record.py`。
- **验证方法：** 17area结构与真实base变更通过，云端run43794301757成功。E02/E03/E11。
- **适用条件：** 对上游或上一提交有相关code/config变化；文档绿色不代表boot构建成功。
- **当前状态：** 云端已验证。提交 `86e63369f0fe0e914c14bbab72c629415fdcec7b`、`07c939cd102aa877f6f3188705a7bd0bf2f1d3bc`、`9ad441eec6d78a656f80b38dd5e92ed82415e36a`。

## BUG-021

**反复下载已验证输入，以及构建结束后归档/上传耗时**

- **出现阶段：** hostedfreshbuild输入阶段与最终archive。不是“XNU编译所有时间可被缓存解决”的证明。
- **错误表现：** run39约34min到失败后又约19minarchive/upload；新runner重复读取IPSW/vendorinputs。失败若只看Actions最后报错会丢innerlog。
- **根本原因：** 临时主机不保留downloads；压缩全场景后upload再次压缩；runtimeSeed与buildobjects不能混在可共享downloadcache。
- **错误尝试：** 只凭文件存在命中cache、复用unknownobjects/privateSeed、删除错误现场、声称还没测过的warmcache必定显著提速，均未采用。
- **最终修复：** target/source keyed下载cache逐文件重hash；只缓存原脚本verifiedpublicdownloads（不是公开分发许可），不含compiledobjects/runtime/privateinputs。archivegzip1、uploadcompression0；AEAduplicate仅双向hash/provenanceverified后省略并记录。
- **操作步骤：** 使用成功workflow的`download_cache.py`restore/capture与原`archive-attempt.py`；cachekeys/checks不可去掉。完整日志和source/objectscene私有落地；不要把含Apple/固件的cache在公开fork分享，详见[Actions](GITHUB_ACTIONS.md)。
- **涉及文件：** `device/scripts/repro/download_cache.py`、`test-download-cache.py`、`archive-attempt.py`、`collect-author-audit.py`；`.github/workflows/sheng-clean-release.yml`；固件range downloader与`firmware_cache.py`。
- **验证方法：** 5cachetests覆盖reuse/corruption/path/identity/archive；run41 coldmiss后save2,011files/9,984,049,658bytes，所有来源check仍执行；archive记录AEAomission。E03/E06。
- **适用条件：** 固定24A446/ROM/sourceidentity、私有授权cacheenvironment；跨target不可混用。
- **当前状态：** cachecoldcapture/本地逻辑通过；**warm整轮提速未测**，compiledobjects未缓存。提交 `c3c74d5c50d6b0c99f4b6759a36072d66c4493a7`；约8minarchive的run41与run39差异不能当controlledbenchmark。

## BUG-022

**外层单 DTB 与八 DTB 入口差异，及早期 loader 验证 map 格式错误**

- **出现阶段：** boot.img交付后的限定入口实验、独立loader模拟。
- **错误表现：** 单DTB没有本次进系统观察；另行八DTB变体用户报告进系统。旧loader-01初次map模型不接受producer格式，不能当镜像boot失败。
- **根本原因：** mapfailure已确认是测试harness未处理zeroRVA等producer记录；outerDTB入口差异与板匹配根因**未证明**。
- **错误尝试：** 把Fastboot/黑屏直接认定内核或所有UEFI坏；把harnessmap错误当DarwinBoot本体bug；八DTB结果推广到所有设备，均不成立。
- **最终修复：** harness适配actualproducer map，保留实际PEparser指令与旧失败记录；独立变体用originalmkbootimg，仅换outerDTBs及必要headerlen/ID，firmware/payload保持byteidentity。没有改内核为“可启动”。
- **操作步骤：** 先按[验收](VERIFICATION.md)检查原singleDTB版，核对DTB来源/size/count/boardcompatibility。八DTB重包只能对自己有权使用的matchinginputs按原writer生成新文件；本教程不分发DTBs或自动刷入。
- **涉及文件：** 固定UEFI`Resources/Scripts/mkbootimg.py`；`UniXNU/scripts/unixnu/bootimg.py`；私有`stock-dtb/manifest.json`与`loader-02/RESULT.json`。
- **验证方法：** firmware与payload各自byteidentity，AndroidID/边界/zeroPadding通过；actualparser接受正确kernel并拒绝3damagecases，止于ADTallocation前；hardware只为用户对八DTB版的反馈。E07/E08/E09。
- **适用条件：** 原run41payload/firmware与该设备历史DTBs；不保证其他boardrevision相同。
- **当前状态：** 部分验证；**DTB差异根因未解决，ExitBootServices/内核入口/驱动runtime没有由模拟证明**。

## BUG-023

**release --check 列出配置，但主控误以为 tree 已组装**

- **出现阶段：** run43714673586短preparation后、prelinkregression之前。
- **错误表现：** `--check`通过但期望的`tree/kits/XnuPrelink`不存在，未开始真正编译。
- **根本原因：** 原release在check模式于列patch/config后提前return，不执行`cmd_build`/tree；主控缺一步。
- **错误尝试：** 修改原check语义、关闭prelinktests或从旧tree复制结果；未采用。
- **最终修复：** 主控明确调用原`unixnu tree`，然后检查freshobjectinventory与originalenginefixtures。
- **操作步骤：** 按教程6节 `--check`、`status --json`、`tree`，顺序不省略；不要只凭checkdone文本跳到compiler。
- **涉及文件：** `device/scripts/repro/run-release.py`的`assemble-tree`阶段；framework`scripts/unixnu/cli.py cmd_release`的checkreturn。
- **验证方法：** run41主控 `assemble-tree`通过，precompileobjects为空，36originalenginechecks通过。E03/E06。
- **适用条件：** check-onlyconfiguration作为preflight的主控；不是XnuPrelink代码错误。
- **当前状态：** 完整成功路径已验证。

## BUG-024

**平台 u64 身份、Data seed 与安装 UUID 混用，旧 workflow 八位检查也不适用**

- **出现阶段：** workflowinput、runtimeprepare、Seed对象预检与最终manifest身份校验。
- **错误表现：** 旧hostedREADME/package入口只接受8hex；真实u64高位被误截断的风险。run43711505839对象已通过却SeedUUID与原安装不同，表明仓库default不能替代installedSeed。
- **根本原因：** platform`unique-chip-id`、APFSDataUUID、packedSeedbytes是三种不同输入；缺cache不说明应该生成新Data。原runtime会在编译前绑定实际SeedUUID。
- **错误尝试：** 截到8digits、用仓库defaultUUID替换实际UUID、复制别人Seed、cachemiss自动`--init-data`、只改compiledUUID不重kernel，均不作为推荐。
- **最终修复：** 非零hexu64完整值1–16digits（可0x）；保留/校验实际原Seed，输入只有首次newseed与已有seed两个互斥入口；runtimeprepare在kernel前读取实际UUID并更新工作区config。
- **操作步骤：** 私下提供自己`UNIXNU_UNIQUE_CHIP_ID`，不输出值；既有安装用`--data-ramdisk FILE`，first用`--init-data`且保存generatedseed。使用[教程4/8节](BUILD_CN.md)的真实接口；不要复制个人AESGCMworkflowSecret/contract。
- **涉及文件：** `device/scripts/prepare-sheng-candidate-inputs.py`（原个人恢复，不作为通用入口）、`sheng-candidate-input-contract.json`（不公开内容）；`UniXNU/scripts/unixnu/runtime.py prepare/seed_uuid`、cli及`make-data-seed.py`；boardruntime/ADTconfig。
- **验证方法：** 原run41实际Seedhash、runtimeUUID、preparedconfig与finalpayload/rootpolicy身份一致，malformed/corruptauthenticatedinput拒绝。新input须重新验收，不只改expectedhash。E03/E06/E07/E10。
- **适用条件：** 原安装或自己的明确firstseed；新的DataUUID/容量可能改变strictshapecontract。
- **当前状态：** 原输入路径静态验证通过；**新设备/新Seed完整路径未在本轮复现**。首次设备安装与jailbreakbootstrap不是本项完成范围。

## 没有被确证为独立已修 Bug 的项目

- **Mesa patch冲突：** 历史审计推翻了某些“必须关闭验证”的结论；实际固定Mesa17patch顺序与reverse检查成立，run41生产build保持检查。没有据此添加一张“禁Mesa验证已修复”卡片。
- **ArmDTPlatform archive/index：** 最终使用真实原archive、目标检查与符号证据；没有发现足以单独归因的“ranlib故障已修复”证据。相关真实依赖问题在001/006/007/011记录。
- **Android header/BootShim：** 最终v0/page4096/压缩FD+DTB/FATpayload的组成有验收证据；没有为了满足主题列表而虚构bootheader或BootShim源码bug。需要如何检查见VERIFICATION。
- **Windows换行：** 本教程隔离准备首轮CRLF影响精确marker，第二轮只在独立副本normalizeLF模拟macOS；这是文档复核环境差异，不是run41macOSbuildbug。
- **Wi-Fi与动画：** 当前仍未解决，详见[KNOWN_ISSUES](KNOWN_ISSUES.md)。source/buildgreen不能替代实机修复。
