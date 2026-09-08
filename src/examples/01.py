from pymakex.datasets import CORTEX_M4_CFG, TOOL_OF
from pymakex.Helper import Helper

"""
TOOL  CPU
"""


toolpath_armgcc = r"D:\LLVM\arm-none-eabi-gcc14\bin"
toolpath_riscv = r"D:\LLVM\riscv\bin"
tool = "gcc"
prefix = "arm-none-eabi-"

print("== Welcome to  PYMAKEx! ==")
hlp = Helper()

############
# Flags = FlagsConfig()
# flags to helper
############
CFG = CORTEX_M4_CFG.clone()
hlp.Config(CFG)

# hlp.TOML()

############
# TOOL
############
hlp.Update({"TOOLPATH": toolpath_armgcc, "TOOL": tool, "TOOL_PREFIX": prefix})
print(TOOL_OF(tool, prefix))

print(hlp["CFG"])

hlp.Refresh()

print("====== 01 ==========")
print(hlp.Flags)
print("====== 01 ==========")


print(" ")
