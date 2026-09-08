from nimmake.datasets import CORTEX_M4_CFG, VENDOR_MODEL_OF, Vendor
from nimmake.Helper import Helper

toolpath_armgcc = r"D:\LLVM\arm-none-eabi-gcc14\bin"
toolpath_riscv = r"D:\LLVM\riscv\bin"
tool = "gcc"
prefix = "arm-none-eabi-"

print("== Welcome to  Nimmake! ==")
hlp = Helper()

############
# Flags = FlagsConfig()
# flags to helper
############
CFG = CORTEX_M4_CFG.clone()
CFG = VENDOR_MODEL_OF(Vendor.ST, "STM32F407")

print("-" * 40)
hlp.Config(CFG)
print("-" * 40)

# hlp.TOML()


############
# TOOL
############
hlp.Update({"TOOLPATH": toolpath_armgcc, "TOOL": tool, "TOOL_PREFIX": prefix})
# print(TOOL_OF(tool, prefix))

# print(hlp["CFG"])

hlp.Refresh()
print("=" * 40)
print(hlp.Flags)
print("=" * 40)
print("*" * 40)
print(hlp.Toolchain)
print("*" * 40)
