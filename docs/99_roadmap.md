## ROADMAP

as 的工具 gcc or as? 是否带 -c 选项

of_vendor_model

default vendor model, 如何结合工具链

指定目录编译目录生成toml 文件

toml - party
nimmake -l 2 -t partyname

## issues

1. 修复 CommandBuilder 中的预处理问题 preprocess "STATIC" "SHARED" [已修复]
2. lib 自动安装问题
3. HEADER模式还是会自动编译 [已修复]
4. --dry-run 出现none问题， [已修复]
   tracker.py 148行
   traker.Track 返回两个值，一个为命令 一个为是否可以执行
   parsePaertie.py CommandBuilder.py 修改 [已修复]
5. --dry-run 执行命令 [已修复]
6. lib 时候， 会编译其他模块的代码， 如果为header 不编译, [已修复]
7. phony 仅仅支持字符串，不支持对象 [已修复]
   hlp.Phony("flash", [bin.name, flash.name])
8. rc!=0 显示全部错误信息 [已修复]
9. 没有取fpu CFG = CORTEX_M4_CFG.clone() [已修复]
   refresh 处理， backend 类中处理
10. lib, 不能生成libparty-\*.a, 可以phony指定lib, [已修复]
    依据 target_type 来判断是否生成lib
11. as -c 出现 -c 选项，可以出现c. 有的工具链找不到as [已修复]
12. 1.s 更新后没反应 05_arm32 [已修复]
    .s cannot get depends, so cannot update
13. lib 一直在更新 [已修复]
14. 出现错误不能退出
15. 厂商+模型 配置问题

## features

1. 临时调整party, 编译文件的扩展名 [已修复]
   help类 Parties 函数带有 参数 source_exts: list[str] = None
2. lib 是否可以和 phony 绑定
3. 文件多时 怎么加快速度
4. lib 自动安装问题 --lib 解决lib 快速编译安装问题
5. Thirdparty 为 不同厂家芯片提供接口文件 --chip 参数指定芯片
6. devicetree
