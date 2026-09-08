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

import platform

from nimmake.datasets.chips import _ARCH_SIMPLIFY, CPU_INFO
from nimmake.utils import log

TOOL_CMD_PREFIX: dict[str, type] = {
    ("gcc", ""): ["gcc", ""],
    ("gcc", "x86_64"): ["gcc", ""],
    ("gcc", "arm"): ["gcc", "arm"],
    ("gcc", "riscv"): ["gcc", "riscv"],
    ("clang", ""): ["clang", ""],
    ("clang", "x86_64"): ["clang", ""],
    ("clang", "arm"): ["clang", "arm"],
    ("clang", "riscv"): ["clang", "riscv"],
    #
    ("default", ""): ["gcc", ""],
    ("default", "x86_64"): ["gcc", ""],
    #
    ("armclang", ""): ["armclang", ""],
    ("msvc", ""): ["msvc", ""],
    #
    ("armgcc", ""): ["gcc", "arm"],
    ("armllvm", ""): ["clang", "arm"],
}


def get_tool(tool: str = "", prefix: str = "") -> str:
    if not tool:
        return "default"
    if tool in ["gcc", "clang", "msvc", "armclang", "armgcc"]:
        return tool
    if "gcc" in tool:
        return "gcc"
    if "clang" in tool:
        return "clang"
    if "msvc" in tool:
        return "msvc"
    if "armclang" in tool:
        return "armclang"
    if "arm" in tool and "llvm" in tool:
        return "armllvm"


def get_gcc_suits(prefix: str = "") -> list[str]:
    """
    objcopy hex bin
    """
    return {
        "CC": prefix + "gcc",
        "CXX": prefix + "g++",
        "AS": prefix + "as",
        "AR": prefix + "ar",
        "LD": prefix + "gcc",
        "SIZE": prefix + "size",
        "OBJCOPY": prefix + "objcopy",
        "OBJDUMP": prefix + "objdump",
    }


def get_clang_suits(prefix: str = "") -> list[str]:
    """
    objcopy hex bin
    """
    return {
        "CC": prefix + "clang",
        "CXX": prefix + "clang++",
        "AS": prefix + "clang",
        "AR": prefix + "llvm-ar",
        "LD": prefix + "clang",
        "SIZE": prefix + "llvm-size",
        "OBJCOPY": prefix + "llvm-objcopy",
        "OBJDUMP": prefix + "llvm-objdump",
    }


def get_msvc_suits(prefix: str = "") -> list[str]:
    """
    objcopy hex bin
    """
    return {
        "CC": prefix + "cl.exe",
        "CXX": prefix + "cl++",
        "AS": prefix + "cl.exe",
        "AR": prefix + "lib.exe",
        "LD": prefix + "link.exe",
        "SIZE": prefix + "size.exe",
        "OBJCOPY": prefix + "objcopy.exe",
        "OBJDUMP": prefix + "objdump.exe",
    }


def tool_suits(tool: str = "gcc", prefix: str = "") -> list[str]:
    if tool == "gcc":
        return get_gcc_suits(prefix)
    elif tool == "clang":
        return get_clang_suits(prefix)
    elif tool == "msvc":
        return get_msvc_suits(prefix)
    else:
        return get_gcc_suits()


# ===================================================================
# ARM Cortex-M FPU 表
# ===================================================================

# def _arm_fpu_flags_1(cpu: str, fpu: str) -> List[str]:
#     """ARM 目标 FPU 相关标志"""
#     info = ARM_CORTEX_FPU.get(cpu)
#     mode = fpu or (info[2] if info and info[1] else "none")
#     flags = []
#     if mode and mode not in ("none", "soft", "hard"):
#         flags.append(f"-mfpu={mode}")
#     abi = "softfp" if mode.startswith("fpv") else ("hard" if mode == "hard" else "soft")
#     flags.append(f"-mfloat-abi={abi}")
#     flags.append("-mthumb")
#     return flags


def _arm_fpu_flags(cpu: str, fpu: str = "none", abi: str = None, thumb: str = "") -> list[str]:
    """ARM 目标 FPU 相关标志"""
    info = CPU_INFO.get(cpu)
    if not info:
        log.error(f"[cpu :{cpu}] not in {CPU_INFO.keys()}")
        return []

    flags = []
    fpu_ = fpu or (info.get("fpu") if info.get("fpu") is not None else "none")

    if fpu_ and fpu_ not in ("none", "soft", "hard"):
        flags.append(f"-mfpu={fpu_}")
    abi_ = "hard" if fpu_.startswith("fpv") else ("hard" if fpu_ == "hard" else "soft")
    if abi:
        abi_ = abi
    flags.append(f"-mfloat-abi={abi_}")

    # flags = []
    # mode = fpu or (info.get("fpu") if info.get("fpu") is not None else "none")

    # if mode and mode not in ("none", "soft", "hard"):
    #     flags.append(f"-mfpu={mode}")
    # abi = "softfp" if mode.startswith("fpv") else ("hard" if mode == "hard" else "soft")
    # flags.append(f"-mfloat-abi={abi}")
    flags.append("-mthumb" if not thumb else f"-m{thumb}")
    return flags


def _riscv_fpu_flags2(cpu: str, fpu: str = "none", thumb: str = "") -> list[str]:
    """RISC-V 目标架构与 ABI 标志

    从 CPU_INFO 中读取 arch 和 abi，生成 -march= / -mabi= / -mcmodel= 标志。
    与 ARM 不同，RISC-V 没有 -mfpu / -mfloat-abi / -mthumb 参数。

    CPU_INFO 示例：
        "rv32imac":  {"arch": "rv32imac",  "abi": "ilp32"}
        "rv32imafc": {"arch": "rv32imafc", "abi": "ilp32f"}
        "rv64gc":    {"arch": "rv64gc",    "abi": "lp64d"}
    """
    info = CPU_INFO.get(cpu)
    if not info:
        log.error(f"[cpu :{cpu}] not in {CPU_INFO.keys()}")
        return []

    flags = []
    arch = info.get("arch")
    if arch:
        flags.append(f"-march={arch}")
    abi = info.get("abi")
    if abi:
        flags.append(f"-mabi={abi}")
    # rv64 需要 medany 以支持 64 位地址空间；rv32 用 medlow 即可
    if arch and arch.startswith("rv64"):
        flags.append("-mcmodel=medany")
    return flags


def _riscv_fpu_flags(cpu: str, fpu: str = "none", abi: str = None, thumb: str = "") -> list[str]:
    """RISC-V 目标架构与 ABI 标志

    从 CPU_INFO 中读取 arch 和 abi，生成 -march= / -mabi= / -mcmodel= 标志。
    与 ARM 不同，RISC-V 没有 -mfpu / -mfloat-abi / -mthumb 参数。

    CPU_INFO 示例：
        "rv32imac":  {"arch": "rv32imac",  "abi": "ilp32"}
        "rv32imafc": {"arch": "rv32imafc", "abi": "ilp32f"}
        "rv64gc":    {"arch": "rv64gc",    "abi": "lp64d"}
    """
    log.info(f"_riscv_fpu_flags cpu :{cpu}")
    cpu_split = cpu.split("_")
    cpu_ = cpu_split[0]
    cpu_tail = ""
    if len(cpu_split) > 1:
        cpu_tail = "".join([f"_{x}" for x in cpu_split[1:]])
    info = CPU_INFO.get(cpu_)
    if not info:
        log.error(f"[cpu :{cpu}] not in {CPU_INFO.keys()}")
        return []

    flags = []
    arch = info.get("arch")
    if arch:
        flags.append(f"-march={arch}{cpu_tail}")
    abi = info.get("abi")
    # if abi:
    #     flags.append(f"-mfloat-abi={abi}")
    # rv64 需要 medany 以支持 64 位地址空间；rv32 用 medlow 即可
    if arch and arch.startswith("rv64"):
        flags.append("-mcmodel=medany")
    return flags


def generate_riscv_gcc_flags(arch_str, mcmodel="medany", thumb=True):
    """
    根据 RISC-V 架构字符串生成 riscv-none-elf-gcc 的编译参数列表
    """
    # 1. 基础命令
    flags = ["riscv-none-elf-gcc", "-c"]

    # 2. 解析架构字符串 (例如: rv32imac)
    if not arch_str.startswith("rv"):
        raise ValueError("架构字符串必须以 'rv' 开头，例如 rv32imac")

    base_arch = arch_str[:4]  # rv32 或 rv64
    extensions = arch_str[4:]  # imac, imafdc 等

    # 3. 自动推导 ABI 和 FPU 参数
    if base_arch == "rv32":
        if "d" in extensions:
            abi = "ilp32d"
            float_abi = "hard"
        elif "f" in extensions:
            abi = "ilp32f"
            float_abi = "hard"
        else:
            abi = "ilp32"
            float_abi = "soft"

    elif base_arch == "rv64":
        if "d" in extensions:
            abi = "lp64d"
            float_abi = "hard"
        elif "f" in extensions:
            abi = "lp64f"
            float_abi = "hard"
        else:
            abi = "lp64"
            float_abi = "soft"
    else:
        raise ValueError(f"不支持的基础架构: {base_arch}")

    # 4. 组装参数
    flags.append(f"-march={arch_str}")
    flags.append(f"-mabi={abi}")
    flags.append(f"-mfloat-abi={float_abi}")
    flags.append(f"-mcmodel={mcmodel}")

    # 注意：-mthumb 是 ARM 架构特有的参数，RISC-V 没有此参数。
    # 这里保留您的原始需求，但建议在实际 RISC-V 编译中去掉它。
    if thumb:
        flags.append("-mthumb")

    return flags


def _arm_llvm_fpu_flags(cpu: str, fpu: str = "none", abi: str = None, thumb: str = "") -> list[str]:
    """ARM LLVM/Clang 目标 FPU 相关标志

    与 GCC 版 _arm_fpu_flags 的区别：Clang 对 fpv* FPU 使用 hard ABI，
    而非 GCC 的 softfp。参考 ARM LLVM 官方示例和 Makefile 惯例。
    """
    # log.info(f"arm_llvm_fpu_flags: {cpu} {fpu} {abi} {thumb}")
    flags = []
    info = CPU_INFO.get(cpu)
    arch_ = info.get("arch")
    if arch_.startswith("armv"):
        # arch_ = arch_[3:]
        arm_simplify = _ARCH_SIMPLIFY.get(arch_)
        flags.append(f"--target={arm_simplify}-unknown-none-eabi")
        # flags.append(f"--target=arm-arm-none-eabi")
        # flags.append(f"--target=arm-none-eabi")
        flags.append(f"-march={info.get('arch')}")

    fpu_ = fpu or (info.get("fpu") if info.get("fpu") is not None else "none")

    if fpu_ and fpu_ not in ("none", "soft", "hard"):
        flags.append(f"-mfpu={fpu_}")
    abi_ = "hard" if fpu_.startswith("fpv") else ("hard" if fpu_ == "hard" else "soft")
    if abi:
        abi_ = abi
    flags.append(f"-mfloat-abi={abi_}")
    # log.info(f"info 5: {flags}")
    flags.append("-mthumb" if not thumb else f"-m{thumb}")
    # flags.append("-mlittle-endian" if not endian or endian == "little" else "-mbig-endian")

    return flags


def _riscv_llvm_fpu_flags(
    cpu: str, fpu: str = "none", abi: str = None, thumb: str = ""
) -> list[str]:
    """RISC-V Clang/LLVM 目标架构与 ABI 标志

    与 GCC 版 _riscv_fpu_flags 的区别：Clang 需要额外的 --target= 三元组。
    其余 -march= / -mabi= / -mcmodel= 行为一致。
    """
    info = CPU_INFO.get(cpu)
    if not info:
        log.error(f"[cpu :{cpu}] not in {CPU_INFO.keys()}")
        return []

    flags = []
    arch = info.get("arch")
    if not arch:
        return flags

    # Clang 三元组：rv32 → riscv32-unknown-none-elf, rv64 → riscv64-unknown-none-elf
    bits = "64" if arch.startswith("rv64") else "32"
    flags.append(f"--target=riscv{bits}-unknown-none-elf")
    flags.append(f"-march={arch}")

    abi = info.get("abi")
    if abi:
        flags.append(f"-mabi={abi}")
    if arch.startswith("rv64"):
        flags.append("-mcmodel=medany")
    return flags


def generate_riscv_clang_flags(arch_str, mcmodel="medany"):
    """
    根据 RISC-V 架构字符串生成 Clang 的编译参数列表
    """
    # 1. 基础命令与 Target 指定
    flags = ["clang", "--target=riscv32-unknown-elf", "-c"]

    # 2. 解析架构字符串
    if not arch_str.startswith("rv"):
        raise ValueError("架构字符串必须以 'rv' 开头，例如 rv32imac")

    base_arch = arch_str[:4]  # rv32 或 rv64
    extensions = arch_str[4:]  # imac, imafdc 等

    # 如果是 RV64，更新 target 和默认 mcmodel
    if base_arch == "rv64":
        flags = "--target=riscv64-unknown-elf"
        # RV64 在裸机环境下通常使用 medany 或 medlow
        mcmodel = mcmodel or "medany"

    # 3. 自动推导 ABI
    if base_arch == "rv32":
        if "d" in extensions:
            abi = "ilp32d"
        elif "f" in extensions:
            abi = "ilp32f"
        else:
            abi = "ilp32"
    elif base_arch == "rv64":
        if "d" in extensions:
            abi = "lp64d"
        elif "f" in extensions:
            abi = "lp64f"
        else:
            abi = "lp64"
    else:
        raise ValueError(f"不支持的基础架构: {base_arch}")

    # 4. 组装 Clang 参数
    flags.append(f"-march={arch_str}")
    flags.append(f"-mabi={abi}")
    flags.append(f"-mcmodel={mcmodel}")

    # 注意：Clang 在 RISC-V 下不需要也不支持 -mfloat-abi 和 -mthumb
    return flags


# ===================================================================
# 链接参数生成工具
# ===================================================================


def _ld_gcc(
    linkscript="",
    mmap="",
    gc_sections=False,
    nostartfiles=False,
    nostdlib=False,
    shared=False,
    library_path="",
    specs="",
    lto="",
    semihost=False,
    sysroot="",
    **kwargs,
) -> list[str]:
    """GCC style link flags"""
    flags = []
    if gc_sections:
        flags.append("-Wl,--gc-sections")
    if linkscript:
        flags.append(
            f"--scatter={linkscript}" if linkscript.endswith(".sct") else f"-T{linkscript}"
        )
    if mmap:
        flags.append(f"-Wl,-Map={mmap}")

    if nostartfiles:
        flags.append("-nostartfiles")
    if nostdlib:
        flags.append("-nostdlib")

    if lto:
        flags.append(f"-flto={lto}")
    if sysroot:
        flags.append(f"--sysroot={sysroot}")
    if library_path:
        flags.append(f"-L{library_path}")
    if specs:
        flags.append(f"--specs={specs}")

    if not shared:
        # flags.append("-shared")
        pass
    else:
        # flags.append("-Wl,--shared")
        pass
    return flags


def _ld_zig(
    linkscript="",
    mmap="",
    gc_sections=False,
    nostartfiles=False,
    nostdlib=False,
    shared=False,
    library_path="",
    specs="",
    lto="",
    semihost=False,
    sysroot="",
    **kwargs,
) -> list[str]:
    """zig style link flags"""
    flags = []
    if gc_sections:
        flags.append("-Wl,--gc-sections")
    if linkscript:
        flags.append(
            f"--scatter={linkscript}" if linkscript.endswith(".sct") else f"-T{linkscript}"
        )
    if mmap:
        flags.append(f"-Wl,-Map={mmap}")

    if nostartfiles:
        flags.append("-nostartfiles")
    if nostdlib:
        flags.append("-nostdlib")

    if lto:
        flags.append(f"-flto={lto}")
    if sysroot:
        flags.append(f"--sysroot={sysroot}")
    if library_path:
        flags.append(f"-L{library_path}")
    if specs:
        flags.append(f"--specs={specs}")

    if not shared:
        # flags.append("-shared")
        pass
    else:
        # flags.append("-Wl,--shared")
        pass
    return flags


def _ld_armllvm(
    linkscript="",
    mmap="",
    gc_sections=False,
    nostartfiles=False,
    nostdlib=False,
    shared=False,
    ld_path="",
    library_path="",
    specs="",
    lto="",
    semihost=False,
    sysroot="",
    **kwargs,
) -> list[str]:
    """arm style link flags"""
    flags = []
    # if gc_sections:
    #     flags.append("-Wl,--gc-sections")

    if ld_path:
        flags.append(f"--ld-path={ld_path}")
    if sysroot:
        flags.append(f"--sysroot={sysroot}")
    if linkscript:
        flags.append(
            f"--scatter={linkscript}" if linkscript.endswith(".sct") else f"-T{linkscript}"
        )
    if mmap:
        flags.append(f"-Wl,-Map={mmap}")

    if nostartfiles:
        flags.append("-nostartfiles")
    if nostdlib:
        flags.append("-nostdlib")
    if gc_sections:
        flags.append("-Wl,--gc-sections")

    if lto:
        flags.append(f"-flto={lto}")
    # if ld_path:
    #     flags.append(f"--ld-path={ld_path}")
    # if sysroot:
    #     flags.append(f"--sysroot={sysroot}")
    if library_path:
        flags.append(f"-L{library_path}")
    if specs:
        flags.append(f"--specs={specs}")

    if not shared:
        # flags.append("-shared")
        pass
    else:
        # flags.append("-Wl,--shared")
        pass
    return flags


def _ld_armclang(
    linkscript="",
    mmap="",
    gc_sections=False,
    nostartfiles=False,
    nostdlib=False,
    shared=False,
    ld_path="",
    library_path=None,
    specs=None,
    lto="",
    semihost=False,
    sysroot="",
    **kwargs,
) -> list[str]:
    """ARMClang 风格链接参数"""
    flags = []
    if gc_sections:
        flags.append("-Wl,--gc-sections")
    if linkscript:
        flags.append(
            f"--scatter={linkscript}" if linkscript.endswith(".sct") else f"-T{linkscript}"
        )
    if mmap:
        flags.append(f"-Wl,-Map={mmap}")
    if nostartfiles:
        flags.append("-nostartfiles")
    if nostdlib:
        flags.append("-nostdlib")
    if lto:
        flags.append(f"-flto={lto}")
    if sysroot:
        flags.append(f"--sysroot={sysroot}")
    if ld_path:
        flags.append(f"--ld-path={ld_path}")
    for lp in library_path or []:
        flags.append(f"-L{lp}")
    for s in specs or []:
        flags.append(f"--specs={s}.specs")
    return flags


def _tool_gcc(tool: str = "gcc", prefix: str = "") -> list[str]:
    tool = "gcc"
    prefix = prefix.strip().lower()
    dct = {
        "cc": f"{prefix}{tool}",
        "cxx": f"{prefix}g++",
        "as": f"{prefix}as",
        "ar": f"{prefix}ar ",
        "ld": f"{prefix}gcc ",
        "link": f"{prefix}gcc ",
        "size": f"{prefix}size ",
        "objcopy": f"{prefix}objcopy ",
        "objdump": f"{prefix}objdump ",
    }
    return dct


def _tool_clang(tool: str = "clang", prefix: str = "") -> list[str]:
    prefix = prefix.strip().lower()
    dct = {
        "cc": f"{prefix}clang",
        "cxx": f"{prefix}clang++",
        "as": f"{prefix}clang",
        "ar": f"{prefix}llvm-ar",
        "ld": f"{prefix}clang",
        "link": f"{prefix}ld.lld",
        "size": f"{prefix}llvm-size",
        "objcopy": f"{prefix}llvm-objcopy",
        "objdump": f"{prefix}llvm-objdump",
    }
    return dct


def _tool_zig(tool: str = "zig", prefix: str = "") -> list[str]:
    prefix = prefix.strip().lower()
    dct = {
        "cc": f"{prefix}zig cc",
        "cxx": f"{prefix}zig c++",
        "as": f"{prefix}zig cc -c -x assembler",
        "ar": f"{prefix}zig ranlib",
        "ld": f"{prefix}zig ld",
        "link": f"{prefix}zig link",
        "size": f"{prefix}zig size",
        "objcopy": f"{prefix}zig objcopy",
        "objdump": f"{prefix}zig objdump",
    }
    return dct


def _tool_armclang(tool: str = "clang", prefix: str = "") -> list[str]:
    prefix = prefix.strip().lower()
    dct = {
        "cc": "armclang",
        "cxx": "armclang++",
        "as": "armclang",
        "ar": "armar",
        "ld": "armlink",
        "link": "armclang",
        "size": "size",
        "objcopy": "fromelf",
        "objdump": "fromelf",
    }
    return dct


def get_suffix(cc: str = None, targetos: str = None, cflags: list[str] = None):
    """
    target suffix
    msvc :动态链 两个文件 .dll .lib
    mingw -win : 两个文件 .dll .a or .dll.a
    linux, shared , 可以传版本号 SONAME 软链接,也可以不传版本号,默认版本号
    -Wl,-soname,libcalc.so.1
    """
    log.debug(f"Platfrom = {platform.system()}  {platform.machine()}")
    if cc == "armclang":
        return ".axf", ".o", ".a", ".a"

    if cc == "msvc":
        return ".exe", ".obj", ".lib", ".lib"

    # gcc
    if "gcc" in cc:
        if targetos in ["elf", "none"]:
            return ".elf", ".o", ".a", ".a"
        elif targetos in ["windows"]:
            return ".exe", ".o", ".a", ".dll"
        elif targetos in ["linux"]:
            return ".elf", ".o", ".a", ".so"
        elif targetos in ["apple", "darwin"]:
            return ".app", ".o", ".a", ".dylib"
        else:
            return ".elf", ".o", ".a", ".a"

    # clang
    if "clang" in cc:
        cflags = cflags
        _target = ""
        plat = platform.system().lower().strip()
        for flag in cflags:
            if flag.startswith("-target"):
                _target = flag.split("=")[1]
                break
        if _target:
            _target_triple = _target.split("-")
            if len(_target_triple) >= 3:
                plat = _target_triple[-2]

        if plat.lower() in ["windows"]:
            return ".exe", ".o", ".a", ".dll"
        elif plat.lower() in ["linux"]:
            return ".elf", ".o", ".a", ".so"
        elif plat.lower() in ["apple", "darwin"]:
            return ".app", ".o", ".a", ".dylib"
        else:
            return ".elf", ".o", ".a", ".a"
    return None, None, None, None


# def get_tool(tool: str = "", prefix: str = "") -> str:
#     if not tool:
#         return "default"
#     if tool in ["gcc", "clang", "msvc", "armclang", "armgcc"]:
#         return tool
#     if "gcc" in tool:
#         return "gcc"
#     if "clang" in tool:
#         return "clang"
#     if "msvc" in tool:
#         return "msvc"
#     if "armclang" in tool:
#         return "armclang"
#     if "arm" in tool and "llvm" in tool:
#         return "armllvm"


# def get_backend(tool: str, arch: str) -> bool:
#     _tool = tool.lower()
#     _tool = get_tool(_tool)

#     _arch = arch
#     if not _arch:
#         _arch = ""
#     if "arm" in _arch:
#         _arch = "arm"
#     if "riscv" in _arch:
#         _arch = "riscv"
#     return BACKENDS.get((_tool, _arch), None)

#     return True


# def get_backend_cls(tool: str = "", prefix: str = "") -> str:
#     if not tool:
#         tool = "default"
#     if tool not in ["gcc", "clang", "msvc", "armclang", "armgcc", "armllvm"]:
#         tool = "default"

#     if not prefix:
#         prefix = ""

#     if "arm" in prefix:
#         prefix = "arm"
#     elif "llvm" in prefix:
#         prefix = "llvm"
#     elif "riscv" in prefix:
#         prefix = "riscv"
#     elif "x86_64" in prefix:
#         prefix = "x86_64"
#     else:
#         prefix = ""
#     # log.error(f"get_backend_cls = {tool}, {prefix}")
#     return BACKENDS.get((tool, prefix), None)
