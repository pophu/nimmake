# Core/meson.build
# This file acts like a "function" that returns multiple values via variables
# When called via subdir('Core'), these variables become available in parent scope

# =============================================================================
# "Function": get_app_sources() -> returns app_sources
# =============================================================================
app_sources = files(
  'Src/main.c',
  'Src/stm32f4xx_it.c',
  'Src/stm32f4xx_hal_msp.c',
  'Src/sysmem.c',
  'Src/syscalls.c'
)

# =============================================================================
# "Function": get_app_cpp_sources() -> returns app_cpp_sources
# =============================================================================
app_cpp_sources = files(
  # Add C++ source files here, e.g.:
  # 'Src/app.cpp',
  # 'Src/my_class.cpp'
)

# =============================================================================
# "Function": get_system_src() -> returns system_stm32f4xx
# =============================================================================
system_stm32f4xx = files('Src/system_stm32f4xx.c')

# =============================================================================
# "Function": get_asm_sources() -> returns asm_sources
# =============================================================================
asm_sources = files(
  '../startup_stm32f407xx.s',
  # Add more assembly files here, e.g.:
  # 'Src/interrupt_handlers.s',
)

# =============================================================================
# "Function": build_asm_lib() -> returns startup_lib
# =============================================================================
startup_lib = static_library(
  'asm_startup',
  asm_sources,
  c_args: asm_comp_flags
)
