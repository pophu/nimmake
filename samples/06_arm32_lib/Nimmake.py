from nimmake.configs import BuildType

# from pymakex.builder import Parties
from nimmake.datasets import CORTEX_M4_CFG
from nimmake.Helper import Helper

"""
TOOL  CPU. arm-none-eabi-gcc, party_lib
"""

toolpath_armgcc = r"D:\LLVM\arm-none-eabi-gcc14\bin"
toolpath_clang = r"D:\LLVM\ETArm\bin"
toolpath_riscv = r"D:\LLVM\riscv\bin"
tool = "gcc"
prefix = "arm-none-eabi-"
riscv_prefix = "riscv32-unknown-elf"

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
hlp.set_cfg("linkscript", "STM32F407XX_FLASH.ld")

# hlp.TOML()

############
# TOOL
############
# hlp["TOOLPATH"] = [toolpath2]
# hlp.Append(TOOLPATH=toolpath2)
hlp.Update(toolchain)
# hlp.Update({"TOOLPATH": toolpath_armgcc, "TOOL": tool, "TOOL_PREFIX": prefix})
# print(TOOL_OF(tool, prefix))
hlp.Append(LIBPATH="lib")
hlp.Append(LIBS="m")
hlp.Append(LIBS="c")
hlp.Append(LIBS="driver")
hlp.Refresh()

# Affer Refresh


PARTY_PARAM = {
    "CPU": hlp._cfg.cpu,
    "ABI": hlp._cfg.abi,
    "FPU": hlp._cfg.fpu,
    "MODEL": hlp._cfg.model,
}

core = hlp.Parties("CORE", "Core", params=PARTY_PARAM)
driver = hlp.Parties(
    "Driver",
    "Drivers",
    third_party="HAL",
    # build_type=BuildType.STATIC.name,
    build_type=BuildType.HEADER.name,
    defines={"STM32F407xx": "", "USE_HAL_DRIVER": ""},
    params=PARTY_PARAM,
)

core.DependOn(driver)
driver.DependOn(core)

# print(hlp["LIBS"])
# print(core.depends, "======================")
# print(driver.depends, "======================")
# print(driver.defines, "======================")
# print(driver.include_dirs(), "======================")

# # # target
srcs = [
    "startup_stm32f407xx.s",
    # "src_stm/main.c",
]
t = hlp.Program("test", sources=srcs)
hlp.DefaultTarget(t)
# lib = hlp.Library_STATIC("driver")
# hlp.DefaultTarget(lib)


# mylib = hlp.Library_STATIC("src2")  # 指定party 名称
# hlp.DefaultTarget(mylib)

target_out = f"{hlp['BUILDDIR']}/test{hlp['TARGET_SUFFIX']}"
bin = hlp.Command(
    "BIN",
    [
        f"{hlp['OBJCOPY']} -O binary {target_out} build/test.bin",
        f"{hlp['OBJCOPY']} -O ihex  {target_out} build/test.hex",
    ],
)
flash_openocd = 'openocd -f interface/cmsis-dap.cfg -f target/stm32f4x.cfg -c init -c reset -c halt -c "program build/test.bin exit 0x08000000" -c reset -c shutdown'
flash = hlp.Command(
    "FLASH",
    [f"{flash_openocd}"],
)

# hlp.Phony("ph1", ["test", "src", cmd1])
hlp.Phony("all", ["test", "BIN", "FLASH"])
hlp.Phony("flash", [bin.name, flash.name])
hlp.Phony("bin", [bin.name])

# hlp.Phony("ph1", ["test", "src", cmd1])
# hlp.Alias("my", ["test", "src", cmd1])

print(hlp.Flags)
