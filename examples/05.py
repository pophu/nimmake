import os
import sys

__file_dir__ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, __file_dir__)

# from pymakex.builder import Parties
from pymakex.datasets import CORTEX_M3_CFG, CORTEX_M4_CFG, TOOL_OF
from pymakex.flags import FlagsConfig
from pymakex.Helper import Helper

"""
# TOOL ar arm-none-eabi-gcc ALIAS  COMMAND
# add alias command
# add postaction or command
"""

toolpath_armgcc = r"D:\LLVM\arm-none-eabi-gcc14\bin"
toolpath_riscv = r"D:\LLVM\riscv\bin"
tool = "gcc"
prefix = "arm-none-eabi-"


print("== Welcome to  PYMAKEx! ==")
hlp = Helper()

############
# ACTION COMMAND
############
CFG = CORTEX_M4_CFG.clone()
hlp.Config(CFG)

# hlp.TOML()
hlp.set_cfg("linkscript", "src_stm/STM32F407XX_FLASH.ld")
hlp.set_cfg("nostdlib", False)
hlp.set_cfg("lto", None)

############
# TOOL
############
# hlp["TOOLPATH"] = [toolpath2]
# hlp.Append(TOOLPATH=toolpath2)
hlp.Update({"TOOLPATH": toolpath_armgcc, "TOOL": tool, "TOOL_PREFIX": prefix})
# print(TOOL_OF(tool, prefix))

hlp.Refresh()

# Affer Refresh

hlp.Append(LIBS="m")
hlp.Append(LIBS="c")
hlp.Append(DEFINES={"XXXX": "123"})

core = hlp.Parties("CORE", "src_stm/Core")
driver = hlp.Parties(
    "Driver", "src_stm/Drivers", defines={"STM32F407xx": "", "USE_HAL_DRIVER": ""}
)

core.DependOn(driver)
driver.DependOn(core)


print(hlp.Flags)
# print(hlp["LIBS"])
# print(core.depends, "======================")
# print(driver.depends, "======================")
# print(driver.defines, "======================")
# print(driver.include_dirs(), "======================")

# # print(hlp["PARTIES"])

# # # target
srcs = [
    "src_stm/startup_stm32f407xx.s",
    # "src_stm/main.c",
]
t = hlp.Program("test", sources=srcs)
hlp.DefaultTarget(t)


# print(hlp["PARTIES"], "0000")
# print(main.srcs, 111)


# mylib = hlp.Library_STATIC("src2")  # 指定party 名称
# hlp.DefaultTarget(mylib)

target = f"{hlp['BUILDDIR']}/test{hlp['TARGET_SUFFIX']}"
bin = hlp.Command(
    "BIN",
    [
        f"{hlp['SIZE']} {target}",
        f"{hlp['OBJCOPY']} -O binary {target} build/test.bin",
        f"{hlp['OBJCOPY']} -O ihex  {target} build/test.hex",
    ],
)
flash_openocd = 'openocd -f interface/cmsis-dap.cfg -f target/stm32f4x.cfg -c init -c reset -c halt -c  "program build/test.bin exit 0x08000000" -c reset -c shutdown'
flash = hlp.Command(
    "FLASH",
    [f"{flash_openocd}"],
)

# hlp.Phony("ph1", ["test", "src", cmd1])
hlp.Alias("my", ["test", "BIN", "FLASH"])


print("+" * 20)
print(" ")

"""
# ==========================================
# FlagsConfig 配置文件
# 用于配置编译工具链、目标架构及编译链接参数
# ==========================================

# ---- 工具 ----
toolchain = "arm-none-eabi"

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
linkscript = "STM32F407VGTX_FLASH.ld"
mmap = ""
gc_sections = true
nostartfiles = false
nostdlib = false
shared = false
library_path = "/path/to/libs"
specs = "nano.specs"
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

CFLAGS: ['-mcpu=cortex-m4', '-mfpu=fpv4-sp-d16', '-mfloat-abi=softfp', '-mthumb', '-O2', '-Wall', '-g', '-fdata-sections', '-ffunction-sections', '-ffreestanding', '-std=c99']
CXXFLAGS: ['-mcpu=cortex-m4', '-mfpu=fpv4-sp-d16', '-mfloat-abi=softfp', '-mthumb', '-O2', '-Wall', '-g', '-fdata-sections', '-ffunction-sections', '-ffreestanding', '-std=c++11', '-fno-rtti', '-fno-exceptions']
ASFLAGS: ['-mcpu=cortex-m4', '-mfpu=fpv4-sp-d16', '-mfloat-abi=softfp', '-mthumb']
ARFLAGS: ['rcs']
LINKFLAGS: ['-Wl,--gc-sections', '-Tsrc_stm/STM32F407XX_FLASH.ld', '-flto=thin', '-L/path/to/libs', '--specs=nano.specs']
DEFINES: {'DEBUG': '1', 'BOARD_NAME': '"STM32F407"', 'STM32F407xx': '', 'USE_HAL_DRIVER': '', 'XXXX': '123'}
"""
