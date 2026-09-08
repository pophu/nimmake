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

"""Presets DCT  GCC"""

from __future__ import annotations

CORTEX_M4_GCC_DCT = {
    "toolchain": "gcc",
    "cpu": "cortex-m4",
    "fpu": "hard",
    "opt": "O2",
    "dbg": True,
    "warn": "Wall",
    "std_c": "c99",
    "std_cxx": "c++11",
    "no_rtti": True,
    "no_exception": True,
    "data_sections": "-fdata-sections",
    "func_sections": "-ffunction-sections",
    "linkscript": "stm32f4.ld",
    "gc_sections": True,
}

# CORTEX_M4_ARMLLVM_DCT = {
#     "toolchain": "gcc",
#     "cpu": "cortex-m4",
#     "fpu": "hard",
#     "opt": "O2",
#     "dbg": True,
#     "warn": "Wall",
#     "std_c": "c99",
#     "std_cxx": "c++11",
#     "nostdlib": True,
#     "no_rtti": True,
#     "no_exception": True,
#     "data_sections": "-fdata-sections",
#     "func_sections": "-ffunction-sections",
#     "linkscript": "stm32f4.ld",
#     "gc_sections": True,
# }

RISCV_32_IMAC_GCC_DCT = {
    "toolchain": "gcc",
    "cpu": "rv32imac",
    "abi": "ilp32",
    "opt": "O2",
    "dbg": True,
    "warn": "Wall",
    "std_c": "gnu99",
    "std_cxx": "c++11",
    "no_rtti": True,
    "no_exception": True,
    "data_sections": "-fdata-sections",
    "func_sections": "-ffunction-sections",
    "linkscript": "gd32vf1.ld",
    "gc_sections": True,
}
RISCV_64_GC_GCC_DCT = {
    "toolchain": "gcc",
    "cpu": "rv64gc",
    "abi": "lp64d",
    "opt": "O2",
    "dbg": True,
    "warn": "Wall",
    "std_c": "c99",
    "std_cxx": "c++11",
    "no_rtti": True,
    "no_exception": True,
    "data_sections": "-fdata-sections",
    "func_sections": "-ffunction-sections",
    "freestanding": False,
    "no_builtin": False,
    "linkscript": "gd32vf1.ld",
    "gc_sections": True,
}
ESP_RISCV_32_IMAC_GCC_DCT = {
    "toolchain": "gcc",
    "cpu": "rv32imac",
    "abi": "ilp32",
    "opt": "O2",
    "dbg": True,
    "warn": "Wall",
    "std_c": "c99",
    "std_cxx": "c++11",
    "no_rtti": True,
    "no_exception": True,
    "data_sections": "-fdata-sections",
    "func_sections": "-ffunction-sections",
    "linkscript": "gd32vf1.ld",
    "gc_sections": True,
}

DESK_GCC_DCT = {
    "toolchain": "gcc",
    # "arch": "x86-64",
    "opt": "O2",
    "dbg": False,
    "warn": "Wall",
    "std_c": "c99",
    "std_cxx": "c++17",
}
DESK_CLANG_DCT = {
    # "arch": "x86-64",
    "opt": "O2",
    "dbg": False,
    "warn": "Wall",
    "std_c": "c99",
    "std_cxx": "c++17",
}


# ===================================================================
# 预设 DCT  CLANG
# ===================================================================
CORTEX_M4_CLANG_DCT = {
    "toolchain": "clang",
    "cpu": "cortex-m4",
    "fpu": "fpv4-sp-d16",
    "opt": "O2",
    "dbg": True,
    "warn": "Wall",
    "std_c": "c99",
    "std_cxx": "c++11",
    "nostdlib": True,
    "freestanding": False,
    "data_sections": "-fdata-sections",
    "func_sections": "-ffunction-sections",
    "linkscript": "stm32f4.ld",
    "gc_sections": True,
}

RISCV_32_IMAC_CLANG_DCT = {
    "toolchain": "clang",
    "cpu": "rv32imac",
    "abi": "ilp32",
    "opt": "O2",
    "dbg": True,
    "warn": "Wall",
    "std_c": "c99",
    "std_cxx": "c++11",
    "data_sections": "-fdata-sections",
    "func_sections": "-ffunction-sections",
    "linkscript": "gd32vf1.ld",
    "gc_sections": True,
}
RISCV_64_GC_CLANG_DCT = {
    "toolchain": "clang",
    "cpu": "rv64gc",
    "abi": "lp64d",
    "opt": "O2",
    "dbg": True,
    "warn": "Wall",
    "std_c": "c99",
    "std_cxx": "c++11",
    "data_sections": "-fdata-sections",
    "func_sections": "-ffunction-sections",
    "linkscript": "gd32vf1.ld",
    "gc_sections": True,
}
ESP_RISCV_32_IMAC_CLANG_DCT = {
    "toolchain": "clang",
    "cpu": "rv32imac",
    "abi": "ilp32",
    "opt": "O2",
    "dbg": True,
    "warn": "Wall",
    "std_c": "c99",
    "std_cxx": "c++11",
    "data_sections": "-fdata-sections",
    "func_sections": "-ffunction-sections",
    "linkscript": "gd32vf1.ld",
    "gc_sections": True,
}

DESK_CLANG_DCT = {
    "toolchain": "clang",
    "arch": "x86-64",
    "opt": "O2",
    "dbg": False,
    "warn": "Wall",
    "std_c": "c99",
    "std_cxx": "c++17",
}

# ===================================================================
# 预设 DCT  CLANG
# ===================================================================
DESK_MSVC_DCT = {
    "toolchain": "msvc",
    "arch": "x86-64",
    "opt": "O2",
    "dbg": False,
    "warn": "Wall",
    "std_c": "c99",
    "std_cxx": "c++17",
}


if __name__ == "__main__":
    # 打印上面所有字典名称

    for k in list(globals().keys()):  # ✅ 先转为列表再遍历
        if k.endswith("_DCT"):
            print(f"{k}, ")
            # print(f"\n{k} ")
            # for key, value in globals()[k].items():
            #     print(f"  {key}: {value}")

    # for k in globals():
    #     print(k)
    #     # if k.startswith("CORTEX_M4"):
    #     #     print(k)
    #     # elif k.startswith("RISCV_"):
    #     #     print(k)
    #     # elif k.startswith("DESK"):
    #     #     print(k)
