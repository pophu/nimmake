from .chips import _ARCH_SIMPLIFY, CPU_INFO, VENDOR_MODELS, cpu_arch

#
from .presets import (
    CORTEX_M3_CFG,
    CORTEX_M4_ARMLLVM_CFG,
    CORTEX_M4_CFG,
    CORTEX_M4_CLANG_CFG,
    DESK_CLANG_CFG,
    DESK_GCC_CFG,
    RISCV_32_IMAC_CFG,
    RISCV_64_GC_CFG,
)

#
from .presets import get_flags_cfg_by_toolchain_cpu as TOOLCHAIN_CPU_OF

# from .presets import get_flags_cfg_by_vedor_model as VENDOR_MODEL_OF
from .tools import TOOL_CMD_PREFIX
from .tools import tool_suits as TOOL_OF
from .vendor import Vendor
from .vendor import of_vendor_model as VENDOR_MODEL_OF

__all__ = [
    CPU_INFO,
    VENDOR_MODELS,
    cpu_arch,
    _ARCH_SIMPLIFY,
    # tools
    TOOL_CMD_PREFIX,
    TOOL_OF,
    #
    TOOLCHAIN_CPU_OF,
    # VENDOR_MODEL_OF,
    #
    CORTEX_M3_CFG,
    CORTEX_M4_CFG,
    DESK_CLANG_CFG,
    DESK_GCC_CFG,
    CORTEX_M4_CLANG_CFG,
    CORTEX_M4_ARMLLVM_CFG,
    RISCV_32_IMAC_CFG,
    RISCV_64_GC_CFG,
    # vendor
    Vendor,
    VENDOR_MODEL_OF,
]
