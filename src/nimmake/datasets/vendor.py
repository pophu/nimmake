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

from enum import Enum

from nimmake.datasets.presets import (
    CORTEX_M3_CFG,
    CORTEX_M4_CFG,
    CORTEX_M7_CFG,
    CORTEX_M33_CFG,
    DESK_CLANG_CFG,
    DESK_GCC_CFG,
    DESK_MSVC_CFG,
)
from nimmake.datasets.presets_dct import ESP_RISCV_32_IMAC_GCC_DCT
from nimmake.flags.config import FlagsConfig
from nimmake.utils import log

# ===================================================================
# 预设 vendor
# ===================================================================
FLAGS_CFG_VENDOR = {
    "DEFAULT": ["ST", "STMicroelectronics"],
    "STMicroelectronics": ["ST", "STMicroelectronics"],
    "GigaDevice": ["GD", "GigaDevice"],
    "Espressif": ["ESP", "Espressif"],
    "Nordic": ["Nordic"],
    "NXP": ["NXP"],
    "TI": ["TI"],
}


class Vendor(Enum):
    DEFAULT = ("DEFAULT", "Default", "default")
    ST = ("STMicroelectronics", "STM")  # 全名 + 基础配置
    GD = ("GigaDevice", "GD")
    ESP = ("Espressif", "ESP")
    NORDIC = ("Nordic", "NordicSemiconductor")
    NXP = ("NXP", "NXPSemiconductors ")
    TI = ("TI", " TexasInstruments")


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


DAFAULT_DESKTOP = DESK_GCC_CFG.clone().set("vendor", "default")


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
    DAFAULT_DESKTOP,
]


def _resolve_vendor(name: str) -> str:
    """将厂商名或简写解析为全名，大小写不敏感"""
    name_upper = name.upper()
    for v in Vendor:
        if v.name == name_upper:
            return v.value[0]
        for alias in v.value:
            if alias.strip().upper() == name_upper:
                return v.value[0]
    return name


def of_vendor_model(vendor: str | Vendor = "default", model: str = "default"):
    cfg = None
    if isinstance(vendor, Vendor):
        _vendor = vendor.value[0]
    else:
        _vendor = _resolve_vendor(vendor)
    _model = model.upper() if model else "DEFAULT"

    for cfg in FLAGS_CFG_VENDOR_MODEL:
        # print(cfg)
        # print(cfg.vendor)
        # print(cfg.model)
        cfg_model = cfg.model.upper()
        if _vendor == "DEFAULT":
            if cfg_model == _model:
                return cfg
            continue
        if cfg.vendor == _vendor and cfg_model == _model:
            return cfg

    log.error(f"vendor model {vendor} {model} not found")
    return cfg
