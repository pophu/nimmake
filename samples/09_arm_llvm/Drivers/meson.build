# meson/sources/meson.build
# Source files module
# This module defines all source file lists
# Note: Paths must be relative to the current meson.build location

# # =============================================================================
# # C Application source files
# # =============================================================================
# app_sources = files(
#   'Src/main.c',
#   'Src/stm32f4xx_it.c',
#   'Src/stm32f4xx_hal_msp.c',
#   'Src/sysmem.c',
#   'Src/syscalls.c'
# )

# # =============================================================================
# # C++ Application source files (add your .cpp files here)
# # =============================================================================
# app_cpp_sources = files(
#   # Add C++ source files here, e.g.:
#   # '../../Core/Src/app.cpp',
#   # '../../Core/Src/my_class.cpp'
# )

# =============================================================================
# System file (part of drivers library)
# =============================================================================
# system_stm32f4xx = files('Src/system_stm32f4xx.c')

# =============================================================================
# Assembly files (.s or .S)
# =============================================================================
asm_sources = files(
  '../startup_stm32f407xx.s',
  # Add more assembly files here, e.g.:
  # '../../Core/Src/interrupt_handlers.s',
  # '../../Drivers/asm/context_switch.s'
)

# =============================================================================
# HAL Driver source files
# =============================================================================
driver_sources = files(
  'STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_rcc.c',
  'STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_rcc_ex.c',
  'STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_flash.c',
  'STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_flash_ex.c',
  'STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_flash_ramfunc.c',
  'STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_gpio.c',
  'STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_dma_ex.c',
  'STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_dma.c',
  'STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_pwr.c',
  'STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_pwr_ex.c',
  'STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_cortex.c',
  'STM32F4xx_HAL_Driver/Src/stm32f4xx_hal.c',
  'STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_exti.c'
) + system_stm32f4xx
