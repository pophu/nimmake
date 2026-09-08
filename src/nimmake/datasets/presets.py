# MIT License
#
# Copyright (c) 2026-2036 Pophu and contributors
# https://github.com/pophu/nimmake
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""Presets —  FlagsConfig for common chips and toolchains"""

from __future__ import annotations

import sys
from pathlib import Path

from .presets_dct import (
    # CORTEX_M4_ARMLLVM_DCT,
    CORTEX_M4_CLANG_DCT,
    CORTEX_M4_GCC_DCT,
    DESK_CLANG_DCT,
    DESK_GCC_DCT,
    DESK_MSVC_DCT,
    ESP_RISCV_32_IMAC_GCC_DCT,
    RISCV_32_IMAC_GCC_DCT,
    RISCV_64_GC_GCC_DCT,
)

try:
    # 情况1：作为包导入时（python -m parts.Helper）
    from ..flags import FlagsConfig

    # from ..flags import FlagsConfig, FlagsFactory
    pass
except ImportError:
    # 情况2：直接运行时（python Helper.py）
    parts_dir = Path(__file__).parent.parent  # 找到 parts 目录
    sys.path.insert(0, str(parts_dir))  # 加入搜索路径
    # from flags import FlagsConfig, FlagsFactory  # 绝对导入
    from ..flags import FlagsConfig


# ===================================================================
# 预设 FlagsConfig 实例
# ===================================================================

# --- chip ---
CORTEX_M4_CFG = FlagsConfig.from_dict(CORTEX_M4_GCC_DCT)
CORTEX_M4_CLANG_CFG = FlagsConfig.from_dict(CORTEX_M4_CLANG_DCT)
CORTEX_M4_ARMLLVM_CFG = FlagsConfig.from_dict(CORTEX_M4_CLANG_DCT)
CORTEX_M4_ARMCLANG_CFG = FlagsConfig.from_dict(CORTEX_M4_CLANG_DCT)

CORTEX_M3_CFG = CORTEX_M4_CFG.clone().set("cpu", "cortex-m3").set("fpu", "softfp")

CORTEX_M33_CFG = CORTEX_M4_CFG.clone().set("cpu", "cortex-m33")

CORTEX_M7_CFG = CORTEX_M4_CFG.clone().set("cpu", "cortex-m7")

RISCV_32_IMAC_CFG = FlagsConfig.from_dict(RISCV_32_IMAC_GCC_DCT)
RISCV_64_GC_CFG = FlagsConfig.from_dict(RISCV_64_GC_GCC_DCT)

# XTENSA_CFG = FlagsConfig.from_dict(ESP_RISCV_32_IMAC_DCT).set("vendor", "Espressif")

DESK_GCC_CFG = FlagsConfig.from_dict(DESK_GCC_DCT)
DESK_CLANG_CFG = FlagsConfig.from_dict(DESK_CLANG_DCT)
DESK_MSVC_CFG = FlagsConfig.from_dict(DESK_MSVC_DCT)

# ===================================================================
# 预设 vendor model
# ===================================================================

# --- STM32 ---
STM_F4_CFG = CORTEX_M4_CFG.clone().set("vendor", "STMicroelectronics")
STM_F1_CFG = CORTEX_M3_CFG.clone().set("vendor", "STMicroelectronics")
STM_F7_CFG = CORTEX_M7_CFG.clone().set("vendor", "STMicroelectronics")

STM32F407 = STM_F4_CFG.clone().set("model", "STM32F407")
STM32F103 = STM_F1_CFG.clone().set("model", "STM32F103")
STM32H743 = STM_F7_CFG.clone().set("model", "STM32H743")
STM32G474 = STM_F4_CFG.clone().set("model", "STM32G474")

STM32L476 = STM_F4_CFG.clone().set("model", "STM32G474")

# --- GD32 ---
GD_F4_CFG = CORTEX_M4_CFG.clone().set("vendor", "GigaDevice")
GD_F1_CFG = CORTEX_M33_CFG.clone().set("vendor", "GigaDevice")

GD32F407 = GD_F4_CFG.clone().set("model", "GD32F407")
GD32VF103 = GD_F1_CFG.clone().set("model", "GD32VF103")


# --- ESP32 ---
ESP_C3_CFG = FlagsConfig.from_dict(ESP_RISCV_32_IMAC_GCC_DCT).set("vendor", "Espressif")
ESP_S3_CFG = ESP_C3_CFG.clone().set("cpu", "xtensa").set("opt", "Os")

ESP32C3 = ESP_C3_CFG.clone().set("opt", "Os").set("model", "ESP32C3")
ESP32S3 = ESP_S3_CFG.clone().set("opt", "O2").set("model", "ESP32S3")


# --- NRF ---
NRF_F4_CFG = CORTEX_M4_CFG.clone().set("vendor", "Nordic")
NRF_F33_CFG = CORTEX_M33_CFG.clone().set("vendor", "Nordic")

NRF52840 = NRF_F4_CFG.clone().set("model", "NRF52840").set("linkscript", "nrf52.ld")
NRF5340 = NRF_F33_CFG.clone().set("model", "NRF5340").set("linkscript", "nrf53.ld")


# --- NXP ---
NXP_F7_CFG = CORTEX_M7_CFG.clone().set("vendor", "NXP")
MIMXRT1062 = NXP_F7_CFG.clone().set("model", "MIMXRT1062").set("linkscript", "imxrt1062.ld")


# --- TI ---
TI_F4_CFG = CORTEX_M4_CFG.clone().set("vendor", "TI")

TM4C129 = TI_F4_CFG.clone().set("model", "TM4C129").set("linkscript", "tm4c129.ld")


# --- 桌面 ---

DESKTOP_GCC_X86 = DESK_GCC_CFG.clone().set("arch", "x86-64")
DESKTOP_CLANG_X86 = DESK_CLANG_CFG.clone().set("arch", "x86-64")
DESKTOP_MSVC_X86 = DESK_MSVC_CFG.clone().set("arch", "x86-64")


# ===================================================================
# 预设 chip
# ===================================================================

FLAGS_CFG_BY_CHIP = [
    CORTEX_M4_CFG,
    CORTEX_M3_CFG,
    CORTEX_M33_CFG,
    CORTEX_M7_CFG,
    #
    RISCV_32_IMAC_CFG,
    RISCV_64_GC_CFG,
    # XTENSA
    #
    DESK_GCC_CFG,
    DESK_CLANG_CFG,
    DESK_MSVC_CFG,
]

# ===================================================================
# 预设 vendor model
# ===================================================================

FLAGS_CFG_VENDOR_MODEL = [
    # --- STM32 ---
    STM_F4_CFG,
    STM_F1_CFG,
    STM_F7_CFG,
    STM32F407,
    STM32F103,
    STM32H743,
    STM32G474,
    STM32L476,
    # --- GD32 ---
    GD_F4_CFG,
    GD_F1_CFG,
    GD32F407,
    GD32VF103,
    # --- ESP32 ---
    ESP_C3_CFG,
    ESP_S3_CFG,
    ESP32C3,
    ESP32S3,
    # --- NRF ---
    NRF_F4_CFG,
    NRF_F33_CFG,
    NRF52840,
    NRF5340,
    # --- NXP ---
    NXP_F7_CFG,
    MIMXRT1062,
    # --- TI ---
    TI_F4_CFG,
    TM4C129,
    # --- 桌面 ---
    DESKTOP_GCC_X86,
    DESKTOP_CLANG_X86,
    DESKTOP_MSVC_X86,
]


def get_flags_cfg(toolchain: str, vendor: str, model: str, cpu: str) -> FlagsConfig:
    """根据工具链获取预设配置"""
    if toolchain == "armgcc":
        return STM32F407
    elif toolchain == "riscvgcc":
        return RISCV_32_IMAC_CFG
    else:
        raise ValueError(f"Unknown toolchain: {toolchain}")


def get_flags_cfg_by_toolchain_cpu(toolchain: str, cpu: str) -> FlagsConfig:
    """根据工具链获取预设配置"""
    if "gcc" not in toolchain and "clang" not in toolchain:
        return None
    if "gcc" in toolchain:
        for cfg in FLAGS_CFG_BY_CHIP:
            if cpu in cfg.cpu:
                return cfg
    if "clang" in toolchain:
        for cfg in FLAGS_CFG_BY_CHIP:
            if cpu in cfg.cpu:
                return cfg
    return None


def get_flags_cfg_by_vedor_model(vendor: str, model: str) -> FlagsConfig:
    """根据工具链获取预设配置"""
    cfg = None
    for cfg in FLAGS_CFG_VENDOR_MODEL:
        if vendor in cfg.vendor and model in cfg.model:
            return cfg
    return cfg


# # ===================================================================
# # 快速构建函数
# # ===================================================================


# def _make(toolchain: str, cfg: FlagsConfig, **overrides) -> FlagsFactory:
#     """从预设配置创建工厂，支持覆盖部分参数"""
#     if overrides:
#         cfg = cfg.clone()
#         for k, v in overrides.items():
#             if hasattr(cfg, k):
#                 setattr(cfg, k, v)
#     return FlagsFactory.from_config(toolchain, cfg)


# def flags_make(toolchain: str, cfg: FlagsConfig, **overrides) -> FlagsFactory:
#     """从预设配置创建工厂，支持覆盖部分参数"""
#     if overrides:
#         cfg = cfg.clone()
#         for k, v in overrides.items():
#             if hasattr(cfg, k):
#                 setattr(cfg, k, v)
#     return FlagsFactory.from_config(toolchain, cfg)


# def stm32f407(
#     toolchain: str = "armgcc",
#     *,
#     opt: str | None = None,
#     dbg: bool | None = None,
#     **kw,
# ) -> FlagsFactory:
#     """STM32F407 (Cortex-M4)"""
#     overrides = {}
#     if opt is not None:
#         overrides["opt"] = opt
#     if dbg is not None:
#         overrides["dbg"] = dbg
#     overrides.update(kw)
#     return _make(toolchain, STM32F407, **overrides)


# def stm32f103(
#     toolchain: str = "armgcc",
#     *,
#     opt: str | None = None,
#     dbg: bool | None = None,
#     **kw,
# ) -> FlagsFactory:
#     """STM32F103 (Cortex-M3)"""
#     overrides = {}
#     if opt is not None:
#         overrides["opt"] = opt
#     if dbg is not None:
#         overrides["dbg"] = dbg
#     overrides.update(kw)
#     return _make(toolchain, STM32F103, **overrides)


# def stm32h743(
#     toolchain: str = "armgcc",
#     *,
#     opt: str | None = None,
#     dbg: bool | None = None,
#     **kw,
# ) -> FlagsFactory:
#     """STM32H743 (Cortex-M7)"""
#     overrides = {}
#     if opt is not None:
#         overrides["opt"] = opt
#     if dbg is not None:
#         overrides["dbg"] = dbg
#     overrides.update(kw)
#     return _make(toolchain, STM32H743, **overrides)


# def gd32vf103(
#     toolchain: str = "riscvgcc",
#     *,
#     opt: str | None = None,
#     dbg: bool | None = None,
#     **kw,
# ) -> FlagsFactory:
#     """GD32VF103 (RISC-V)"""
#     overrides = {}
#     if opt is not None:
#         overrides["opt"] = opt
#     if dbg is not None:
#         overrides["dbg"] = dbg
#     overrides.update(kw)
#     return _make(toolchain, GD32VF103, **overrides)


# def esp32c3(
#     toolchain: str = "riscvgcc",
#     *,
#     opt: str | None = None,
#     dbg: bool | None = None,
#     **kw,
# ) -> FlagsFactory:
#     """ESP32-C3 (RISC-V)"""
#     overrides = {}
#     if opt is not None:
#         overrides["opt"] = opt
#     if dbg is not None:
#         overrides["dbg"] = dbg
#     overrides.update(kw)
#     return _make(toolchain, ESP32C3, **overrides)


# def nrf52840(
#     toolchain: str = "armgcc",
#     *,
#     opt: str | None = None,
#     dbg: bool | None = None,
#     **kw,
# ) -> FlagsFactory:
#     """NRF52840 (Cortex-M4)"""
#     overrides = {}
#     if opt is not None:
#         overrides["opt"] = opt
#     if dbg is not None:
#         overrides["dbg"] = dbg
#     overrides.update(kw)
#     return _make(toolchain, NRF52840, **overrides)
