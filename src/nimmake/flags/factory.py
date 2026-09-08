# """
# FlagsFactory — 编译标志工厂主类
# """

# from __future__ import annotations

# from typing import Dict, List, Optional

# from . import chips
# from .backends import BACKENDS
# from .config import FlagsConfig
# from .flags import Flags, fmt_define


# class FlagsFactory:
#     """
#     编译标志工厂。

#     Usage:
#         f = FlagsFactory("armgcc", cpu="cortex-m4")
#         f = FlagsFactory("armgcc", model="STM32F407")
#         f = FlagsFactory("gcc", opt="O2", dbg=True, linkscript="stm32f4.ld")

#         f.cflags     # C 编译标志
#         f.cxxflags   # C++ 编译标志
#         f.asflags    # 汇编标志
#         f.arflags    # 归档标志
#         f.ldflags    # 链接标志
#         f.defines    # 宏定义
#     """

#     def __init__(
#         self,
#         toolchain: str = "",
#         model: str = "",
#         vendor: str = "",
#         *,
#         cpu: str = "",
#         arch: str = "",
#         fpu: str = "",
#         abi: str = "",
#         opt: str = "O0",
#         dbg: bool = False,
#         warn: str = "",
#         std_c: str = "",
#         std_cxx: str = "",
#         data_sections: bool = False,
#         func_sections: bool = False,
#         defines: dict[str, str] | None = None,
#         linkscript: str = "",
#         mmap: str = "",
#         gc_sections: bool = False,
#         nostartfiles: bool = False,
#         nostdlib: bool = False,
#         shared: bool = False,
#         library_path: list[str] | None = None,
#         specs: list[str] | None = None,
#         lto: str = "",
#         semihost: bool = False,
#         sysroot: str = "",
#     ):
#         # 统一装入 FlagsConfig
#         self._cfg = FlagsConfig(
#             # toolchain=toolchain,
#             cpu=cpu,
#             arch=arch,
#             fpu=fpu,
#             abi=abi,
#             # model=model,
#             # vendor=vendor,
#             opt=opt,
#             dbg=dbg,
#             warn=warn,
#             std_c=std_c,
#             std_cxx=std_cxx,
#             data_sections=data_sections,
#             func_sections=func_sections,
#             defines=defines or {},
#             linkscript=linkscript,
#             mmap=mmap,
#             gc_sections=gc_sections,
#             nostartfiles=nostartfiles,
#             nostdlib=nostdlib,
#             shared=shared,
#             library_path=library_path or [],
#             specs=specs or [],
#             lto=lto,
#             semihost=semihost,
#             sysroot=sysroot,
#         )
#         # self.model = model
#         # self.vendor = vendor
#         self._init(toolchain, vendor, model)
#         # self._backend = None  # toolchain backend 实例

#     # move to env compiler
#     @classmethod
#     def from_config(cls, toolchain: str, cfg: FlagsConfig) -> FlagsFactory:
#         """从 FlagsConfig 对象创建"""
#         f = cls.__new__(cls)
#         f._cfg = cfg.clone()
#         f._init(toolchain)
#         return f

#     def _init(self, toolchain: str, vendor: str = "", model: str = "") -> None:
#         # 自动检测
#         # if not toolchain:
#         #     toolchain = detect.detect()
#         self.model = model
#         self.vendor = vendor

#         # 型号 → CPU
#         cfg = self._cfg
#         if self.model and not cfg.cpu:
#             resolved = chips.chip_by_model(self.model)
#             if resolved:
#                 cfg.cpu = resolved
#             else:
#                 raise ValueError(f"未知厂商型号: {cfg.model}")

#         # CPU → arch / fpu / abi
#         cinfo = chips.cpu_arch(cfg.cpu) if cfg.cpu else None
#         if cinfo:
#             cfg.arch = cfg.arch or cinfo.get("arch", "")
#             cfg.fpu = cfg.fpu or cinfo.get("fpu", "")
#             cfg.abi = cfg.abi or cinfo.get("abi", "")

#         cls = BACKENDS.get(toolchain)
#         if cls is None:
#             raise ValueError(f"未知工具链: {toolchain}，可选: {list(BACKENDS.keys())}")

#         self._backend = cls(cpu=cfg.cpu, arch=cfg.arch, fpu=cfg.fpu, abi=cfg.abi)
#         self._flags: Flags | None = None
#         self._toolchain = toolchain

#     # ------------------------------------------------------------------
#     # 重建
#     # ------------------------------------------------------------------

#     def rebuild(self) -> Flags:
#         c = self._cfg
#         self._flags = self._backend.collect(
#             opt=c.opt,
#             dbg=c.dbg,
#             warn=c.warn,
#             std_c=c.std_c,
#             std_cxx=c.std_cxx,
#             data_sections=c.data_sections,
#             func_sections=c.func_sections,
#             defines=dict(c.defines),
#             linkscript=c.linkscript,
#             mmap=c.mmap,
#             gc_sections=c.gc_sections,
#             nostartfiles=c.nostartfiles,
#             nostdlib=c.nostdlib,
#             shared=c.shared,
#             library_path=c.library_path,
#             specs=c.specs,
#             lto=c.lto,
#             semihost=c.semihost,
#             sysroot=c.sysroot,
#         )
#         return self._flags

#     @property
#     def flags(self) -> Flags:
#         if self._flags is None:
#             self.rebuild()
#         return self._flags

#     @property
#     def config(self) -> FlagsConfig:
#         """导出当前配置（只读快照）"""
#         return self._cfg.clone()

#     # ------------------------------------------------------------------
#     # 属性
#     # ------------------------------------------------------------------

#     @property
#     def cflags(self) -> list[str]:
#         return self.flags.cflags[:] + [fmt_define(k, v) for k, v in self._cfg.defines.items()]

#     @property
#     def cxxflags(self) -> list[str]:
#         return self.flags.cxxflags[:] + [fmt_define(k, v) for k, v in self._cfg.defines.items()]

#     @property
#     def asflags(self) -> list[str]:
#         return self.flags.asflags[:] + [fmt_define(k, v) for k, v in self._cfg.defines.items()]

#     @property
#     def arflags(self) -> list[str]:
#         return self.flags.arflags[:]

#     @property
#     def defines(self) -> dict[str, str]:
#         return dict(self._cfg.defines)

#     @defines.setter
#     def defines(self, d: dict[str, str]) -> None:
#         self._cfg.defines = d
#         self._flags = None

#     @property
#     def ldflags(self) -> list[str]:
#         return self.flags.ldflags[:]

#     @property
#     def all(self) -> dict[str, object]:
#         return {
#             "cflags": self.cflags,
#             "cxxflags": self.cxxflags,
#             "asflags": self.asflags,
#             "arflags": self.arflags,
#             "defines": self.defines,
#             "ldflags": self.ldflags,
#         }

#     def __repr__(self) -> str:
#         return f"<FlagsFactory toolchain={self._toolchain}>"

#     # ------------------------------------------------------------------
#     # 更新参数（自动清除缓存）
#     # ------------------------------------------------------------------

#     def _dirty(self) -> None:
#         self._flags = None

#     def update(self, **kwargs) -> FlagsFactory:
#         """
#         直接修改 self._cfg 的字段，参数名与 FlagsConfig 一致。

#         用法:
#             f.update(opt="Os", dbg=False)
#             f.update(linkscript="new.ld", gc_sections=True, defines={"NDEBUG": ""})
#         """
#         for k, v in kwargs.items():
#             if hasattr(self._cfg, k):
#                 setattr(self._cfg, k, v)
#             else:
#                 raise AttributeError(f"FlagsConfig 无此字段: {k}")
#         self._dirty()
#         return self

#     def set_opt(self, opt: str) -> FlagsFactory:
#         self._cfg.opt = opt
#         self._dirty()
#         return self

#     def set_dbg(self, dbg: bool) -> FlagsFactory:
#         self._cfg.dbg = dbg
#         self._dirty()
#         return self

#     def set_warn(self, warn: str) -> FlagsFactory:
#         self._cfg.warn = warn
#         self._dirty()
#         return self

#     def set_std(self, std_c: str = "", std_cxx: str = "") -> FlagsFactory:
#         self._cfg.std_c = std_c
#         self._cfg.std_cxx = std_cxx
#         self._dirty()
#         return self

#     def set_sections(self, data: bool = False, func: bool = False) -> FlagsFactory:
#         self._cfg.data_sections = data
#         self._cfg.func_sections = func
#         self._dirty()
#         return self

#     def set_linkscript(self, path: str) -> FlagsFactory:
#         self._cfg.linkscript = path
#         self._dirty()
#         return self


# def new_flags(
#     toolchain: str = "",
#     *,
#     cpu: str = "",
#     arch: str = "",
#     fpu: str = "",
#     abi: str = "",
#     model: str = "",
#     vendor: str = "",
#     opt: str = "O0",
#     dbg: bool = False,
#     warn: str = "",
#     std_c: str = "",
#     std_cxx: str = "",
#     data_sections: bool = False,
#     func_sections: bool = False,
#     defines: dict[str, str] | None = None,
#     linkscript: str = "",
#     mmap: str = "",
#     gc_sections: bool = False,
#     nostartfiles: bool = False,
#     nostdlib: bool = False,
#     shared: bool = False,
#     library_path: list[str] | None = None,
#     specs: list[str] | None = None,
#     lto: str = "",
#     semihost: bool = False,
#     sysroot: str = "",
# ) -> Flags:
#     """快速获取标志的便捷函数"""
#     f = FlagsFactory(
#         toolchain,
#         cpu=cpu,
#         arch=arch,
#         fpu=fpu,
#         abi=abi,
#         model=model,
#         vendor=vendor,
#         opt=opt,
#         dbg=dbg,
#         warn=warn,
#         std_c=std_c,
#         std_cxx=std_cxx,
#         data_sections=data_sections,
#         func_sections=func_sections,
#         defines=defines,
#         linkscript=linkscript,
#         mmap=mmap,
#         gc_sections=gc_sections,
#         nostartfiles=nostartfiles,
#         nostdlib=nostdlib,
#         shared=shared,
#         library_path=library_path,
#         specs=specs,
#         lto=lto,
#         semihost=semihost,
#         sysroot=sysroot,
#     )
#     return f.flags
