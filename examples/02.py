import os
import sys

__file_dir__ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, __file_dir__)

from pymakex.datasets import CORTEX_M3_CFG, CORTEX_M4_CFG, DESK_GCC_CFG, TOOL_OF
from pymakex.flags import FlagsConfig
from pymakex.Helper import Helper

"""
TOOL  CPU
"""

toolpath_armgcc = r"D:\LLVM\arm-none-eabi-gcc14\bin"
toolpath_riscv = r"D:\LLVM\riscv\bin"
tool = "gcc"
# prefix = "arm-none-eabi-"
prefix = ""

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
hlp.Update({"TOOLPATH": toolpath_armgcc, "TOOL": tool, "TOOL_PREFIX": prefix})
# print(TOOL_OF(tool, prefix))

# print(hlp["CFG"])

hlp.Refresh()

# hlp.Action(["echo", "hello world"])
# print(hlp["ACTIONS"])

# print("====== 01 ==========")
# print(hlp.Flags)
# print("====== 01 ==========")

# print("====== 02 ==========")
# print(hlp["DEFINES"])

############
# Parties = Parties("FParties", "src")
# method 1: use helper function Party
# hlp.Party("SRC", "src", macros={"XXXX": "123"})
#
# method 2: use Parties class
# SRC = Parties(
#     "SRC",
#     "src",
#     macros={"XXXX": "123"},
#     params={"yyyy": "456"},
# )
# hlp.Party(**SRC.Dictionary())
############

src2 = hlp.Parties("SRC2", "src2")


# # # target
t = hlp.Program("test")
hlp.DefaultTarget(t)

# mylib = hlp.Library_STATIC("src2")  # 指定party 名称
# hlp.DefaultTarget(mylib)

cmd1 = hlp.Command("CMD1", ["echo hello world"])

# hlp.Phony("ph1", ["test", "src", cmd1])
# hlp.Alias("my", ["test", "src", cmd1])


print("+" * 20)
print(" ")
