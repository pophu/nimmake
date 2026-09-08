from nimmake.datasets import RISCV_32_IMAC_CFG
from nimmake.Helper import Helper

"""
TOOL  CPU. arm-none-eabi-gcc, party_lib
"""

toolpath_armgcc = r"D:\LLVM\arm-none-eabi-gcc14\bin"
toolpath_clang = r"D:\LLVM\ETArm\bin"
toolpath_riscv = r"D:\LLVM\xpack-riscv-none-elf-gcc-15\bin"
tool = "gcc"
prefix = "arm-none-eabi-"
riscv_prefix = "riscv-none-elf-"

ToolChain_armgcc = {"TOOLPATH": toolpath_armgcc, "TOOL": tool, "TOOL_PREFIX": prefix}
ToolChain_armclang = {"TOOLPATH": toolpath_armgcc, "TOOL": "armclang", "TOOL_PREFIX": ""}
ToolChain_gcc = {"TOOLPATH": toolpath_armgcc, "TOOL": tool, "TOOL_PREFIX": ""}
ToolChain_clang = {"TOOLPATH": toolpath_clang, "TOOL": "clang", "TOOL_PREFIX": ""}
ToolChain_riscv = {"TOOLPATH": toolpath_riscv, "TOOL": "gcc", "TOOL_PREFIX": riscv_prefix}
toolchain = ToolChain_riscv

print("== Welcome to  PYMAKEx! ==")
hlp = Helper()

############
# ACTION COMMAND
############
CFG = RISCV_32_IMAC_CFG.clone()
CFG.set("cpu", "rv32imac_zicsr_zifencei")

hlp.Config(CFG)
hlp.set_cfg("linkscript", "LD/Link.ld")
hlp.set_cfg("std_c", "gnu99")

# hlp.TOML()

############
# TOOL
############
# hlp["TOOLPATH"] = [toolpath2]
# hlp.Append(TOOLPATH=toolpath2)
# hlp.Append(DEFINES={"CH32V20x_D6": ""})
hlp.Update(toolchain)
# hlp.Update({"TOOLPATH": toolpath_armgcc, "TOOL": tool, "TOOL_PREFIX": prefix})
# print(TOOL_OF(tool, prefix))

hlp.Refresh()

# Affer Refresh

print(hlp["BUILDDIR"])

hlp.Append(LIBS="m")
hlp.Append(LIBS="c")

PARTY_PARAM = {
    "CPU": hlp._cfg.cpu,
    "ABI": hlp._cfg.abi,
    "FPU": hlp._cfg.fpu,
    "MODEL": hlp._cfg.model,
}

core = hlp.Parties("CORE", "Core", params=PARTY_PARAM)
debug = hlp.Parties("DEBUG", "Debug", params=PARTY_PARAM)
user = hlp.Parties("USER", "User", params=PARTY_PARAM)
driver = hlp.Parties(
    "Driver",
    "Peripheral",
    # defines={"CH32V20x_D6": "", "USE_HAL_DRIVER": ""},
    defines={"CH32V20x_D6": ""},
    params=PARTY_PARAM,
)

core.DependOn([driver, debug, user])
driver.DependOn([core, user])
user.DependOn([core, driver])
debug.DependOn([core, user])


# print(hlp["LIBS"])
# print(core.depends, "======================")
# print(driver.depends, "======================")
# print(driver.defines, "======================")
# print(driver.include_dirs(), "======================")

# # # target
srcs = [
    "Startup/startup_ch32v20x_D6.s",
    # "src_stm/main.c",
]
t = hlp.Program("test", sources=srcs)
lib= hlp.Library_STATIC("driver")
# hlp.DefaultTarget(t)
hlp.DefaultTarget(lib)

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
flash = hlp.Command("FLASH", [f"{flash_openocd}"])

# hlp.Phony("ph1", ["test", "src", cmd1])
hlp.Phony("my", ["test", "BIN", "FLASH"])
hlp.Phony("flash", ["FLASH"])

# hlp.Phony("ph1", ["test", "src", cmd1])
# hlp.Alias("my", ["test", "src", cmd1])

print(hlp.Flags)


"""
nimmake -f Makefile.py

nimmake -l 1

nimmake -c

nimmake --dry-run


nimmake --verbose 1

D:\LLVM\xpack-riscv-none-elf-gcc-15\bin\riscv-none-elf-gcc -c -mabi=ilp32 -mcmodel=medany -march=rv32imac_zicsr -O2 -Wall -g -fdata-sections -ffunction-sections -std=gnu99 -DCH32V20x_D6 -IDebug -IPeripheral/inc -IUser -ICore Core/core_riscv.c -o BUILD/OBJ/CORE/core_riscv.o

D:\LLVM\xpack-riscv-none-elf-gcc-15\bin\riscv-none-elf-as -mabi=ilp32 -march=rv32imac_zicsr Startup/startup_ch32v20x_D6.s -o BUILD/OBJ/\_DEFAULT/startup_ch32v20x_D6.o

riscv-none-elf-gcc -c -mabi=ilp32 -mcmodel=medany -march=rv32imac_zicsr_zifencei -O2 -Wall -g -fdata-sections -ffunction-sections -std=gnu99 -DCH32V20x_D6 -IPeripheral/inc -ICore -IDebug -IUser Peripheral/src/ch32v20x_misc.c -o BUILD/OBJ/DRIVER/ch32v20x_misc.o

D:\LLVM\xpack-riscv-none-elf-gcc-15\bin\riscv-none-elf-gcc -c -mabi=ilp32 -mcmodel=medany -march=rv32imac_zicsr_zifencei Startup/startup_ch32v20x_D6.s -o BUILD/OBJ/\_DEFAULT/startup_ch32v20x_D6.o  
riscv-none-elf-as: unrecognized option `-mcmodel=medany'


D:\LLVM\xpack-riscv-none-elf-gcc-15\bin\riscv-none-elf-gcc -mabi=ilp32 -march=rv32imac_zicsr_zifencei -nostartfiles "-Wl,--gc-sections" "-TLd/Link.ld" -lm -lc -lgcc BUILD/OBJ/CORE/core_riscv.o BUILD/OBJ/DEBUG/debug.o BUILD/OBJ/USER/ch32v20x_it.o BUILD/OBJ/USER/main.o BUILD/OBJ/USER/system_ch32v20x.o BUILD/OBJ/DRIVER/ch32v20x_adc.o BUILD/OBJ/DRIVER/ch32v20x_bkp.o BUILD/OBJ/DRIVER/ch32v20x_can.o BUILD/OBJ/DRIVER/ch32v20x_crc.o BUILD/OBJ/DRIVER/ch32v20x_dbgmcu.o BUILD/OBJ/DRIVER/ch32v20x_dma.o BUILD/OBJ/DRIVER/ch32v20x_exti.o BUILD/OBJ/DRIVER/ch32v20x_flash.o BUILD/OBJ/DRIVER/ch32v20x_gpio.o BUILD/OBJ/DRIVER/ch32v20x_i2c.o BUILD/OBJ/DRIVER/ch32v20x_iwdg.o BUILD/OBJ/DRIVER/ch32v20x_misc.o BUILD/OBJ/DRIVER/ch32v20x_opa.o BUILD/OBJ/DRIVER/ch32v20x_pwr.o BUILD/OBJ/DRIVER/ch32v20x_rcc.o BUILD/OBJ/DRIVER/ch32v20x_rtc.o BUILD/OBJ/DRIVER/ch32v20x_spi.o BUILD/OBJ/DRIVER/ch32v20x_tim.o BUILD/OBJ/DRIVER/ch32v20x_usart.o BUILD/OBJ/DRIVER/ch32v20x_wwdg.o BUILD/OBJ/\_DEFAULT/startup_ch32v20x_D6.o -o BUILD/test.elf

"""
