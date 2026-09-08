import os
import sys

from pymakex.datasets import CORTEX_M3_CFG, CORTEX_M4_CFG, DESK_GCC_CFG, TOOL_OF
from pymakex.flags import FlagsConfig
from pymakex.Helper import Helper

"""
TOOL  CPU
"""

toolpath_armgcc = r"D:\LLVM\arm-none-eabi-gcc14\bin"
toolpath_riscv = r"D:\LLVM\riscv\bin"
toolpath_default = None
tool = "clang"
prefix = ""
toolpath = toolpath_default

print("== Welcome to  PYMAKEx! ==")
hlp = Helper()

############
# ACTION COMMAND
############
CFG = DESK_GCC_CFG.clone()
hlp.Config(CFG)
# hlp.TOML()

############
# TOOL
############
# hlp["TOOLPATH"] = [toolpath2]
# hlp.Append(TOOLPATH=toolpath2)
hlp.Update({"TOOLPATH": None, "TOOL": tool, "TOOL_PREFIX": prefix})
# print(TOOL_OF(tool, prefix))
# print(hlp["CFG"])

hlp.Refresh()

src = ["main.c"]
# # # target
tgt = hlp.Program("test", sources=src)
hlp.DefaultTarget(tgt)

# mylib = hlp.Library_STATIC("src2")  # 指定party 名称
# hlp.DefaultTarget(mylib)
