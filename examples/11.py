import os
import sys

__file_dir__ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, __file_dir__)

# from pymakex.builders.builder import Parties
from pymakex.datasets import CORTEX_M3_CFG, CORTEX_M4_CFG, TOOL_OF
from pymakex.flags import FlagsConfig
from pymakex.Helper import Helper

"""
TOOL  CPU
"""


toolpath_armgcc = r"D:\LLVM\arm-none-eabi-gcc14\bin"
toolpath_armllvm = r"D:\LLVM\ETArm\bin"
toolpath_riscv = r"D:\LLVM\riscv\bin"
toolpath = toolpath_armllvm
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

hlp.set_cfg("linkscript", "src_stm/STM32F407XX_FLASH.ld")

############
# TOOL
############
hlp.Update({"TOOLPATH": toolpath, "TOOL": tool, "TOOL_PREFIX": prefix})
# print(TOOL_OF(tool, prefix))

# print(hlp["CFG"])

hlp.Refresh()
# print(hlp.Flags)

core = hlp.Parties("CORE", "src_stm/Core")
driver = hlp.Parties(
    "Driver", "src_stm/Drivers", defines={"STM32F407xx": "", "USE_HAL_DRIVER": ""}
)

core.DependOn(driver)
driver.DependOn(core)
# hlp.DAG()
srcs = [
    "src_stm/startup_stm32f407xx.s",
    # "src_stm/main.c",
]
t = hlp.Program("test", sources=srcs)
hlp.DefaultTarget(t)

cmd1 = hlp.Command("CMD1", ["ECHO hello world"])
hlp.Alias("my", ["test", "CMD1"])

# hlp.Phony("ph1", ["test", "src", cmd1])


print(hlp.Flags)
