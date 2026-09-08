import os
import sys
from pathlib import Path

__file_dir__ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, __file_dir__)

# from pymakex.builder import Parties
from pymakex.datasets import CORTEX_M3_CFG, CORTEX_M4_CFG, TOOL_OF
from pymakex.flags import FlagsConfig
from pymakex.Helper import Helper

"""
TOOL  CPU   armclang
"""

toolpath_armgcc = r"D:\LLVM\arm-none-eabi-gcc14\bin"
toolpath_armllvm = r"D:\LLVM\ETArm\bin"
toolpath_riscv = r"D:\LLVM\riscv\bin"
toolpath = toolpath_armllvm
tool = "clang"
prefix = "arm"

print("== Welcome to  PYMAKEx! ==")
hlp = Helper()

############
# ACTION COMMAND
############
CFG = CORTEX_M4_CFG.clone()
hlp.Config(CFG)

# hlp.TOML()
hlp.set_cfg("linkscript", "src_stm/STM32F407XX_FLASH.ld")
# sysroot = Path(toolpath).parent / "lib/clang-runtimes/arm-none-eabi/armv7m_hard_fpv4_sp_d16"
# hlp.set_cfg("sysroot", sysroot.as_posix())
hlp.set_cfg("library_path", "")


############
# TOOL
############
# hlp["TOOLPATH"] = [toolpath2]
# hlp.Append(TOOLPATH=toolpath2)
hlp.Update({"TOOLPATH": toolpath, "TOOL": tool, "TOOL_PREFIX": prefix})
# print(TOOL_OF(tool, prefix))

hlp.Refresh()

# Affer Refresh

hlp.Append(LIBS="clang_rt.builtins")
hlp.Append(LIBS="m")
hlp.Append(LIBS="c")

hlp.Append(DEFINES={"XXXX": "123"})

core = hlp.Parties("CORE", "src_stm/Core")
driver = hlp.Parties(
    "Driver", "src_stm/Drivers", defines={"STM32F407xx": "", "USE_HAL_DRIVER": ""}
)

core.DependOn(driver)
driver.DependOn(core)

print(hlp.Toolchain)
print(hlp.Flags)
# print(hlp["LIBS"])
# print(core.depends, "======================")
# print(driver.depends, "======================")
# print(driver.defines, "======================")
# print(driver.include_dirs(), "======================")
# print(hlp["PARTIES"])

# # # target
t = hlp.Program("test")
hlp.DefaultTarget(t)

# mylib = hlp.Library_STATIC("src2")  # 指定party 名称
# hlp.DefaultTarget(mylib)

cmd1 = hlp.Command("CMD1", ["echo hello world"])

# hlp.Phony("ph1", ["test", "src", cmd1])
hlp.Alias("my", ["test", "CMD1"])


print("+" * 20)
print(" ")


"""

hlp.TOML()
hlp.set_cfg("linkscript", "src_stm/STM32F407XX_FLASH.ld")
sysroot = Path(toolpath).parent / "lib/clang-runtimes/arm-none-eabi/armv7m_hard_fpv4_sp_d16"
hlp.set_cfg("sysroot", sysroot.as_posix())
hlp.set_cfg("library_path", "")
LD_PATH=Path(toolpath) / "ld.lld"
hlp.set_cfg("ld_path", LD_PATH.as_posix())

"""
