from nimmake.configs import BuildType
from nimmake.datasets import CORTEX_M4_CLANG_CFG
from nimmake.Helper import Helper, Path

"""
# TOOL ar arm-none-eabi-gcc ALIAS  COMMAND
# add alias command
# add postaction or command
"""

toolpath_armgcc = r"D:\LLVM\arm-none-eabi-gcc14\bin"
toolpath_armllvm = r"D:\LLVM\ETArm\bin"
toolpath_riscv = r"D:\LLVM\riscv\bin"
toolpath = toolpath_armllvm
tool = "clang"
prefix = "arm"

print("== Welcome to Nimmake ARM LLVM! ==")
hlp = Helper()

############
# ACTION COMMAND
############
# CFG = CORTEX_M4_CFG.clone()
CFG = CORTEX_M4_CLANG_CFG.clone()
hlp.Config(CFG)

# hlp.TOML()
hlp.set_cfg("linkscript", "STM32F407XX_FLASH.ld")
sysroot = Path(toolpath).parent / "lib/clang-runtimes/arm-none-eabi/armv7m_hard_fpv4_sp_d16"
hlp.set_cfg("sysroot", sysroot.as_posix())
# hlp.set_cfg("specs", "")
# hlp.set_cfg("abi", "softfp")
hlp.set_cfg("nostdlib", True)
# hlp.set_cfg("freestanding", True)
hlp.set_cfg("library_path", "")

# ############
# # TOOL
# ############
# # hlp["TOOLPATH"] = [toolpath2]
# # hlp.Append(TOOLPATH=toolpath2)
# # hlp.Update({"TOOLPATH": toolpath_armgcc, "TOOL": tool, "TOOL_PREFIX": prefix})
hlp.Update({"TOOLPATH": toolpath, "TOOL": tool, "TOOL_PREFIX": prefix})

hlp.Append(LIBS="clang_rt.builtins")
hlp.Append(LIBS="m")
hlp.Append(LIBS="c")

hlp.Refresh()

# Affer Refresh
PARTY_PARAM = {
    # "CPU": hlp._cfg.cpu,
    # "ABI": hlp._cfg.abi,
    # "FPU": hlp._cfg.fpu,
    # "MODEL": hlp._cfg.model,
}

core = hlp.Parties("CORE", "Core", params=PARTY_PARAM)
driver = hlp.Parties(
    "Driver",
    "Drivers",
    third_party="HAL",
    build_type=BuildType.STATIC.name,
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
    # "1.s",
    # "src_stm/main.c",
]
t = hlp.Program("test", sources=srcs)
hlp.DefaultTarget(t)

mylib = hlp.Library_STATIC("Driver")  # 指定party 名称
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
hlp.Phony("my", ["test", "BIN", "FLASH"])
hlp.Phony("flash", ["FLASH"])


print(hlp.Flags)
