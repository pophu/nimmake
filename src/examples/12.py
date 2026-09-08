import os
import sys
from pathlib import Path

__file_dir__ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, __file_dir__)

# from pymakex.builder import Parties
from pymakex.datasets import CORTEX_M3_CFG, CORTEX_M4_CFG, CORTEX_M4_CLANG_CFG, TOOL_OF
from pymakex.flags import FlagsConfig
from pymakex.Helper import Helper

"""
TOOL  CPU   armllvm , target lib
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
CFG = CORTEX_M4_CLANG_CFG.clone()
hlp.Config(CFG)

# hlp.TOML()
hlp.set_cfg("linkscript", "src_stm/STM32F407XX_FLASH.ld")
# sysroot = Path(toolpath).parent / "lib/clang-runtimes/arm-none-eabi/armv7m_hard_fpv4_sp_d16"
# hlp.set_cfg("sysroot", sysroot.as_posix())
# hlp.set_cfg("specs", "")
hlp.set_cfg("abi", "softfp")
hlp.set_cfg("nostdlib", False)
hlp.set_cfg("freestanding", True)
hlp.set_cfg("library_path", "")


############
# TOOL
############
# hlp["TOOLPATH"] = [toolpath2]
# hlp.Append(TOOLPATH=toolpath2)
hlp.Update({"TOOLPATH": toolpath, "TOOL": tool, "TOOL_PREFIX": prefix})
# print(TOOL_OF(tool, prefix))

hlp.Append(LIBS="clang_rt.builtins")
hlp.Append(LIBS="m")
hlp.Append(LIBS="c")

hlp.Append(DEFINES={"XXXX": "123"})

hlp.Refresh()
# Affer Refresh


core = hlp.Parties("CORE", "src_stm/Core")
driver = hlp.Parties(
    "Driver",
    "src_stm/Drivers",
    third_party="HAL",
    build_type="STATIC",
    defines={"STM32F407xx": "", "USE_HAL_DRIVER": ""},
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
srcs = [
    "src_stm/startup_stm32f407xx.s",
    # "src_stm/main.c",
]
t = hlp.Program("test", sources=srcs)
lib = hlp.Library_STATIC("driver")
hlp.DefaultTarget(t)


# mylib = hlp.Library_STATIC("src2")  # 指定party 名称
# hlp.DefaultTarget(mylib)

target_out = hlp.target_out()
bin = hlp.Command("BIN", [hlp.bin_cmd(), hlp.hex_cmd()])
# flash_openocd = 'openocd -f interface/cmsis-dap.cfg -f target/stm32f4x.cfg -c init -c reset -c halt -c "program build/test.bin exit 0x08000000" -c reset -c shutdown'
flash = hlp.Command(
    "FLASH",
    [hlp.open_cmd("daplink", "stm32f4x", 0x08000000)],
)

# hlp.Phony("ph1", ["test", "src", cmd1])
# hlp.Phony("my", ["test", "BIN", "FLASH"])
hlp.Phony("all", [t, bin, flash])
hlp.Phony("flash", [flash])
hlp.Phony("bin", [t, bin])


print("+" * 20)
print(" ")


"""
# ==========================================
# FlagsConfig 配置文件
# 用于配置编译工具链、目标架构及编译链接参数
# ==========================================

# ---- 工具 ----
toolchain = "armllvm"

# ---- 目标 ----
cpu = "cortex-m4"
arch = "armv7e-m"
fpu = "fpv4-sp-d16"
abi = "eabi"
thumb = "yes"
# 支持字符串或字符串数组
model =  "STM32F407"
vendor = "ST"

# ---- 编译 ----
opt = "O2"
dbg = true
warn = "Wall"
std_c = "c99"
std_cxx = "c++11"
data_sections = "yes"
func_sections = "yes"
freestanding = true
no_builtin = false

# ---- C++ 专属 Flags ----
no_rtti = true
no_exceptions = true

# ---- 链接 ----
linkscript = "src_stm/STM32F407VGTX_FLASH.ld"
mmap = ""
gc_sections = true
nostartfiles = false
nostdlib = true
shared = false
library_path = "/path/to/libs"
# specs = "nano.specs"
lto = "thin"
semihost = false
sysroot = ""

# ---- 宏定义 ----
# 键值对形式，对应 dict[str, str]
[defines]
DEBUG = "1"
BOARD_NAME = "\"STM32F407\""
STM32F407xx =""
USE_HAL_DRIVER = ""


hlp.TOML()
hlp.set_cfg("linkscript", "src_stm/STM32F407XX_FLASH.ld")
sysroot = Path(toolpath).parent / "lib/clang-runtimes/arm-none-eabi/armv7m_hard_fpv4_sp_d16"
hlp.set_cfg("sysroot", sysroot.as_posix())
hlp.set_cfg("library_path", "")
LD_PATH=Path(toolpath) / "ld.lld"
hlp.set_cfg("ld_path", LD_PATH.as_posix())

"""
