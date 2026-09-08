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


"""
chips — chip / vendor models database
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# 厂商型号 → CPU（按厂商分组）
# ---------------------------------------------------------------------------

VENDOR_MODELS: dict[str, dict[str, str]] = {
    "STMicroelectronics": {
        # STM32 F0 (Cortex-M0)
        "STM32F030": "cortex-m0",
        "STM32F031": "cortex-m0",
        "STM32F042": "cortex-m0",
        "STM32F051": "cortex-m0",
        "STM32F070": "cortex-m0",
        "STM32F072": "cortex-m0",
        "STM32F091": "cortex-m0",
        "STM32F098": "cortex-m0",
        # STM32 F1 (Cortex-M3)
        "STM32F103": "cortex-m3",
        "STM32F107": "cortex-m3",
        # STM32 F2 (Cortex-M3)
        "STM32F205": "cortex-m3",
        "STM32F207": "cortex-m3",
        # STM32 F3 (Cortex-M4)
        "STM32F302": "cortex-m4",
        "STM32F303": "cortex-m4",
        "STM32F334": "cortex-m4",
        "STM32F372": "cortex-m4",
        "STM32F373": "cortex-m4",
        # STM32 F4 (Cortex-M4)
        "STM32F401": "cortex-m4",
        "STM32F405": "cortex-m4",
        "STM32F407": "cortex-m4",
        "STM32F410": "cortex-m4",
        "STM32F411": "cortex-m4",
        "STM32F412": "cortex-m4",
        "STM32F413": "cortex-m4",
        "STM32F423": "cortex-m4",
        "STM32F427": "cortex-m4",
        "STM32F429": "cortex-m4",
        "STM32F437": "cortex-m4",
        "STM32F439": "cortex-m4",
        "STM32F446": "cortex-m4",
        "STM32F469": "cortex-m4",
        # STM32 F7 (Cortex-M7)
        "STM32F722": "cortex-m7",
        "STM32F723": "cortex-m7",
        "STM32F732": "cortex-m7",
        "STM32F733": "cortex-m7",
        "STM32F745": "cortex-m7",
        "STM32F746": "cortex-m7",
        "STM32F756": "cortex-m7",
        "STM32F765": "cortex-m7",
        "STM32F767": "cortex-m7",
        "STM32F769": "cortex-m7",
        "STM32F777": "cortex-m7",
        "STM32F778": "cortex-m7",
        "STM32F779": "cortex-m7",
        # STM32 G0 (Cortex-M0plus)
        "STM32G031": "cortex-m0plus",
        "STM32G041": "cortex-m0plus",
        "STM32G070": "cortex-m0plus",
        "STM32G071": "cortex-m0plus",
        "STM32G081": "cortex-m0plus",
        # STM32 G4 (Cortex-M4)
        "STM32G431": "cortex-m4",
        "STM32G441": "cortex-m4",
        "STM32G471": "cortex-m4",
        "STM32G473": "cortex-m4",
        "STM32G474": "cortex-m4",
        "STM32G483": "cortex-m4",
        "STM32G484": "cortex-m4",
        "STM32G491": "cortex-m4",
        # STM32 H7 (Cortex-M7)
        "STM32H723": "cortex-m7",
        "STM32H725": "cortex-m7",
        "STM32H730": "cortex-m7",
        "STM32H733": "cortex-m7",
        "STM32H735": "cortex-m7",
        "STM32H742": "cortex-m7",
        "STM32H743": "cortex-m7",
        "STM32H745": "cortex-m7",
        "STM32H747": "cortex-m7",
        "STM32H750": "cortex-m7",
        "STM32H753": "cortex-m7",
        "STM32H755": "cortex-m7",
        "STM32H757": "cortex-m7",
        # STM32 L0 (Cortex-M0plus)
        "STM32L010": "cortex-m0plus",
        "STM32L011": "cortex-m0plus",
        "STM32L021": "cortex-m0plus",
        "STM32L031": "cortex-m0plus",
        "STM32L041": "cortex-m0plus",
        "STM32L051": "cortex-m0plus",
        "STM32L052": "cortex-m0plus",
        "STM32L053": "cortex-m0plus",
        "STM32L062": "cortex-m0plus",
        "STM32L063": "cortex-m0plus",
        "STM32L071": "cortex-m0plus",
        "STM32L072": "cortex-m0plus",
        "STM32L073": "cortex-m0plus",
        "STM32L081": "cortex-m0plus",
        "STM32L082": "cortex-m0plus",
        "STM32L083": "cortex-m0plus",
        # STM32 L1 (Cortex-M3)
        "STM32L100": "cortex-m3",
        "STM32L151": "cortex-m3",
        "STM32L152": "cortex-m3",
        "STM32L162": "cortex-m3",
        # STM32 L4 (Cortex-M4)
        "STM32L412": "cortex-m4",
        "STM32L422": "cortex-m4",
        "STM32L431": "cortex-m4",
        "STM32L432": "cortex-m4",
        "STM32L433": "cortex-m4",
        "STM32L442": "cortex-m4",
        "STM32L443": "cortex-m4",
        "STM32L451": "cortex-m4",
        "STM32L452": "cortex-m4",
        "STM32L462": "cortex-m4",
        "STM32L471": "cortex-m4",
        "STM32L475": "cortex-m4",
        "STM32L476": "cortex-m4",
        "STM32L486": "cortex-m4",
        "STM32L496": "cortex-m4",
        "STM32L4A6": "cortex-m4",
        # STM32 L5 (Cortex-M33)
        "STM32L552": "cortex-m33",
        "STM32L562": "cortex-m33",
        # STM32 U5 (Cortex-M33)
        "STM32U575": "cortex-m33",
        "STM32U585": "cortex-m33",
        # STM32 WB (Cortex-M4)
        "STM32WB15": "cortex-m4",
        "STM32WB35": "cortex-m4",
        "STM32WB55": "cortex-m4",
        # STM32 WL (Cortex-M4)
        "STM32WL54": "cortex-m4",
        "STM32WL55": "cortex-m4",
    },
    "GigaDevice": {
        "GD32VF103": "rv32imac",
        "GD32F130": "cortex-m3",
        "GD32F150": "cortex-m3",
        "GD32F170": "cortex-m4",
        "GD32F190": "cortex-m4",
        "GD32F303": "cortex-m4",
        "GD32F305": "cortex-m4",
        "GD32F307": "cortex-m4",
        "GD32F330": "cortex-m4",
        "GD32F350": "cortex-m4",
        "GD32F403": "cortex-m4",
        "GD32F405": "cortex-m4",
        "GD32F407": "cortex-m4",
        "GD32F450": "cortex-m4",
        "GD32F470": "cortex-m4",
    },
    "Espressif": {
        "ESP32": "xtensa",
        "ESP32S2": "xtensa",
        "ESP32S3": "xtensa",
        "ESP32C2": "rv32imc",
        "ESP32C3": "rv32imc",
        "ESP32C5": "rv32imac",
        "ESP32C6": "rv32imac",
        "ESP32H2": "rv32imac",
        "ESP32P4": "rv32imac",
    },
    "Nordic": {
        "NRF51": "cortex-m0",
        "NRF52": "cortex-m4",
        "NRF53": "cortex-m33",
        "NRF91": "cortex-m33",
    },
    "NXP": {
        "MIMXRT1011": "cortex-m7",
        "MIMXRT1021": "cortex-m7",
        "MIMXRT1052": "cortex-m7",
        "MIMXRT1062": "cortex-m7",
        "MIMXRT1064": "cortex-m7",
        "MIMXRT1176": "cortex-m7",
        "LPC1114": "cortex-m0",
        "LPC1768": "cortex-m3",
        "LPC54606": "cortex-m4",
    },
    "TI": {
        "TM4C123": "cortex-m4",
        "TM4C129": "cortex-m4",
        "CC2650": "cortex-m3",
        "CC3220": "cortex-m4",
    },
    "Bouffalo": {
        "BL602": "rv32imc",
        "BL702": "rv32imc",
    },
    "Kendryte": {
        "K210": "rv64gc",
    },
    "WCH": {
        "CH32V003": "rv32ec",
        "CH32V103": "rv32imac",
        "CH32V203": "rv32imac",
        "CH32V303": "rv32imafc",
    },
}

_VENDOR_FLAT: dict[str, str] | None = None


def _build_flat() -> dict[str, str]:
    """将嵌套的 VENDOR_MODELS 展平为 {model: cpu}"""
    flat: dict[str, str] = {}
    for models in VENDOR_MODELS.values():
        flat.update(models)
    return flat


def chip_by_model(model: str) -> str | None:
    """根据厂商型号返回 CPU 名称"""
    global _VENDOR_FLAT
    if _VENDOR_FLAT is None:
        _VENDOR_FLAT = _build_flat()
    return _VENDOR_FLAT.get(model.upper())


def chips_by_vendor(vendor: str) -> dict[str, str]:
    """返回指定厂商的所有型号映射 {model: cpu}"""
    key = vendor.lower()
    for v, models in VENDOR_MODELS.items():
        if v.lower() == key:
            return dict(models)
    return {}


def vendor_of_model(model: str) -> str | None:
    """返回型号所属的厂商名称"""
    upper = model.upper()
    for vendor, models in VENDOR_MODELS.items():
        if upper in models:
            return vendor
    return None


# ---------------------------------------------------------------------------
# CPU → 架构 / FPU / ABI ,
# none soft,  fpv4-sp-d16  hard ,  fpv4-sp-d16 softfp
# fpu ：默认是否硬浮点  abi : 启用哪种 soft softfp  hard
# ---------------------------------------------------------------------------

CPU_INFO: dict[str, dict] = {
    # ARM Cortex-M
    "cortex-m0": {"arch": "armv6s-m", "fpu": None, "default_fpu": "soft"},
    "cortex-m0plus": {"arch": "armv6s-m", "fpu": None, "default_fpu": "soft"},
    "cortex-m1": {"arch": "armv6s-m", "fpu": None, "default_fpu": "soft"},
    "cortex-m3": {"arch": "armv7-m", "fpu": None, "default_fpu": "soft"},
    "cortex-m4": {"arch": "armv7e-m", "fpu": "fpv4-sp-d16", "default_fpu": "softfp"},
    "cortex-m7": {"arch": "armv7e-m", "fpu": "fpv5-d16", "default_fpu": "softfp"},
    "cortex-m23": {"arch": "armv8-m.base", "fpu": None, "default_fpu": "soft"},
    "cortex-m33": {"arch": "armv8-m.main", "fpu": "fpv5-sp-d16", "default_fpu": "softfp"},
    "cortex-m35p": {"arch": "armv8-m.main", "fpu": "fpv5-sp-d16", "default_fpu": "softfp"},
    "cortex-m55": {"arch": "armv8.1-m.main", "fpu": "fpv5-d16", "default_fpu": "softfp"},
    "cortex-m85": {"arch": "armv8.1-m.main", "fpu": "fpv5-d16", "default_fpu": "softfp"},
    # ARM Cortex-A
    "cortex-a7": {"arch": "armv7ve", "fpu": "neon-vfpv4", "default_fpu": "hard"},
    "cortex-a9": {"arch": "armv7-a", "fpu": "neon-fp16", "default_fpu": "hard"},
    "cortex-a53": {"arch": "armv8-a", "fpu": "neon-fp-armv8", "default_fpu": "hard"},
    "cortex-a72": {"arch": "armv8-a", "fpu": "neon-fp-armv8", "default_fpu": "hard"},
    # RISC-V
    # "rv32imac": {"arch": "rv32imac", "abi": "ilp32", "default_fpu": "soft"},
    # "rv32imafc": {"arch": "rv32imafc", "abi": "ilp32f", "default_fpu": "soft"},
    # "rv32imafdc": {"arch": "rv32imafdc", "abi": "ilp32d", "default_fpu": "soft"},
    # "rv64gc": {"arch": "rv64gc", "abi": "lp64d", "default_fpu": "hard"},
    # RISC-V 常见架构配置补充
    # --- 32位架构 (RV32) ---
    # 基础指令集 (仅包含最基本的整数运算，通常用于极简微控制器)
    "rv32i": {"arch": "rv32i", "abi": "ilp32", "default_fpu": "soft"},
    # 基础 + 乘除法 + 压缩指令 (常见的极简配置，无原子操作)
    "rv32imc": {"arch": "rv32imc", "abi": "ilp32", "default_fpu": "soft"},
    # 基础 + 乘除法 + 原子 + 压缩指令 (您提供的常见MCU配置，如 GD32VF103)
    "rv32imac": {"arch": "rv32imac", "abi": "ilp32", "default_fpu": "soft"},
    # 基础 + 乘除法 + 单精度浮点 + 原子 + 压缩指令
    "rv32imafc": {"arch": "rv32imafc", "abi": "ilp32f", "default_fpu": "soft"},
    # 基础 + 乘除法 + 单/双精度浮点 + 原子 + 压缩指令 (32位全功能配置)
    "rv32imafdc": {"arch": "rv32imafdc", "abi": "ilp32d", "default_fpu": "soft"},
    # 基础 + 乘除法 + 原子 + 压缩指令 + 位操作扩展 (Bit Manipulation)
    "rv32imacb": {"arch": "rv32imacb", "abi": "ilp32", "default_fpu": "soft"},
    # --- 64位架构 (RV64) ---
    # 基础 + 乘除法 + 原子 + 压缩指令 (无浮点，常用于轻量级Linux系统)
    "rv64imac": {"arch": "rv64imac", "abi": "lp64", "default_fpu": "soft"},
    # 基础 + 乘除法 + 单精度浮点 + 原子 + 压缩指令
    "rv64imafc": {"arch": "rv64imafc", "abi": "lp64f", "default_fpu": "soft"},
    # 基础 + 乘除法 + 单/双精度浮点 + 原子 + 压缩指令 (64位全功能配置)
    "rv64imafdc": {"arch": "rv64imafdc", "abi": "lp64d", "default_fpu": "soft"},
    # 通用 64 位配置缩写 (等同于 rv64imafdc，常用于桌面/服务器级Linux)
    "rv64gc": {"arch": "rv64gc", "abi": "lp64d", "default_fpu": "hard"},
    # x86
    "x86": {"arch": "i386", "fpu": None, "default_fpu": ""},
    "x86-64": {"arch": "x86-64", "fpu": None, "default_fpu": ""},
    "x86-64-v3": {"arch": "x86-64-v3", "fpu": None, "default_fpu": ""},
    "xtensa": {"arch": "xtensa", "fpu": None, "default_fpu": ""},
}

_ARCH_SIMPLIFY = {
    "armv6s-m": "armv6m",
    "armv7-m": "armv7m",
    "armv7e-m": "armv7m",
    "armv8-m.base": "armv8m_base",
    "armv8-m.main": "armv8m_main",
    "armv8.1-m.main": "armv8.1m_main",
}


def cpu_arch(cpu: str) -> dict | None:
    """根据 CPU 名称返回架构信息"""
    return CPU_INFO.get(cpu)


def get_arch_simplify(arch: str) -> str | None:
    """根据架构返回简化后的架构"""
    return _ARCH_SIMPLIFY.get(arch)


def get_float_abi(fpu: str | None) -> str:
    if fpu in (None, "none", "soft"):
        return "soft"
    return "hard"


def get_fpu_floatabi(cpu: str | None, fpu: str | None, float_abi: str | None) -> tuple:
    info = CPU_INFO.get(cpu)
    if not info:
        return fpu, float_abi
    fpu = info.get("fpu") or "nofp"
    # fpu_safe = fpu.replace("-", "_")
    float_abi_ = get_float_abi(fpu)
    if not float_abi:
        float_abi = float_abi_
    elif float_abi == "softfp":
        float_abi = "soft"
    elif float_abi == "soft":
        float_abi = "soft"

    if fpu == "nofp":
        float_abi = "soft"
    return fpu, float_abi


def get_eta_sysroot(cpu: str, fpu: str | None, float_abi: str | None = None) -> str:
    info = CPU_INFO.get(cpu)
    if not info:
        return ""
    arch = info.get("arch", "")
    arch_simple = get_arch_simplify(arch) or arch.replace("-", "").replace(".", "_")
    fpu = info.get("fpu") or "nofp"
    fpu_safe = fpu.replace("-", "_")
    # if float_abi is None:
    #     float_abi = get_float_abi(fpu)
    float_abi_ = get_float_abi(fpu)

    if not float_abi:
        float_abi = float_abi_
    elif float_abi == "softfp":
        float_abi = "soft"
    elif float_abi == "soft":
        float_abi = "soft"

    if fpu == "nofp":
        float_abi = "soft"

    res = f"clang-runtimes/arm-none-eabi/{arch_simple}_{float_abi}_{fpu_safe}"
    # print(f"chips::get_eta_sysroot {res}  {float_abi}")
    return res


def get_eta_riscv_sysroot(cpu: str, float_abi: str | None = None) -> str:
    pass
