import os
import sys

__file_dir__ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, __file_dir__)

# from pymakex.builder import Parties
from pymakex.datasets import CORTEX_M3_CFG, CORTEX_M4_CFG, TOOL_OF
from pymakex.flags import FlagsConfig
from pymakex.Helper import Helper

# from pymakex.thirdParties.MyParties import MyParties

"""
TOOL  CPU  armclang  --keil
"""

toolpath_armgcc = r"D:\LLVM\arm-none-eabi-gcc14\bin"
toolpath_clang = r"D:\LLVM\ETArm\bin"
toolpath_armcalng = r"D:\LLVM\riscv\bin"
toolpath_riscv = r"D:\LLVM\riscv\bin"

toolpath = toolpath_riscv
tool = "armclang"
prefix = ""

ToolChain_armgcc = {"TOOLPATH": toolpath_armgcc, "TOOL": tool, "TOOL_PREFIX": prefix}
ToolChain_armclang = {"TOOLPATH": toolpath_armgcc, "TOOL": "armclang", "TOOL_PREFIX": ""}
ToolChain_gcc = {"TOOLPATH": toolpath_armgcc, "TOOL": tool, "TOOL_PREFIX": ""}
ToolChain_clang = {"TOOLPATH": toolpath_clang, "TOOL": "clang", "TOOL_PREFIX": ""}
ToolChain_riscv = {"TOOLPATH": toolpath_riscv, "TOOL": "gcc", "TOOL_PREFIX": riscv_prefix}
toolchain = ToolChain_armgcc

print("== Welcome to  PYMAKEx! ==")
hlp = Helper()

############
# ACTION COMMAND
############
CFG = CORTEX_M4_CFG.clone()

hlp.Config(CFG)
hlp.set_cfg("linkscript", "src_stm/STM32F407XX_FLASH.ld")

# hlp.TOML()


############
# TOOL
############
# hlp["TOOLPATH"] = [toolpath2]
# hlp.Append(TOOLPATH=toolpath2)
hlp.Update({"TOOLPATH": toolpath, "TOOL": tool, "TOOL_PREFIX": prefix})
# print(TOOL_OF(tool, prefix))

hlp.Refresh()

# Affer Refresh

hlp.Append(LIBS="m")
hlp.Append(LIBS="c")

core = hlp.Parties("CORE", "src_stm/Core")
driver = hlp.Parties(
    "Driver",
    "src_stm/Drivers",
    # build_type=BuildType.STATIC.name,
    defines={"STM32F407xx": "", "USE_HAL_DRIVER": ""},
)

core.DependOn(driver)
driver.DependOn(core)

# print(hlp["LIBS"])
# print(core.depends, "======================")
# print(driver.depends, "======================")
# print(driver.defines, "======================")
# print(driver.include_dirs(), "======================")


print(hlp.Flags)
# # print(hlp["PARTIES"])


# # # target
t = hlp.Program("test")
hlp.DefaultTarget(t)

# mylib = hlp.Library_STATIC("src2")  # 指定party 名称
# hlp.DefaultTarget(mylib)

cmd1 = hlp.Command("CMD1", ["hello world"])

# hlp.Phony("ph1", ["test", "src", cmd1])
# hlp.Alias("my", ["test", "src", cmd1])


print("+" * 20)
print(" ")
