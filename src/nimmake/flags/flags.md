## flags

### stm32 GCC (ARM GCC)

**工具链**: `arm-none-eabi-gcc` / `armgcc`

#### 编译命令示例

```bash
# 基本编译 (Cortex-M4, STM32F407)


        Compiling D:\Mycode\STM32_F407_GCC_TPL\FatFs\source\ff.c  ==>>  build\FATFS\ff.o
arm-none-eabi-gcc -o build\FATFS\ff.o -c --std=c99 -mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16 -O2 -Wall -g   -DUSE_HAL_DRIVER -DSTM32F407xx  -I..\..\..\FatFs\source -ICore\Inc -ICommon -I..\..\..\Drivers\STM32F4xx_HAL_Driver\Inc -I..\..\..\Drivers\STM32F4xx_HAL_Driver\Inc\Legacy -I..\..\..\Drivers\CMSIS\Device\ST\STM32F4xx\Include -I..\..\..\Drivers\CMSIS\Include -ICode -I..\..\..\FreeRTOS\Source\include -I..\..\..\FreeRTOS\Source\CMSIS_RTOS_V2 -I..\..\..\FreeRTOS\Source\portable\GCC\ARM_CM4F -IOnChip -IOffChip -IFatfsUSR\usr -IUSBLIB\Class\CDC\Inc -IUSBLIB\Class\MSC\Inc -IUSBLIB\Core\Inc -IUSBMSC\App -IUSBMSC\Target -ISensor -IMenu D:\Mycode\STM32_F407_GCC_TPL\FatFs\source\ff.c

        Linking   ==>>  build\0000_armgcc.elf

arm-none-eabi-g++ -o build\0000_armgcc.elf -mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16 -Wl,--gc-sections -T..\..\..\LinkerScripts\STM32F407ZGTx_FLASH.ld -Wl,-Map=output.map --specs=nano.specs  build\FATFS\diskio.o build\FATFS\ff.o build\FATFS\ff_gen_drv.o build\FATFS\ffsystem.o build\FATFS\ffunicode.o build\CORE\main.o build\CORE\stm32f4xx_hal_msp.o build\CORE\stm32f4xx_it.o build\CORE\system_stm32f4xx.o build\COMMON\delay.o build\COMMON\freertos.o build\COMMON\syscalls.o build\COMMON\sysmem.o build\COMMON\time_manager.o build\COMMON\utils.o build\CODE\ds1302.o build\CODE\gpio.o build\CODE\gpio_def.o build\CODE\irq_handler.o build\CODE\log_stream.o build\CODE\logger_port.o build\CODE\motor.o build\CODE\myprintf.o build\CODE\rtc.o build\CODE\start.o build\CODE\version.o build\ONCHIP\dev_dwt.o build\ONCHIP\dev_systick.o build\ONCHIP\dma.o build\ONCHIP\i2c.o build\ONCHIP\sdio.o build\ONCHIP\spi.o build\ONCHIP\tim.o build\ONCHIP\usart.o build\OFFCHIP\dev_eeprom.o build\OFFCHIP\dev_exti.o build\OFFCHIP\dev_gpio.o build\OFFCHIP\dev_icap.o build\OFFCHIP\dev_iichard.o build\OFFCHIP\dev_iicsoft.o build\OFFCHIP\dev_key.o build\OFFCHIP\dev_led.o build\OFFCHIP\dev_pwm.o build\OFFCHIP\dev_sdio.o build\OFFCHIP\dev_spiflash.o build\OFFCHIP\dev_timer.o build\USBLIB\usbd_msc.o build\USBLIB\usbd_msc_bot.o build\USBLIB\usbd_msc_data.o build\USBLIB\usbd_msc_scsi.o build\USBLIB\usbd_core.o build\USBLIB\usbd_ctlreq.o build\USBLIB\usbd_ioreq.o build\USBMSC\usb_device.o build\USBMSC\usbd_desc.o build\USBMSC\usbd_storage_if.o build\USBMSC\usbd_conf.o build\FATFSUSR\bsp_driver_sd.o build\FATFSUSR\bsp_driver_spi.o build\FATFSUSR\fatfs.o build\FATFSUSR\fatfs_helper.o build\FATFSUSR\fatfs_platform.o build\FATFSUSR\sd_diskio.o build\FATFSUSR\user_diskio.o build\SENSOR\acs.o build\SENSOR\bb3.o build\SENSOR\ctd.o build\SENSOR\kfifo.o build\SENSOR\sc6.o build\SENSOR\sensor.o build\SENSOR\sensor_uart.o build\MENU\menu.o build\MENU\menu_config.o build\MENU\menu_convert.o build\MENU\menu_node_2.o build\MENU\menu_port.o  -Llib  -lm -lc -lnosys -lhal -lfreertos


arm-none-eabi-ar rcs build\lib\libonchip.a build\ONCHIP\dev_dwt.o

arm-none-eabi-gcc -c -mcpu=cortex-m4 -mfpu=fpv4-sp-d16 \
    -mfloat-abi=softfp -mthumb -O2 -g -Wall \
    -std=c11 -fdata-sections -ffunction-sections \
    -DSTM32F407xx -DUSE_HAL_DRIVER \
    -I./include -o main.o main.c

# 调试版本
arm-none-eabi-gcc -c -mcpu=cortex-m4 -mfpu=fpv4-sp-d16 \
    -mfloat-abi=softfp -mthumb -O0 -g3 -Wall -Wextra \
    -std=c11 -DDEBUG -o main.o main.c

# Cortex-M3 (STM32F103)
arm-none-eabi-gcc -c -mcpu=cortex-m3 -mthumb \
    -O2 -g -Wall -std=c11 \
    -DSTM32F103xE -o main.o main.c

# Cortex-M7 (STM32H743)
arm-none-eabi-gcc -c -mcpu=cortex-m7 -mfpu=fpv5-d16 \
    -mfloat-abi=softfp -mthumb -O2 -g -Wall \
    -std=c11 -o main.o main.c
```

#### 汇编编译

```bash
arm-none-eabi-gcc -c -mcpu=cortex-m4 -mfpu=fpv4-sp-d16 \
    -mfloat-abi=softfp -mthumb -x assembler-with-cpp \
    -o startup.o startup.s
```

#### 归档（静态库）

```bash
arm-none-eabi-ar rcs libfoo.a foo1.o foo2.o
```

#### 链接

```bash
arm-none-eabi-gcc -Tstm32f4.ld -Wl,-Map=output.map \
    --specs=nosys.specs -Wl,--gc-sections \
    -nostartfiles -o output.elf main.o libfoo.a \
    -L./lib -lm
```

---

### LLVM

    "asmtype": "gcc",

        Compiling D:\Mycode\STM32_F407_GCC_TPL\FatFs\source\diskio.c  ==>>  build\FATFS\diskio.o

llvm-clang -o build\FATFS\diskio.o -c --std=c99 --target=arm-none-eabi -march=armv7m -mcpu=cortex-m4 -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mlittle-endian -O2 -Wall -g -DUSE_HAL_DRIVER -DSTM32F407xx -I..\..\..\FatFs\source -ICore\Inc -ICommon -I..\..\..\Drivers\STM32F4xx_HAL_Driver\Inc -I..\..\..\Drivers\STM32F4xx_HAL_Driver\Inc\Legacy -I..\..\..\Drivers\CMSIS\Device\ST\STM32F4xx\Include -I..\..\..\Drivers\CMSIS\Include -ICode -I..\..\..\FreeRTOS\Source\include -I..\..\..\FreeRTOS\Source\CMSIS_RTOS_V2 -I..\..\..\FreeRTOS\Source\portable\GCC\ARM_CM4F -IOnChip -IOffChip -IFatfsUSR\usr -IUSBLIB\Class\CDC\Inc -IUSBLIB\Class\MSC\Inc -IUSBLIB\Core\Inc -IUSBMSC\App -IUSBMSC\Target -ISensor -IMenu D:\Mycode\STM32_F407_GCC_TPL\FatFs\source\diskio.c

D:\LLVM\ETArm\bin\llvm-clang.exe --target=arm-none-eabi -march=armv7m -mcpu=cortex-m4 -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mlittle-endian -o build\HAL\startup_stm32f407xx.o D:\Mycode\STM32_F407_GCC_TPL\Drivers\CMSIS\Device\ST\STM32F4xx\Source\Templates\gcc\startup_stm32f407xx.s

出现段错误

llvm-clang++ -o build\0001_llvm_arm.elf --target=arm-none-eabi -march=armv7m -mcpu=cortex-m4 -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mlittle-endian --target=arm-none-eabi -Wl,--gc-sections -TSTM32F407ZGTx_FLASH.ld -L/usr/lib/arm -Wl,-Map=output.map build\FATFS\diskio.o build\FATFS\ff.o build\FATFS\ff_gen_drv.o build\FATFS\ffsystem.o build\FATFS\ffunicode.o build\CORE\main.o build\CORE\stm32f4xx_hal_msp.o build\CORE\stm32f4xx_it.o build\CORE\system_stm32f4xx.o build\COMMON\delay.o build\COMMON\freertos.o build\COMMON\syscalls.o build\COMMON\sysmem.o build\COMMON\time_manager.o build\COMMON\utils.o build\CODE\ds1302.o build\CODE\gpio.o build\CODE\gpio_def.o build\CODE\irq_handler.o build\CODE\log_stream.o build\CODE\logger_port.o build\CODE\motor.o build\CODE\myprintf.o build\CODE\rtc.o build\CODE\start.o build\CODE\stdio_impl.o build\CODE\syscall.o build\CODE\version.o build\ONCHIP\dev_dwt.o build\ONCHIP\dev_systick.o build\ONCHIP\dma.o build\ONCHIP\i2c.o build\ONCHIP\sdio.o build\ONCHIP\spi.o build\ONCHIP\tim.o build\ONCHIP\usart.o build\OFFCHIP\dev_eeprom.o build\OFFCHIP\dev_exti.o build\OFFCHIP\dev_gpio.o build\OFFCHIP\dev_icap.o build\OFFCHIP\dev_iichard.o build\OFFCHIP\dev_iicsoft.o build\OFFCHIP\dev_key.o build\OFFCHIP\dev_led.o build\OFFCHIP\dev_pwm.o build\OFFCHIP\dev_sdio.o build\OFFCHIP\dev_spiflash.o build\OFFCHIP\dev_timer.o build\USBLIB\usbd_msc.o build\USBLIB\usbd_msc_bot.o build\USBLIB\usbd_msc_data.o build\USBLIB\usbd_msc_scsi.o build\USBLIB\usbd_core.o build\USBLIB\usbd_ctlreq.o build\USBLIB\usbd_ioreq.o build\USBMSC\usb_device.o build\USBMSC\usbd_desc.o build\USBMSC\usbd_storage_if.o build\USBMSC\usbd_conf.o build\FATFSUSR\bsp_driver_sd.o build\FATFSUSR\bsp_driver_spi.o build\FATFSUSR\fatfs.o build\FATFSUSR\fatfs_helper.o build\FATFSUSR\fatfs_platform.o build\FATFSUSR\sd_diskio.o build\FATFSUSR\user_diskio.o build\SENSOR\acs.o build\SENSOR\bb3.o build\SENSOR\ctd.o build\SENSOR\kfifo.o build\SENSOR\sc6.o build\SENSOR\sensor.o build\SENSOR\sensor_uart.o build\MENU\menu.o build\MENU\menu_config.o build\MENU\menu_convert.o build\MENU\menu_node_2.o build\MENU\menu_port.o -Llib -lm -lc -lnosys -lhal -lfreertos

LIBS = -lc -lnosys
LIBDIR =
LDFLAGS = $(MCU) -TSTM32F407ZGTx_FLASH.ld $(LIBS) -flto -Os -Wl,--gc-sections -Wl,--print-memory-usage -Wl,--strip-all -Wl,-Map=build/hal_103.map,--cref

### STM32 Clang (ARM Clang)

**工具链**: `clang` / `armclang`  
**目标三元组**: `arm-arm-none-eabi`

```
ifeq ($(COMPILER),ARMCLANG)
PREFIX = C:/Keil_v5/ARM/ARMCLANG/bin/
CC = $(PREFIX)armclang
AS = $(PREFIX)armclang
CP = $(PREFIX)armclang
SZ = $(PREFIX)size
CPP = $(PREFIX)armclang
LD = $(PREFIX)armlink
endif
HEX = $(CP) -O ihex
BIN = $(CP) -O binary -S

# ifdef GCC_PATH
# CC = $(GCC_PATH)/$(PREFIX)gcc
# AS = $(GCC_PATH)/$(PREFIX)g++ -x assembler-with-cpp
# CP = $(GCC_PATH)/$(PREFIX)objcopy
# SZ = $(GCC_PATH)/$(PREFIX)size
# CPP = $(GCC_PATH)/$(PREFIX)g++
# endif

#######################################
# CFLAGS
#######################################
# cpu
CPU = -mcpu=cortex-m4

# fpu
FPU = -mfpu=fpv4-sp-d16

# float-abi
FLOAT-ABI = -mfloat-abi=hard

# mcu
MCU = --target=arm-arm-none-eabi $(CPU) -mthumb $(FPU) $(FLOAT-ABI)

# macros for gcc
# AS defines
AS_DEFS =

# C defines
C_DEFS =  \
-DUSE_HAL_DRIVER \
-DSTM32F407xx


# AS includes
AS_INCLUDES =  \
-ICore/Inc


# compile gcc flags
# ASFLAGS = $(MCU) $(AS_DEFS) $(AS_INCLUDES) $(OPT) -Wall
ASFLAGS =   $(MCU)  -masm=auto -c -gdwarf-3
ASFLAGS +=   $(C_INCLUDES)
# ASFLAGS += -Wa,armasm,--pd,"__UVISION_VERSION SETA 532"

CFLAGS += $(MCU) $(C_DEFS) $(C_INCLUDES) $(OPT) -Wall -fdata-sections -ffunction-sections  -std=c99

ifeq ($(DEBUG), 1)
CFLAGS += -g -gdwarf-2
endif


# Generate dependency information
# CFLAGS += -MMD -MP -MF"$(@:%.o=%.d)"

CFLAGS += -fexec-charset=UTF-8 -finput-charset=UTF-8

# C++ flag
CPP_FLAGS  = $(MCU) $(C_DEFS) $(C_INCLUDES) $(OPT) -Wall -fdata-sections -ffunction-sections  -fno-rtti -fno-exceptions -lstdc++ -std=c++11
LDFLAGS += -Wl,-u_printf_float
# C_DEFS +=    -DUSE_USBD_COMPOSITE   #usbd_conf.h:38:   "USE_USBD_COMPOSITE"

# ASM sources
# ASM_SOURCES =  $(WORKSPACE_DIR)/Startup/startup_stm32f407xx.s
ASM_SOURCES = startup_stm32f407xx_armclang.s   #arm asm style

# link script
LDSCRIPT = $(WORKSPACE_DIR)/LinkerScripts/STM32F407ZGTx_FLASH.ld

# libraries
# LIBS = -lc -lm -lnosys
LIBDIR =
LDFLAGS = $(MCU) -specs=nano.specs -T$(LDSCRIPT) $(LIBDIR) $(LIBS) -Wl,-Map=$(BUILD_DIR)/$(TARGET).map,--cref -Wl,--gc-sections

ifeq ($(COMPILER),ARMCLANG)
# LDFLAGS = $(MCU) -specs=nano.specs  -T$(LDSCRIPT) $(LIBDIR) $(LIBS)
LDFLAGS =  --cpu=Cortex-M4.fp.sp --strict --scatter link.sct --libpath C:\Keil_v5\ARM\ARMCLANG\lib
endif
```

#### 编译命令示例

```bash
# 基本编译 (Cortex-M4)
clang --target=arm-arm-none-eabi -c \
    -mcpu=cortex-m4 -mfpu=fpv4-sp-d16 \
    -mfloat-abi=softfp -mthumb -O2 -g \
    -Wall -std=c11 -fdata-sections -ffunction-sections \
    -DSTM32F407xx -I./include -o main.o main.c

# 优化大小
clang --target=arm-arm-none-eabi -c \
    -mcpu=cortex-m4 -Os -g -DNDEBUG \
    -o main.o main.c

# C++ 编译
clang++ --target=arm-arm-none-eabi -c \
    -mcpu=cortex-m4 -O2 -g -std=c++17 \
    -fno-exceptions -fno-rtti -o app.o app.cpp
```

#### 链接（使用 scatter 文件）

```bash
clang --target=arm-arm-none-eabi \
    --scatter=stm32f4.sct -Wl,-Map=output.map \
    -Wl,--gc-sections -o output.elf main.o
```

或使用链接脚本：

```bash
clang --target=arm-arm-none-eabi \
    -Tstm32f4.ld -Wl,-Map=output.map \
    -o output.elf main.o
```

---

### ARM Clang (通用 ARM Clang)

**工具链**: `llvm-arm` / `ARMClangBackend`

#### 编译命令示例

```bash
# Cortex-M33 (NRF5340)
clang --target=arm-arm-none-eabi -c \
    -mcpu=cortex-m33 -mfpu=fpv5-sp-d16 \
    -mfloat-abi=softfp -mthumb -O2 -g \
    -std=c11 -DNRF5340_XXAA -o main.o main.c

# 无 FPU 配置 (Cortex-M0+)
clang --target=arm-arm-none-eabi -c \
    -mcpu=cortex-m0plus -mthumb -Os -g \
    -std=c11 -o main.o main.c

# 硬浮点 ABI
clang --target=arm-arm-none-eabi -c \
    -mcpu=cortex-m7 -mfpu=fpv5-d16 \
    -mfloat-abi=hard -mthumb -O2 -Ofast \
    -ffp-contract=fast -o math.o math.c
```

#### LTO 链接时优化

```bash
clang --target=arm-arm-none-eabi -flto=thin \
    -Tlinker.ld -Wl,-Map=output.map \
    -o output.elf *.o
```

---

### RISC-V GCC

**工具链**: `riscv64-unknown-elf-gcc` / `riscvgcc`

#### 编译命令示例

```bash
# RV32IMAC (GD32VF103/ESP32-C3)
riscv64-unknown-elf-gcc -c \
    -march=rv32imac -mabi=ilp32 \
    -mcmodel=medany -Os -g \
    -std=c11 -ffreestanding -nostdlib \
    -DGD32VF103xC -o main.o main.c

# RV32IM (基础整数指令集)
riscv64-unknown-elf-gcc -c \
    -march=rv32im -mabi=ilp32 \
    -mcmodel=medany -O2 -g -o main.o main.c

# RV64GC (64位通用)
riscv64-unknown-elf-gcc -c \
    -march=rv64gc -mabi=lp64d \
    -mcmodel=medany -O2 -g \
    -std=c17 -o main.o main.c

# 压缩指令扩展 (RV32IMC)
riscv64-unknown-elf-gcc -c \
    -march=rv32imac_zicsr_zifencei -mabi=ilp32 \
    -mcmodel=medany -Os -o main.o main.c
```

#### 链接（裸机环境）

```bash
riscv64-unknown-elf-gcc -Tgd32vf1.ld \
    -Wl,-Map=output.map -Wl,--gc-sections \
    -nostartfiles -nostdlib \
    -o output.elf main.o startup.o \
    -lgcc -lc_nano -lm
```

#### 使用 sysroot

```bash
riscv64-unknown-elf-gcc --sysroot=/opt/riscv/sysroot \
    -Tlink.ld -o output.elf main.o
```

---

### RISC-V Clang/LLVM

**工具链**: `clang` / `riscvclang`  
**目标三元组**: `riscv32-unknown-elf`

#### 编译命令示例

```bash
# RV32IMAC 基础编译
clang --target=riscv32-unknown-elf -c \
    -march=rv32imac -mabi=ilp32 \
    -O2 -g -std=c11 -o main.o main.c

# RV64GC 64位编译
clang --target=riscv64-unknown-elf -c \
    -march=rv64gc -mabi=lp64d \
    -O2 -g -std=c17 -o main.o main.c

# 扩展指令集 (位操作、压缩等)
clang --target=riscv32-unknown-elf -c \
    -march=rv32imac_zba_zbb_zbc_zbs -mabi=ilp32 \
    -O3 -o crypto.o crypto.c

# 向量扩展 (V扩展，实验性)
clang --target=riscv32-unknown-elf -c \
    -march=rv32imafdv_zvl128b -mabi=ilp32f \
    -O2 -o vector.o vector.c
```

#### 链接

```bash
clang --target=riscv32-unknown-elf \
    -Tlinker.ld -Wl,-Map=output.map \
    -o output.elf main.o
```

---

## 通用选项速查表

| 参数           | 说明               | 示例                         |
| -------------- | ------------------ | ---------------------------- |
| `-mcpu=`       | CPU 型号           | `-mcpu=cortex-m4`            |
| `-march=`      | 架构               | `-march=rv32imac`            |
| `-mabi=`       | ABI                | `-mabi=ilp32`                |
| `-mfpu=`       | FPU 类型           | `-mfpu=fpv4-sp-d16`          |
| `-mfloat-abi=` | 浮点ABI            | `-mfloat-abi=softfp`         |
| `-O<level>`    | 优化级别           | `-O2`, `-Os`, `-O0`          |
| `-g`           | 调试信息           | `-g`, `-g3`                  |
| `-std=`        | 语言标准           | `-std=c11`, `-std=c++17`     |
| `-Wall`        | 启用常用警告       | -                            |
| `-D<macro>`    | 定义宏             | `-DDEBUG`, `-DVERSION=1`     |
| `-I<path>`     | 包含目录           | `-I./include`                |
| `-T<script>`   | 链接脚本           | `-Tstm32f4.ld`               |
| `-Wl,<opt>`    | 链接器选项         | `-Wl,--gc-sections`          |
| `--target=`    | 目标三元组 (Clang) | `--target=arm-arm-none-eabi` |

## 典型工作流示例

### STM32F407 + ARM GCC 完整构建流程

```bash
# 1. 编译源文件
arm-none-eabi-gcc -c -mcpu=cortex-m4 -mfpu=fpv4-sp-d16 \
    -mfloat-abi=softfp -mthumb -O2 -g -Wall \
    -std=c11 -fdata-sections -ffunction-sections \
    -DSTM32F407xx -DUSE_HAL_DRIVER \
    -I./Inc -I./Drivers/CMSIS/Include \
    -I./Drivers/STM32F4xx_HAL_Driver/Inc \
    build/main.o Src/main.c

arm-none-eabi-gcc -c -mcpu=cortex-m4 -mfpu=fpv4-sp-d16 \
    -mfloat-abi=softfp -mthumb -O2 -g \
    build/stup.o Startup/startup_stm32f407xx.s

# 2. 创建静态库（可选）
arm-none-eabi-ar rcs build/libperiph.a build/gpio.o build/uart.o

# 3. 链接
arm-none-eabi-gcc -TSTM32F407ZGTx_FLASH.ld \
    -Wl,-Map=build/output.map --specs=nosys.specs \
    -Wl,--gc-sections -static \
    -Wl,--start-group -lc -lm -Wl,--end-group \
    -o build/output.elf build/main.o build/stup.o \
    build/libperiph.a

# 4. 生成二进制文件
arm-none-eabi-objcopy -O binary -S build/output.elf build/output.bin
arm-none-eabi-objcopy -O ihex -S build/output.elf build/output.hex

# 5. 显示信息
arm-none-eabi-size build/output.elf
arm-none-eabi-readelf -h build/output.elf
```

### RISC-V GD32VF103 完整构建流程

```bash
# 1. 编译
riscv64-unknown-elf-gcc -c \
    -march=rv32imac -mabi=ilp32 \
    -mcmodel=medany -Os -g -std=c11 \
    -ffreestanding -nostdlib \
    -DGD32VF103xC -I./include \
    -o build/main.o src/main.c

# 2. 链接
riscv64-unknown-elf-gcc -TLinkerScript.ld \
    -Wl,-Map=build/output.map \
    -Wl,--gc-sections -nostartfiles -nostdlib \
    -o build/output.elf build/main.o \
    -lgcc -lc_nano -lm

# 3. 生成二进制
riscv64-unknown-elf-objcopy -O binary \
    build/output.elf build/output.bin
```

arm-none-eabi-gcc -o BUILD/test.ELF -Tsrc_stm/STM32F407XX_FLASH.ld -Wl,-Map=build/output.map -Wl,--gc-sections --specs=nosys.specs BUILD/OBJ/CORE/main.o BUILD/OBJ/CORE/stm32f4xx_hal_msp.o BUILD/OBJ/CORE/stm32f4xx_it.o BUILD/OBJ/CORE/syscalls.o BUILD/OBJ/CORE/sysmem.o BUILD/OBJ/CORE/system_stm32f4xx.o BUILD/OBJ/DRIVER/stm32f4xx_hal.o BUILD/OBJ/DRIVER/stm32f4xx_hal_cortex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_dma.o BUILD/OBJ/DRIVER/stm32f4xx_hal_dma_ex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_exti.o BUILD/OBJ/DRIVER/stm32f4xx_hal_flash.o BUILD/OBJ/DRIVER/stm32f4xx_hal_flash_ex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_flash_ramfunc.o BUILD/OBJ/DRIVER/stm32f4xx_hal_gpio.o BUILD/OBJ/DRIVER/stm32f4xx_hal_pwr.o BUILD/OBJ/DRIVER/stm32f4xx_hal_pwr_ex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_rcc.o BUILD/OBJ/DRIVER/stm32f4xx_hal_rcc_ex.o

arm-none-eabi-g++ -o build\0000_armgcc.elf -mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16 -Tsrc_stm/STM32F407XX_FLASH.ld -Wl,-Map=build/output.map -Wl,--gc-sections --specs=nosys.specs BUILD/OBJ/CORE/main.o BUILD/OBJ/CORE/stm32f4xx_hal_msp.o BUILD/OBJ/CORE/stm32f4xx_it.o BUILD/OBJ/CORE/syscalls.o BUILD/OBJ/CORE/sysmem.o BUILD/OBJ/CORE/system_stm32f4xx.o BUILD/OBJ/DRIVER/stm32f4xx_hal.o BUILD/OBJ/DRIVER/stm32f4xx_hal_cortex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_dma.o BUILD/OBJ/DRIVER/stm32f4xx_hal_dma_ex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_exti.o BUILD/OBJ/DRIVER/stm32f4xx_hal_flash.o BUILD/OBJ/DRIVER/stm32f4xx_hal_flash_ex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_flash_ramfunc.o BUILD/OBJ/DRIVER/stm32f4xx_hal_gpio.o BUILD/OBJ/DRIVER/stm32f4xx_hal_pwr.o BUILD/OBJ/DRIVER/stm32f4xx_hal_pwr_ex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_rcc.o BUILD/OBJ/DRIVER/stm32f4xx_hal_rcc_ex.o

arm-none-eabi-gcc -Wl,--gc-sections -Tsrc_stm/STM32F407XX_FLASH.ld --specs=nosys.specs BUILD/OBJ/CORE/main.o BUILD/OBJ/CORE/stm32f4xx_hal_msp.o BUILD/OBJ/CORE/stm32f4xx_it.o BUILD/OBJ/CORE/syscalls.o BUILD/OBJ/CORE/sysmem.o BUILD/OBJ/CORE/system_stm32f4xx.o BUILD/OBJ/DRIVER/stm32f4xx_hal.o BUILD/OBJ/DRIVER/stm32f4xx_hal_cortex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_dma.o BUILD/OBJ/DRIVER/stm32f4xx_hal_dma_ex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_exti.o BUILD/OBJ/DRIVER/stm32f4xx_hal_flash.o BUILD/OBJ/DRIVER/stm32f4xx_hal_flash_ex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_flash_ramfunc.o BUILD/OBJ/DRIVER/stm32f4xx_hal_gpio.o BUILD/OBJ/DRIVER/stm32f4xx_hal_pwr.o BUILD/OBJ/DRIVER/stm32f4xx_hal_pwr_ex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_rcc.o BUILD/OBJ/DRIVER/stm32f4xx_hal_rcc_ex.o -o BUILD/test.ELF

arm-none-eabi-as -c -mcpu=cortex-m4 -mfpu=fpv4-sp-d16 -mfloat-abi=softfp -mthumb -Isrc_stm/Drivers/STM32F4xx_HAL_Driver/Inc -Isrc_stm/Drivers/CMSIS/Include -Isrc_stm/Drivers/STM32F4xx_HAL_Driver/Inc/Legacy -Isrc_stm/Drivers/CMSIS/Device/ST/STM32F4xx/Include -Isrc_stm/Core/Inc -o BUILD/OBJ/DRIVER/startup_stm32f407xx.o src_stm/Drivers/startup_stm32f407xx.s

### arm llvm

LinkerScripts
.ARM.extab (READONLY) : /_ The "READONLY" keyword is only supported in GCC11 and later, remove it if using GCC10 or earlier. _/

READONLY 有影响编译

[INFO] builder.py:231 - clang -c --target=arm-arm-none-eabi -march=armv7e-m -mfpu=fpv4-sp-d16 -mfloat-abi=softfp -mthumb -O2 -Wall -g -fdata-sections -ffunction-sections -ffreestanding -std=c99 -DSTM32F407xx -DUSE_HAL_DRIVER -Isrc_stm/Core/Inc -Isrc_stm/Drivers/CMSIS/Include -Isrc_stm/Drivers/STM32F4xx_HAL_Driver/Inc/Legacy -Isrc_stm/Drivers/STM32F4xx_HAL_Driver/Inc -Isrc_stm/Drivers/CMSIS/Device/ST/STM32F4xx/Include -o BUILD/OBJ/CORE/syscalls.o src_stm/Core/Src/syscalls.c
clang -c --target=arm-arm-none-eabi -march=armv7e-m -mfpu=fpv4-sp-d16 -mfloat-abi=softfp -mthumb -O2 -Wall -g -fdata-sections -ffunction-sections -ffreestanding -std=c99 -DSTM32F407xx -DUSE_HAL_DRIVER -Isrc_stm/Core/Inc -Isrc_stm/Drivers/CMSIS/Include -Isrc_stm/Drivers/STM32F4xx_HAL_Driver/Inc/Legacy -Isrc_stm/Drivers/STM32F4xx_HAL_Driver/Inc -Isrc_stm/Drivers/CMSIS/Device/ST/STM32F4xx/Include -o BUILD/OBJ/CORE/syscalls.o src_stm/Core/Src/main.c

clang -c --target=arm-unknown-none-eabi -march=armv7e-m -mfpu=fpv4-sp-d16 -mfloat-abi=softfp -mthumb -O2 -Wall -g -fdata-sections -ffunction-sections -ffreestanding -std=c99 -DSTM32F407xx -DUSE_HAL_DRIVER -Isrc_stm/Drivers/STM32F4xx_HAL_Driver/Inc -Isrc_stm/Drivers/CMSIS/Device/ST/STM32F4xx/Include -Isrc_stm/Core/Inc -Isrc_stm/Drivers/CMSIS/Include -Isrc_stm/Drivers/STM32F4xx_HAL_Driver/Inc/Legacy -o BUILD/OBJ/CORE/sysmem.o src_stm/Core/Src/sysmem.c

clang --target=arm-arm-none-eabi -mcpu=cortex-m4 -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -fuse-ld=lld -B"D:/LLVM/ETArm/bin" -rtlib=compiler-rt --sysroot=D:/LLVM/ETArm/lib/clang-runtimes/arm-none-eabi/armv7m_hard_fpv4_sp_d16 -Tsrc_stm/STM32F407XX_FLASH.ld -Wl,--gc-sections -flto=thin BUILD/OBJ/CORE/main.o BUILD/OBJ/CORE/stm32f4xx_hal_msp.o BUILD/OBJ/CORE/stm32f4xx_it.o BUILD/OBJ/CORE/syscalls.o BUILD/OBJ/CORE/sysmem.o BUILD/OBJ/CORE/system_stm32f4xx.o BUILD/OBJ/DRIVER/startup_stm32f407xx.o BUILD/OBJ/DRIVER/stm32f4xx_hal.o BUILD/OBJ/DRIVER/stm32f4xx_hal_cortex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_dma.o BUILD/OBJ/DRIVER/stm32f4xx_hal_dma_ex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_exti.o BUILD/OBJ/DRIVER/stm32f4xx_hal_flash.o BUILD/OBJ/DRIVER/stm32f4xx_hal_flash_ex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_flash_ramfunc.o BUILD/OBJ/DRIVER/stm32f4xx_hal_gpio.o BUILD/OBJ/DRIVER/stm32f4xx_hal_pwr.o BUILD/OBJ/DRIVER/stm32f4xx_hal_pwr_ex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_rcc.o BUILD/OBJ/DRIVER/stm32f4xx_hal_rcc_ex.o -lcrt0-semihost -lsemihost -lc -lm -o BUILD/test.elf

-nostdlib

-nostdlib = -nostartfiles + -nodefaultlibs，禁用一切 完全手动控制，需手动加 -lc -lm
-nostartfiles 只跳过 crt0 启动文件，保留 -lc -lm 自动链接 裸机推荐 ✅
-nodefaultlibs 保留启动文件，跳过 -lc -lm 几乎不用

-nostartfiles 会自动从 sysroot 链接 -lc 和 -lm，
-rtlib=compiler-rt 自动链接 libclang_rt.builtins。不需要手动加 -lc -lm。

picolib write / sbrk（无下划线）, newlib 有下划线

-rtlib=compiler-rt 编译器内部函数：**aeabi_uldivmod、**aeabi_uidiv、浮点软模拟等 编译器"自带的工具箱"
摆脱对 GCC 的依赖：在传统的交叉编译环境中，Clang 通常会默认链接 GCC 的 libgcc。使用 -rtlib=compiler-rt 可以让你的工具链完全自包含（Self-contained），不再需要安装或依赖 GNU 的工具链
-lc C 标准库：printf、malloc、memcpy、strcpy 等 你代码里调用的 API
-lm 数学库：sin、cos、sqrt 等 标准库的数学扩展
-lcrt0-semihost 启动文件 + semihosting 入口 程序的"起跑线"
-lsemihost semihosting 系统调用实现
-lclang_rt.builtins-armv7em 替代 -rtlib=compiler-rt

不用 printf/malloc 等 可省-lc
不用 sin/cos 等数学函数 可省-lm
不用 semihosting 调试 -lcrt0-semihost -lsemihost
任何情况下都不能省 -rtlib=compiler-rt

Semihosting = 让 MCU 的 printf 通过调试器显示在 PC 上，而不是走硬件串口。
调试器关了，semihosting 就废了。所以它只适合开发阶段，不适合正式产品。

-B"D:/LLVM/ETArm/bin" → clang 会先去这个目录找 ld.lld / as / lib 等
clang 默认从系统 PATH 或自身安装目录找链接器。你之前遇到 unknown argument: -EL 错误，就是因为 clang 在 PATH 里找到了一个不支持 ARM 的 lld（可能是 MinGW 的），而不是 ETArm 自带的。

-fuse-ld=D:/LLVM/ETArm/bin/ld.lld 直接指定链接器，最精确
--ld-path=D:/LLVM/ETArm/bin/ld.lld 直接指定链接器，精确

_ok_  
-nostdlib -lclang_rt.builtins -lm -lc
--ld-path=D:/LLVM/ETArm/bin/ld.lld
--sysroot=D:/LLVM/ETArm/lib/clang-runtimes/arm-none-eabi/armv7m_hard_fpv4_sp_d16
--sysroot=D:/LLVM/ETArm/bin/clang-runtimes/arm-none-eabi/armv7m_hard_fpv4_sp_d16

hlp.TOML()
hlp.set_cfg("linkscript", "src_stm/STM32F407XX_FLASH.ld")
sysroot = Path(toolpath).parent / "lib/clang-runtimes/arm-none-eabi/armv7m_hard_fpv4_sp_d16"
hlp.set_cfg("sysroot", sysroot.as_posix())
hlp.set_cfg("library_path", "")

D:/LLVM/ETArm/bin/clan --target=arm-arm-none-eabi -mcpu=cortex-m4 -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -fuse-ld=lld -B"D:/LLVM/ETArm/bin" -rtlib=compiler-rt --sysroot=D:/LLVM/ETArm/lib/clang-runtimes/arm-none-eabi/armv7m_hard_fpv4_sp_d16 -Tsrc_stm/STM32F407XX_FLASH.ld -Wl,--gc-sections -flto=thin BUILD/OBJ/CORE/main.o BUILD/OBJ/CORE/stm32f4xx_hal_msp.o BUILD/OBJ/CORE/stm32f4xx_it.o BUILD/OBJ/CORE/syscalls.o BUILD/OBJ/CORE/sysmem.o BUILD/OBJ/CORE/system_stm32f4xx.o BUILD/OBJ/DRIVER/startup_stm32f407xx.o BUILD/OBJ/DRIVER/stm32f4xx_hal.o BUILD/OBJ/DRIVER/stm32f4xx_hal_cortex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_dma.o BUILD/OBJ/DRIVER/stm32f4xx_hal_dma_ex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_exti.o BUILD/OBJ/DRIVER/stm32f4xx_hal_flash.o BUILD/OBJ/DRIVER/stm32f4xx_hal_flash_ex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_flash_ramfunc.o BUILD/OBJ/DRIVER/stm32f4xx_hal_gpio.o BUILD/OBJ/DRIVER/stm32f4xx_hal_pwr.o BUILD/OBJ/DRIVER/stm32f4xx_hal_pwr_ex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_rcc.o BUILD/OBJ/DRIVER/stm32f4xx_hal_rcc_ex.o -lcrt0-semihost -lsemihost -lc -lm -o BUILD/test.elf

D:/LLVM/ETArm/bin/clang --target=arm-arm-none-eabi -march=armv7e-m -mfloat-abi=hard -mthumb --ld-path=D:/LLVM/ETArm/bin/ld.lld --sysroot=D:/LLVM/ETArm/bin/clang-runtimes/arm-none-eabi/armv7m_hard_fpv4_sp_d16 -Tsrc_stm/STM32F407XX_FLASH.ld -nostdlib -Wl,--gc-sections BUILD/OBJ/CORE/main.o BUILD/OBJ/CORE/stm32f4xx_hal_msp.o BUILD/OBJ/CORE/stm32f4xx_it.o BUILD/OBJ/CORE/syscalls.o BUILD/OBJ/CORE/sysmem.o BUILD/OBJ/CORE/system_stm32f4xx.o BUILD/OBJ/DRIVER/startup_stm32f407xx.o BUILD/OBJ/DRIVER/stm32f4xx_hal.o BUILD/OBJ/DRIVER/stm32f4xx_hal_cortex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_dma.o BUILD/OBJ/DRIVER/stm32f4xx_hal_dma_ex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_exti.o BUILD/OBJ/DRIVER/stm32f4xx_hal_flash.o BUILD/OBJ/DRIVER/stm32f4xx_hal_flash_ex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_flash_ramfunc.o BUILD/OBJ/DRIVER/stm32f4xx_hal_gpio.o BUILD/OBJ/DRIVER/stm32f4xx_hal_pwr.o BUILD/OBJ/DRIVER/stm32f4xx_hal_pwr_ex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_rcc.o BUILD/OBJ/DRIVER/stm32f4xx_hal_rcc_ex.o -lc -lm -lclang_rt.builtins -o BUILD/test.elf

--sysroot=D:/LLVM/ETArm/lib/clang-runtimes/arm-none-eabi/armv7m_hard_fpv4_sp_d16
--sysroot=D:/LLVM/ETArm/bin/clang-runtimes/arm-none-eabi/armv7m_hard_fpv4_sp_d16

D:/LLVM/ETArm/bin/clang --target=armv7m-unknown-none-eabi -march=armv7e-m -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb --ld-path=D:/LLVM/ETArm/bin/ld.lld --sysroot=D:/LLVM/ETArm/lib/clang-runtimes/arm-none-eabi/armv7m_hard_fpv4_sp_d16 -Tsrc_stm/STM32F407XX_FLASH.ld -nostdlib -Wl,--gc-sections BUILD/OBJ/CORE/main.o BUILD/OBJ/CORE/stm32f4xx_hal_msp.o BUILD/OBJ/CORE/stm32f4xx_it.o BUILD/OBJ/CORE/system_stm32f4xx.o BUILD/OBJ/CORE/syscalls.o BUILD/OBJ/CORE/sysmem.o BUILD/OBJ/DRIVER/stm32f4xx_hal.o BUILD/OBJ/DRIVER/stm32f4xx_hal_cortex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_dma.o BUILD/OBJ/DRIVER/stm32f4xx_hal_dma_ex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_exti.o BUILD/OBJ/DRIVER/stm32f4xx_hal_flash.o BUILD/OBJ/DRIVER/stm32f4xx_hal_flash_ex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_flash_ramfunc.o BUILD/OBJ/DRIVER/stm32f4xx_hal_gpio.o BUILD/OBJ/DRIVER/stm32f4xx_hal_pwr.o BUILD/OBJ/DRIVER/stm32f4xx_hal_pwr_ex.o BUILD/OBJ/DRIVER/stm32f4xx_hal_rcc.o BUILD/OBJ/DRIVER/stm32f4xx_hal_rcc_ex.o BUILD/OBJ/\_DEFAULT/startup_stm32f407xx.o -lc -lm -lclang_rt.builtins -o BUILD/test.elf

clang -c --target=armv7m-unknown-none-eabi -march=armv7e-m -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -O2 -Wall -g -fdata-sections -ffunction-sections -ffreestanding -std=c99 -DSTM32F407xx -DUSE_HAL_DRIVER -Isrc_stm/Drivers/CMSIS/Device/ST/STM32F4xx/Include -Isrc_stm/Drivers/Drivers/STM32F4xx_HAL_Driver/Inc -Isrc_stm/Core/Inc -Isrc_stm/Drivers/CMSIS/Include -Isrc_stm/Drivers/Drivers/STM32F4xx_HAL_Driver/Legacy/Inc -o BUILD/OBJ/CORE/main.o src_stm/Core/Src/main.c

clang -c --target=arm-unknown-none-eabi -march=armv7e-m -mfpu=fpv4-sp-d16 -mfloat-abi=softfp -mthumb -O2 -Wall -g -fdata-sections -ffunction-sections -ffreestanding -std=c99 -DSTM32F407xx -DUSE_HAL_DRIVER -Isrc_stm/Drivers/STM32F4xx_HAL_Driver/Inc -Isrc_stm/Drivers/CMSIS/Device/ST/STM32F4xx/Include -Isrc_stm/Core/Inc -Isrc_stm/Drivers/CMSIS/Include -Isrc_stm/Drivers/STM32F4xx_HAL_Driver/Inc/Legacy -o BUILD/OBJ/CORE/sysmem.o src_stm/Core/Src/sysmem.c

####

[2/2] - src_stm/Core/Src/sysmem.c
clang -c --target=armv7m-unknown-none-eabi -march=armv7e-m -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -O2 -Wall -g -fdata-sections -ffunction-sections -ffreestanding -std=c99 -DSTM32F407xx -DUSE_HAL_DRIVER -Isrc_stm/Drivers/CMSIS/Device/ST/STM32F4xx/Include -Isrc_stm/Core/Inc -Isrc_stm/Drivers/STM32F4xx_HAL_Driver/Legacy/Inc -Isrc_stm/Drivers/STM32F4xx_HAL_Driver/Inc -Isrc_stm/Drivers/CMSIS/Include -o BUILD/OBJ/CORE/sysmem.o src_stm/Core/Src/sysmem.c

clang -c --target=armv7m-unknown-none-eabi -march=armv7e-m -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -O2 -Wall -g -fdata-sections -ffunction-sections -ffreestanding -std=c99 -DSTM32F407xx -DUSE_HAL_DRIVER -Isrc_stm/Drivers/CMSIS/Device/ST/STM32F4xx/Include -Isrc_stm/Core/Inc -Isrc_stm/Drivers/STM32F4xx_HAL_Driver/Legacy/Inc -Isrc_stm/Drivers/STM32F4xx_HAL_Driver/Inc -Isrc_stm/Drivers/CMSIS/Include -o BUILD/OBJ/CORE/syscalls.o src_stm/Core/Src/syscalls.c

ninja
clang -c --target=armv7m-unknown-none-eabi -march=armv7e-m -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -O2 -Wall -g -fdata-sections -ffunction-sections -ffreestanding -std=c99 -DSTM32F407xx -DUSE_HAL_DRIVER -Isrc_stm/Drivers/STM32F4xx_HAL_Driver/Inc -Isrc_stm/Core/Inc -Isrc_stm/Drivers/STM32F4xx_HAL_Driver/Legacy/Inc -Isrc_stm/Drivers/CMSIS/Include -Isrc_stm/Drivers/CMSIS/Device/ST/STM32F4xx/Include src_stm/Core/Src/syscalls.c -o BUILD/OBJ/CORE/syscalls.o

clang -c --target=armv7m-unknown-none-eabi -march=armv7e-m -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -O2 -Wall -g -fdata-sections -ffunction-sections -ffreestanding -std=c99 -DSTM32F407xx -DUSE_HAL_DRIVER -Isrc_stm/Drivers/STM32F4xx_HAL_Driver/Legacy/Inc -Isrc_stm/Drivers/CMSIS/Include -Isrc_stm/Core/Inc -Isrc_stm/Drivers/CMSIS/Device/ST/STM32F4xx/Include -Isrc_stm/Drivers/STM32F4xx_HAL_Driver/Inc src_stm/Core/Src/main.c -MM -o main.o
