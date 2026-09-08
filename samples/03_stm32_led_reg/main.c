// stm32f407
// 1. 使能GPIOE外设时钟
// RCC AHB1外设时钟使能寄存器 (RCC_AHB1ENR) 的基地址为 0x40023800
// GPIOE的使能位为第4位
#define RCC_AHB1ENR (*(volatile unsigned int *)0x40023800)
#define RCC_AHB1ENR_GPIOEEN (1 << 4)

// 2. 配置GPIOE寄存器
// GPIOE基地址为 0x40021000
#define GPIOE_BASE 0x40021000
#define GPIOE_MODER                                                            \
  (*(volatile unsigned int *)(GPIOE_BASE + 0x00)) // 模式寄存器
#define GPIOE_OTYPER                                                           \
  (*(volatile unsigned int *)(GPIOE_BASE + 0x04)) // 输出类型寄存器
#define GPIOE_OSPEEDR                                                          \
  (*(volatile unsigned int *)(GPIOE_BASE + 0x08)) // 输出速度寄存器
#define GPIOE_PUPDR                                                            \
  (*(volatile unsigned int *)(GPIOE_BASE + 0x0C)) // 上下拉寄存器
#define GPIOE_BSRR                                                             \
  (*(volatile unsigned int *)(GPIOE_BASE + 0x18)) // 置位/复位寄存器

void LED_PE10_Init(void) {
  // 1. 使能GPIOE时钟
  RCC_AHB1ENR |= RCC_AHB1ENR_GPIOEEN;

  // 2. 配置PE10为通用输出模式 (MODER[21:20] = 01)
  // 先清除PE10对应的模式位，再设置为01
  GPIOE_MODER &= ~(3 << 20);
  GPIOE_MODER |= (1 << 20);

  // 3. 配置PE10为推挽输出 (OTYPER[10] = 0)
  GPIOE_OTYPER &= ~(1 << 10);

  // 4. 配置PE10为低速输出 (OSPEEDR[21:20] = 00)
  GPIOE_OSPEEDR &= ~(3 << 20);

  // 5. 配置PE10无上下拉电阻 (PUPDR[21:20] = 00)
  GPIOE_PUPDR &= ~(3 << 20);
}

// 点亮LED（假设LED低电平点亮，则复位引脚；若高电平点亮，则置位引脚）
void LED_PE10_On(void) {
  // 向BSRR低16位写1，将PE10置高电平
  GPIOE_BSRR = (1 << 10);
}

// 熄灭LED
void LED_PE10_Off(void) {
  // 向BSRR高16位写1，将PE10复位为低电平
  GPIOE_BSRR = (1 << (10 + 16));
}

int main(void) {
  // 初始化PE10引脚
  LED_PE10_Init();

  // 点亮LED
  LED_PE10_On();

  while (1) {
    for (int i = 0; i < 500000; i++) {
      ;
    }
    // 主循环
  }
}

// 函数为空，目的是为了骗过编译器不报错
void SystemInit(void) {}

/*
##############################################
# 1. 工具链配置
##############################################
PREFIX = arm-none-eabi-
CC     = $(PREFIX)gcc
AS     = $(PREFIX)gcc -x assembler-with-cpp
CP     = $(PREFIX)objcopy
SZ     = $(PREFIX)size

##############################################
# 2. 工程文件配置
##############################################
TARGET = stm32f407_led
BUILD_DIR = build

# C 源文件
C_SOURCES = main.c
# 启动文件 (汇编)
ASM_SOURCES = startup_stm32f407xx.s

##############################################
# 3. 编译与链接标志
##############################################
# 核心编译参数：Cortex-M4内核、Thumb指令集、浮点单元、C99标准
MCU_FLAGS = -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard

# C 编译标志
CFLAGS  = $(MCU_FLAGS)
CFLAGS += -DSTM32F407xx           # 必须定义的芯片宏
CFLAGS += -O0 -g -gdwarf-2        # 调试模式，关闭优化
CFLAGS += -std=c99
CFLAGS += -Wall -fdata-sections -ffunction-sections

# 汇编标志
ASFLAGS = $(MCU_FLAGS) -Wall -fdata-sections -ffunction-sections

# 链接标志
LDFLAGS  = $(MCU_FLAGS)
LDFLAGS += -Tlinker.ld            # 链接脚本路径
LDFLAGS += --specs=nano.specs     # 使用精简版C库(newlib-nano)
LDFLAGS += -Wl,-Map=$(BUILD_DIR)/$(TARGET).map,--cref
LDFLAGS += -Wl,--gc-sections      # 移除未使用的段，减小体积
LDFLAGS += -lm                    # 链接数学库

##############################################
# 4. 构建规则
##############################################
# 生成目标文件列表
OBJECTS = $(addprefix $(BUILD_DIR)/,$(notdir $(C_SOURCES:.c=.o)))
vpath %.c $(sort $(dir $(C_SOURCES)))
OBJECTS += $(addprefix $(BUILD_DIR)/,$(notdir $(ASM_SOURCES:.s=.o)))
vpath %.s $(sort $(dir $(ASM_SOURCES)))

# 默认构建目标
all: $(BUILD_DIR)/$(TARGET).elf $(BUILD_DIR)/$(TARGET).hex
$(BUILD_DIR)/$(TARGET).bin

# 链接生成 ELF
$(BUILD_DIR)/$(TARGET).elf: $(OBJECTS)
        $(CC) $(OBJECTS) $(LDFLAGS) -o $@
        $(SZ) $@

# C文件编译规则
$(BUILD_DIR)/%.o: %.c | $(BUILD_DIR)
        $(CC) -c $(CFLAGS) -Wa,-a,-ad,-alms=$(BUILD_DIR)/$(notdir $(<:.c=.lst))
$< -o $@

# 汇编文件编译规则
$(BUILD_DIR)/%.o: %.s | $(BUILD_DIR)
        $(AS) -c $(ASFLAGS) $< -o $@

# 生成 HEX 和 BIN 文件
$(BUILD_DIR)/%.hex: $(BUILD_DIR)/%.elf
        $(CP) -O ihex $< $@

$(BUILD_DIR)/%.bin: $(BUILD_DIR)/%.elf
        $(CP) -O binary -S $< $@

# 创建构建目录
$(BUILD_DIR):
        mkdir -p $@

# 清理构建文件
clean:
        rm -rf $(BUILD_DIR)

##############################################
# 5. 烧录规则 (可选，需安装OpenOCD或J-Link)
##############################################
flash: $(BUILD_DIR)/$(TARGET).bin
    # 示例：使用 OpenOCD 烧录
        # openocd -f interface/stlink.cfg -f target/stm32f4x.cfg -c "program
$(BUILD_DIR)/$(TARGET).bin verify reset exit 0x08000000" # 示例：使用 J-Link
烧录 # JLinkExe -device STM32F407VG -if SWD -speed 4000 -autoconnect 1
-CommandFile flash.jlink

.PHONY: all clean flash
*/