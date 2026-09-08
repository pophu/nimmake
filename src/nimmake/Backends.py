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

"""Backend
Backend — get toolchain flags
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from .datasets.chips import get_eta_riscv_sysroot, get_eta_sysroot, get_fpu_floatabi
from .datasets.tools import (
    _arm_fpu_flags,
    _arm_llvm_fpu_flags,
    _ld_armclang,
    _ld_armllvm,
    _ld_gcc,
    _ld_zig,
    _riscv_fpu_flags,
    _riscv_llvm_fpu_flags,
    _tool_armclang,
    _tool_clang,
    _tool_gcc,
    _tool_zig,
    get_tool,
)
from .executor import CmdExecutor
from .flags import Flags
from .utils import log

# ===================================================================
# 基类
# ===================================================================


class BaseBackend(ABC):
    """工具链后端基类"""

    def __init__(
        self,
        cpu: str = "",
        arch: str = "",
        fpu: str = "",
        abi: str = "",
        thumb: str = "",
        vendor: str = "",
        model: str = "",
        exec: CmdExecutor = None,
        toolpath: str = "",
    ):
        self.cpu = cpu
        self.arch = arch
        self.fpu = fpu
        self.abi = abi
        self.thumb = thumb
        self.vendor = vendor
        self.model = model
        self._flags = None
        self._exec = exec
        if not exec:
            self._exec = CmdExecutor()
        self.toolpath = toolpath
        if toolpath:
            self._exec.add_path(toolpath, prepend=True)
        # r_path = self._exec.run("echo %PATH%", shell=True)
        # log.info("PATH:", r_path.stdout)

    # ---- 可重写的 hook ----
    @abstractmethod
    def target_flags(self) -> list[str]:
        return []

    @abstractmethod
    def _ldflags(self, **kw) -> list[str]:
        return []

    @abstractmethod
    def _tool(self, tool: str = "", prefix: str = "") -> list[str]:
        return []

    def set(self, key: str, value: str) -> BaseBackend:
        setattr(self, key, value)
        return self

    def from_cpu_2_fpu(self) -> str:
        pass

    def _arflags(self) -> list[str]:
        return ["rcs"]

    def opt_flags(self, opt: str = "O0", dbg: bool = False, warn: str = "") -> list[str]:
        flags = []
        if opt:
            flags.append(f"-{opt}")
        if warn:
            flags.append(f"-{warn}")
        if dbg:
            flags.append("-g")
        return flags

    def section_flags(self, data_sections: bool = False, func_sections: bool = False) -> list[str]:
        flags = []
        if data_sections:
            flags.append("-fdata-sections")
        if func_sections:
            flags.append("-ffunction-sections")
        return flags

    # ---- 主收集方法 ----
    def collect(
        self,
        opt: str = "O0",
        dbg: bool = False,
        warn: str = "",
        std_c: str = "",
        std_cxx: str = "",
        no_rtti: bool = False,
        no_exceptions: bool = False,
        data_sections: bool = False,
        func_sections: bool = False,
        freestanding: bool = False,
        no_builtin: bool = False,
        defines: dict[str, str] | None = None,
        **ld_kw,
    ) -> Flags:
        self.fpu, self.abi = get_fpu_floatabi(self.cpu, self.fpu, self.abi)
        # print(" BaseBackend fpu:", self.fpu, "abi:", self.abi)

        tgt = self.target_flags()

        opt_f = self.opt_flags(opt, dbg, warn)
        sec = self.section_flags(data_sections, func_sections)
        freestanding = ["-ffreestanding"] if freestanding else []
        no_builtin = ["-fno-builtin"] if no_builtin else []

        c = tgt + opt_f + sec + freestanding
        if std_c:
            c.append(f"-std={std_c}")
        cxx = tgt + opt_f + sec + freestanding + no_builtin
        if std_cxx:
            cxx.append(f"-std={std_cxx}")
            if no_rtti:
                cxx.append("-fno-rtti")
            if no_exceptions:
                cxx.append("-fno-exceptions")

        ld = tgt + self._ldflags(**ld_kw)

        self._flags = Flags(
            cflags=c,
            cxxflags=cxx,
            asflags=tgt[:],
            arflags=self._arflags(),
            ldflags=ld,
            defines=defines or {},
        )

        self.flags = {
            "cflags": c,
            "cxxflags": cxx,
            "asflags": tgt[:],
            "arflags": self._arflags(),
            "ldflags": ld,
            "defines": defines or {},
        }
        return self

    # def flags(
    #     self,
    #     opt: str = "O0",
    #     dbg: bool = False,
    #     warn: str = "",
    #     std_c: str = "",
    #     std_cxx: str = "",
    #     no_rtti: bool = False,
    #     no_exceptions: bool = False,
    #     data_sections: bool = False,
    #     func_sections: bool = False,
    #     freestanding: bool = False,
    #     no_builtin: bool = False,
    #     defines: dict[str, str] | None = None,
    #     **ld_kw,
    # ) -> BaseBackend:
    #     log.debug(std_c, std_cxx)
    #     tgt = self.target_flags()
    #     opt_f = self.opt_flags(opt, dbg, warn)
    #     sec = self.section_flags(data_sections, func_sections)
    #     freestanding = ["-ffreestanding"] if freestanding else []
    #     no_builtin = ["-fno-builtin"] if no_builtin else []
    #     c = tgt + opt_f + sec + freestanding
    #     if std_c:
    #         c.append(f"-std={std_c}")
    #     cxx = tgt + opt_f + sec + freestanding + no_builtin
    #     if std_cxx:
    #         cxx.append(f"-std={std_cxx}")
    #         if no_rtti:
    #             cxx.append(f"-fno-rtti")
    #         if no_exceptions:
    #             cxx.append(f"-fno-exceptions")

    #     ld = self._ldflags(**ld_kw)

    #     self.flags = {
    #         "cflags": c,
    #         "cxxflags": cxx,
    #         "asflags": tgt[:],
    #         "arflags": self._arflags(),
    #         "ldflags": ld,
    #         "defines": defines or {},
    #     }
    #     return self

    def is_tool_exsited(self, cmd: str) -> bool:
        cmd_lst = [cmd, "--version"]
        r = self._exec.is_command_valid(cmd_lst)
        # r_path = self._exec.run("echo %PATH%", shell=True)
        # print("PATH:", r_path.stdout)
        # print(f"======: {cmd_lst} {r}")
        return True if r else False

    def get_triple(self, cmd_lst) -> str:
        r = self._exec.run(cmd_lst, shell=True)  # shell=True 搜索路径
        return r.stdout

    # def output(self) -> List[str]:
    #     print(f"backend cflags: {f.cflags}")
    #     print(f"backend cxxflags: {f.cxxflags}")
    #     print(f"backend asflags: {f.asflags}")
    #     print(f"backend ldflags: {f.ldflags}")
    #     print(f"backend defines: {f.defines}")
    #     pass


# ===================================================================
# GCC
# ===================================================================


class GCCBackend(BaseBackend):
    def target_flags(self) -> list[str]:
        flags = []
        if self.cpu:
            flags.append(f"-mcpu={self.cpu}")
        elif self.arch:
            flags.append(f"-march={self.arch}")
        # flags += _arm_fpu_flags(self.cpu, self.fpu, self.thumb)
        return flags

    def _ldflags(self, **kw) -> list[str]:
        return _ld_gcc(**kw)

    def _tool(self, tool: str = "", prefix: str = "") -> list[str]:
        return _tool_gcc("gcc", prefix)


# ===================================================================
# ARM GCC
# ===================================================================


class ARMGCCBackend(BaseBackend):
    def target_flags(self) -> list[str]:
        flags = []
        if self.cpu:
            flags.append(f"-mcpu={self.cpu}")
        elif self.arch:
            flags.append(f"-march={self.arch}")
        flags += _arm_fpu_flags(self.cpu, self.fpu)
        return flags

    def _ldflags(self, **kw) -> list[str]:
        flags = _ld_gcc(**kw)
        if not kw.get("specs"):
            flags.append("--specs=nosys.specs")
        return flags

    def _tool(self, tool: str = "", prefix: str = "") -> list[str]:
        return _tool_gcc("gcc", prefix)


# ===================================================================
# Clang
# ===================================================================
class ClangBackend(BaseBackend):
    def target_flags(self) -> list[str]:
        flags = []
        if self.cpu:
            flags.append(f"-mcpu={self.cpu}")
        elif self.arch:
            flags.append(f"-march={self.arch}")
        # flags += _arm_fpu_flags(self.cpu, self.fpu, self.thumb)
        return flags

    def _ldflags(self, **kw) -> list[str]:
        return _ld_gcc(**kw)

    def _tool(self, tool: str = "", prefix: str = "") -> list[str]:
        return _tool_clang("clang", prefix)


# ===================================================================
# Clang
# ===================================================================
class ZigBackend(BaseBackend):
    def target_flags(self) -> list[str]:
        flags = []
        if self.cpu:
            flags.append(f"-mcpu={self.cpu}")
        elif self.arch:
            flags.append(f"-march={self.arch}")
        # flags += _arm_fpu_flags(self.cpu, self.fpu, self.thumb)
        return flags

    def _ldflags(self, **kw) -> list[str]:
        return _ld_zig(**kw)

    def _tool(self, tool: str = "", prefix: str = "") -> list[str]:
        return _tool_zig("zig", prefix)


# ===================================================================
# ARM Clang
# ===================================================================


class ARMClangBackend(BaseBackend):
    r"""
    ARmClang based on Keil
    sct
    asm -- arm not  gcc
    armclang --target=arm-arm-none-eabi -mcpu=cortex-a53 -c my_asm.s -o my_asm.o
    armar -r my_lib.a my_asm.o  , no cpu info
    armlink my_main.o my_lib.a -o output.axf ,auto
    armclang --target=arm-arm-none-eabi -march=armv8-a -c main.c -o main.o
    armlink  --force_explicit_attr 选项
    LDFLAGS =  --cpu=Cortex-M4.fp.sp --strict --scatter link.sct
            --libpath C:\Keil_v5\ARM\ARMCLANG\lib
    fromelf --i32 --output $@  $<
        fromelf --bin --output  $@ $<
    """

    def target_flags(self) -> list[str]:
        flags = ["--target=arm-arm-none-eabi"]  # armclang
        if self.cpu:
            flags.append(f"-mcpu={self.cpu}")
        flags += _arm_fpu_flags(self.cpu, self.fpu)
        return flags

    def _ldflags(self, **kw) -> list[str]:
        return _ld_armclang(**kw)

    def _tool(self, tool: str = "", prefix: str = "") -> list[str]:
        return _tool_armclang("clang", prefix)


# ===================================================================
# LLVM ARM
# ===================================================================


class LLVMARMBackend(BaseBackend):
    def target_flags(self) -> list[str]:
        # log.debug(f"LLVMARMBackend is supported  {self.cpu} {self.fpu} {self.abi}")
        # flags = ["--target=arm-arm-none-eabi"]
        # if self.cpu:
        #     flags.append(f"-mcpu={self.cpu}")
        flags = _arm_llvm_fpu_flags(self.cpu, self.fpu)
        return flags

    def _ldflags(self, **kw) -> list[str]:
        kw_ld = dict(**kw)
        if not kw.get("ld_path"):
            ldpath = Path(self.toolpath) / "ld.lld"
            kw_ld["ld_path"] = ldpath.as_posix()
        if not kw.get("sysroot"):
            # log.debug(f"LLVMARMBackend  cpu {self.cpu} , fpu: {self.fpu} abi {self.abi}")
            clang_rt = get_eta_sysroot(self.cpu, self.fpu, self.abi)
            sysroot = Path(self.toolpath).parent / "lib" / clang_rt
            # log.debug(f"LLVMARMBackend  sysroot= {sysroot}")
            kw_ld["sysroot"] = sysroot.as_posix()
        if not kw.get("nostdlib"):
            kw_ld["nostdlib"] = True
        flags = _ld_armllvm(**kw_ld)
        return flags

    def _tool(self, tool: str = "", prefix: str = "") -> list[str]:
        # log.debug("================================")
        return _tool_clang("clang", "")


# ===================================================================
# RISC-V GCC
# ===================================================================


class RISCVGCCBackend(BaseBackend):
    def target_flags(self) -> list[str]:
        flags = []
        if self.arch:
            flags.append(f"-march={self.arch}")
        if self.abi:
            flags.append(f"-mabi={self.abi}")
        # flags.append("-mcmodel=medany")
        flags += _riscv_fpu_flags(self.cpu, self.fpu)
        # log.info(f"RISCVGCCBackend target_flags  : {flags}")
        return flags

    def _ldflags(self, **kw) -> list[str]:
        flags = _ld_gcc(**kw)
        log.info(f"ld flags  : {flags}")
        if not kw.get("specs"):
            flags.append("--specs=nosys.specs")
        return flags

    def _tool(self, tool: str = "", prefix: str = "") -> list[str]:
        # log.debug(f"RISCVGCCBackend toolchain  : {tool} {prefix}")
        return _tool_gcc("gcc", prefix)


# ===================================================================
# RISC-V Clang
# ===================================================================


class RISCVClangBackend(BaseBackend):
    def target_flags(self) -> list[str]:
        flags = ["--target=riscv32-unknown-elf"]
        if self.arch:
            flags.append(f"-march={self.arch}")
        if self.abi:
            flags.append(f"-mabi={self.abi}")
        flags += _riscv_llvm_fpu_flags(self.cpu, self.fpu)
        return flags

    def _ldflags(self, **kw) -> list[str]:
        kw_ld = dict(**kw)
        if not kw.get("ld_path"):
            ldpath = Path(self.toolpath) / "ld.lld"
            kw_ld["ld_path"] = ldpath.as_posix()
        if not kw.get("sysroot"):
            clang_rt = get_eta_riscv_sysroot(self.cpu, self.fpu)
            sysroot = Path(self.toolpath).parent / "lib" / clang_rt
            kw_ld["sysroot"] = sysroot.as_posix()
        if not kw.get("nostdlib"):
            kw_ld["nostdlib"] = True
        flags = _ld_armllvm(**kw_ld)
        return flags

    def _tool(self, tool: str = "", prefix: str = "") -> list[str]:
        # log.debug("================================")
        return _tool_clang("clang", "")


# ===================================================================
# MSVC
# ===================================================================

MSVC_OPT = {"O0": "/Od", "O1": "/O1", "O2": "/O2", "O3": "/Ox", "Os": "/O1"}
MSVC_WARN = {"Wall": "/W4", "Wextra": "/W4", "Werror": "/WX"}
MSVC_STD = {"c++11": "c++14", "c++14": "c++14", "c++17": "c++17", "c++20": "c++20"}


class MSVCBackend(BaseBackend):
    def target_flags(self) -> list[str]:
        return [] if self.arch in ("", "x86") else ["/arch:AVX2"]

    def opt_flags(self, opt="O0", dbg=False, warn="") -> list[str]:
        flags = [MSVC_OPT.get(opt, f"/{opt}")]
        if warn:
            flags.append(MSVC_WARN.get(warn, f"/{warn}"))
        if dbg:
            flags += ["/Zi", "/DEBUG"]
        return flags

    def section_flags(self, data_sections=False, func_sections=False) -> list[str]:
        return ["/Gy"] if func_sections else []

    def collect(
        self,
        opt="O0",
        dbg=False,
        warn="",
        std_c="",
        std_cxx="",
        data_sections=False,
        func_sections=False,
        defines=None,
        **ld_kw,
    ) -> Flags:
        tgt = self.target_flags()
        opt_f = self.opt_flags(opt, dbg, warn)
        sec = self.section_flags(data_sections, func_sections)
        ld = self._ldflags(**ld_kw)

        c = tgt + opt_f + sec
        if std_c:
            c.append(f"/std:{std_c}")
        cxx = tgt + opt_f + sec
        if std_cxx:
            cxx.append(f"/std:{MSVC_STD.get(std_cxx, std_cxx)}")

        return Flags(
            cflags=c,
            cxxflags=cxx,
            asflags=["/c", "/coff"],
            arflags=["/NOLOGO"],
            ldflags=ld,
            defines=defines or {},
        )

    def _ldflags(self, **kw) -> list[str]:
        flags = []
        if kw.get("gc_sections"):
            flags += ["/OPT:REF", "/OPT:ICF"]
        if kw.get("mmap"):
            flags.append(f"/MAP:{kw['mmap']}")
        if kw.get("shared"):
            flags.append("/DLL")
        for lp in kw.get("library_path") or []:
            flags.append(f"/LIBPATH:{lp}")
        return flags


# ===================================================================
# 注册表
# ===================================================================

# BACKENDS2: dict[str, type] = {
#     "gcc": GCCBackend,
#     "armgcc": ARMGCCBackend,
#     "clang": GCCBackend,
#     "armclang": ARMClangBackend,
#     "llvmarm": LLVMARMBackend,
#     "riscvgcc": RISCVGCCBackend,
#     "riscvclang": RISCVClangBackend,
#     "msvc": MSVCBackend,
#     "default": BaseBackend,
# }

BACKENDS: dict[str, type] = {
    ("gcc", ""): GCCBackend,
    ("gcc", "x86_64"): GCCBackend,
    ("gcc", "arm"): ARMGCCBackend,
    ("gcc", "riscv"): RISCVGCCBackend,
    ("clang", ""): ClangBackend,
    ("clang", "x86_64"): ClangBackend,
    ("clang", "arm"): LLVMARMBackend,
    ("clang", "llvm"): LLVMARMBackend,
    ("clang", "riscv"): RISCVClangBackend,
    #
    ("default", ""): BaseBackend,
    ("default", "x86_64"): BaseBackend,
    #
    ("armclang", ""): ARMClangBackend,
    ("msvc", ""): MSVCBackend,
    #
    ("armgcc", ""): ARMGCCBackend,
    ("armllvm", ""): LLVMARMBackend,
}


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


def get_backend(tool: str, arch: str) -> bool:
    _tool = tool.lower()
    _tool = get_tool(_tool)

    _arch = arch
    if not _arch:
        _arch = ""
    if "arm" in _arch:
        _arch = "arm"
    if "riscv" in _arch:
        _arch = "riscv"
    return BACKENDS.get((_tool, _arch), None)

    return True


def get_backend_cls(tool: str = "", prefix: str = "") -> str:
    # log.debug(f"get_backend_cls = {tool}, {prefix}")
    if not tool:
        tool = "default"
    if tool not in ["gcc", "clang", "msvc", "armclang", "armgcc", "armllvm"]:
        tool = "default"
    if tool == "armclang":
        prefix = ""
        return BACKENDS.get((tool, prefix), None)
    if not prefix:
        prefix = ""

    if "arm" in prefix:
        prefix = "arm"
    elif "llvm" in prefix:
        prefix = "llvm"
    elif "riscv" in prefix:
        prefix = "riscv"
    elif "x86_64" in prefix:
        prefix = "x86_64"
    else:
        prefix = ""
    # log.debug(f"get_backend_cls = {tool}, {prefix}")
    return BACKENDS.get((tool, prefix), None)


# # ===================================================================
# # 链接参数生成工具
# # ===================================================================


# def _ld_gcc(
#     linkscript="",
#     mmap="",
#     gc_sections=False,
#     nostartfiles=False,
#     nostdlib=False,
#     shared=False,
#     library_path="",
#     specs="",
#     lto="",
#     semihost=False,
#     sysroot="",
#     **kwargs,
# ) -> list[str]:
#     """GCC style link flags"""
#     flags = []
#     if gc_sections:
#         flags.append("-Wl,--gc-sections")
#     if linkscript:
#         flags.append(
#             f"--scatter={linkscript}" if linkscript.endswith(".sct") else f"-T{linkscript}"
#         )
#     if mmap:
#         flags.append(f"-Wl,-Map={mmap}")

#     if nostartfiles:
#         flags.append("-nostartfiles")
#     if nostdlib:
#         flags.append("-nostdlib")

#     if lto:
#         flags.append(f"-flto={lto}")
#     if sysroot:
#         flags.append(f"--sysroot={sysroot}")
#     if library_path:
#         flags.append(f"-L{library_path}")
#     if specs:
#         flags.append(f"--specs={specs}")

#     if not shared:
#         # flags.append("-shared")
#         pass
#     else:
#         # flags.append("-Wl,--shared")
#         pass
#     return flags


# def _ld_armllvm(
#     linkscript="",
#     mmap="",
#     gc_sections=False,
#     nostartfiles=False,
#     nostdlib=False,
#     shared=False,
#     ld_path="",
#     library_path="",
#     specs="",
#     lto="",
#     semihost=False,
#     sysroot="",
#     **kwargs,
# ) -> list[str]:
#     """arm style link flags"""
#     flags = []
#     # if gc_sections:
#     #     flags.append("-Wl,--gc-sections")

#     if ld_path:
#         flags.append(f"--ld-path={ld_path}")
#     if sysroot:
#         flags.append(f"--sysroot={sysroot}")
#     if linkscript:
#         flags.append(
#             f"--scatter={linkscript}" if linkscript.endswith(".sct") else f"-T{linkscript}"
#         )
#     if mmap:
#         flags.append(f"-Wl,-Map={mmap}")

#     if nostartfiles:
#         flags.append("-nostartfiles")
#     if nostdlib:
#         flags.append("-nostdlib")
#     if gc_sections:
#         flags.append("-Wl,--gc-sections")

#     if lto:
#         flags.append(f"-flto={lto}")
#     # if ld_path:
#     #     flags.append(f"--ld-path={ld_path}")
#     # if sysroot:
#     #     flags.append(f"--sysroot={sysroot}")
#     if library_path:
#         flags.append(f"-L{library_path}")
#     if specs:
#         flags.append(f"--specs={specs}")

#     if not shared:
#         # flags.append("-shared")
#         pass
#     else:
#         # flags.append("-Wl,--shared")
#         pass
#     return flags


# def _ld_armclang(
#     linkscript="",
#     mmap="",
#     gc_sections=False,
#     nostartfiles=False,
#     nostdlib=False,
#     shared=False,
#     ld_path="",
#     library_path=None,
#     specs=None,
#     lto="",
#     semihost=False,
#     sysroot="",
#     **kwargs,
# ) -> list[str]:
#     """ARMClang 风格链接参数"""
#     flags = []
#     if gc_sections:
#         flags.append("-Wl,--gc-sections")
#     if linkscript:
#         flags.append(
#             f"--scatter={linkscript}" if linkscript.endswith(".sct") else f"-T{linkscript}"
#         )
#     if mmap:
#         flags.append(f"-Wl,-Map={mmap}")
#     if nostartfiles:
#         flags.append("-nostartfiles")
#     if nostdlib:
#         flags.append("-nostdlib")
#     if lto:
#         flags.append(f"-flto={lto}")
#     if sysroot:
#         flags.append(f"--sysroot={sysroot}")
#     if ld_path:
#         flags.append(f"--ld-path={ld_path}")
#     for lp in library_path or []:
#         flags.append(f"-L{lp}")
#     for s in specs or []:
#         flags.append(f"--specs={s}.specs")
#     return flags


# def _tool_gcc(tool: str = "gcc", prefix: str = "") -> list[str]:
#     tool = "gcc"
#     prefix = prefix.strip().lower()
#     dct = {
#         "cc": f"{prefix}{tool}",
#         "cxx": f"{prefix}g++",
#         "as": f"{prefix}as",
#         "ar": f"{prefix}ar ",
#         "ld": f"{prefix}gcc ",
#         "link": f"{prefix}gcc ",
#         "size": f"{prefix}size ",
#         "objcopy": f"{prefix}objcopy ",
#         "objdump": f"{prefix}objdump ",
#     }
#     return dct


# def _tool_clang(tool: str = "clang", prefix: str = "") -> list[str]:
#     prefix = prefix.strip().lower()
#     dct = {
#         "cc": f"{prefix}clang",
#         "cxx": f"{prefix}clang++",
#         "as": f"{prefix}clang",
#         "ar": f"{prefix}llvm-ar",
#         "ld": f"{prefix}clang",
#         "link": f"{prefix}ld.lld",
#         "size": f"{prefix}llvm-size",
#         "objcopy": f"{prefix}llvm-objcopy",
#         "objdump": f"{prefix}llvm-objdump",
#     }
#     return dct


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


# def _arm_fpu_flags(cpu: str, fpu: str = "none", thumb: str = "") -> list[str]:
#     """ARM 目标 FPU 相关标志"""
#     info = CPU_INFO.get(cpu)
#     if not info:
#         log.error(f"[cpu :{cpu}] not in {CPU_INFO.keys()}")
#         return []

#     mode = fpu or (info.get("fpu") if info.get("fpu") is not None else "none")

#     flags = []
#     if mode and mode not in ("none", "soft", "hard"):
#         flags.append(f"-mfpu={mode}")
#     abi = "softfp" if mode.startswith("fpv") else ("hard" if mode == "hard" else "soft")
#     flags.append(f"-mfloat-abi={abi}")
#     flags.append("-mthumb" if not thumb else f"-m{thumb}")
#     return flags


# def _arm_llvm_fpu_flags(cpu: str, fpu: str = "none", thumb: str = "") -> list[str]:
#     """ARM LLVM/Clang 目标 FPU 相关标志

#     与 GCC 版 _arm_fpu_flags 的区别：Clang 对 fpv* FPU 使用 hard ABI，
#     而非 GCC 的 softfp。参考 ARM LLVM 官方示例和 Makefile 惯例。
#     """
#     flags = []
#     info = CPU_INFO.get(cpu)
#     arch_ = info.get("arch")
#     # log.info(f"1： info: {info}  {cpu}  {fpu}")
#     if arch_.startswith("armv"):
#         log.info(f"2： info: {flags}")
#         # arch_ = arch_[3:]
#         # flags.append(f"--target=arm-unknown-none-eabi")
#         flags.append(f"--target=arm-arm-none-eabi")
#         # flags.append(f"--target=arm-none-eabi")
#         flags.append(f"-march={info.get('arch')}")
#         # log.info(f"3： info: {flags}")
#     mode = fpu or (info.get("fpu") if info.get("fpu") is not None else "none")

#     if mode and mode not in ("none", "soft", "hard"):
#         flags.append(f"-mfpu={mode}")
#     abi = "softfp" if mode.startswith("fpv") else ("hard" if mode == "hard" else "soft")
#     flags.append(f"-mfloat-abi={abi}")
#     # log.info(f"info 5: {flags}")
#     flags.append("-mthumb" if not thumb else f"-m{thumb}")
#     # flags.append("-mlittle-endian" if not endian or endian == "little" else "-mbig-endian")

#     log.info(f"info 6: {flags}")
#     return flags
