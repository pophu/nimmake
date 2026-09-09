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

"""Helper for quickly building compilation scripts"""

"""
ThirdParties — Third-party component management.

Based on FileGatherer for collecting source files and header directories, supports:
  - Local macros + global macros (auto-merged)
  - Component dependencies (depends_on)
  - Exclusion filtering
"""


import copy
from abc import ABC, abstractmethod
from pathlib import Path

import tomllib

from ..configs import (
    ASM_EXTS,
    C_EXTS,
    CXX_EXTS,
    EXCLUDE_DIRS,
    EXCLUDE_PREFIXES,
    EXCLUDE_SUFFIXES,
    HEADER_EXTS,
    SOURCE_EXTS,
    TOML_PYMAKEX,
    BuildType,
)
from ..gather import FileGatherer, format_include_flags
from ..utils import format_macro_flags, log

# ---------------------------------------------------------------------------
# ThirdParty 基类
# ---------------------------------------------------------------------------

COMMAND_LST = "$TOOL$ $FLAGS$ $_CPPDEFFLAGS $_CPPINCFLAGS$ $PARTY_DEFFLAGS$ $PARTY_INCS$ -c -o TARGET$ $SOURCE$ "


class ThirdParty(ABC):
    """
    用法:
        class MyDriver(ThirdParty):
            def setup(self):
                self.add_macro("USE_MY_DRIVER")
                self.depends_on("core")

        party = MyDriver(name="my_driver", root="./lib/my_driver")
        srcs = party.sources()           # 源文件
        incs = party.include_dirs()       # -I 目录
        flags = party.compile_flags()     # -D 参数
    """

    def __init__(
        self,
        name: str,
        root: str | Path,
        *,
        source_exts: set[str] | None = None,
        header_exts: set[str] | None = None,
        exclude_dirs: list[str | Path] | None = None,
        exclude_prefixes: list[str] | None = None,
        exclude_suffixes: list[str] | None = None,
        recursive: bool = True,
        defines: dict[str, str] | None = None,
        macros: dict[str, str] | None = None,
        global_macros: dict[str, str] | None = None,
        include_macros: dict[str, str] | None = None,
        depends: list[str] | None = None,
        build_type: BuildType = BuildType.OBJECT.name,
        relative: bool = True,  # relative path or absolute path
        params: dict[str, str] | None = None,
        toml: bool = False,
        **kwargs,
    ):
        self.name = name
        # relative abs dir
        # self.dir = Path(dir).resolve()
        self.dir = Path(root)
        # self._build_type = build_type
        self.source_exts = source_exts or SOURCE_EXTS
        self.header_exts = header_exts or HEADER_EXTS
        self.exclude_dirs = exclude_dirs or EXCLUDE_DIRS
        self.exclude_prefixes = exclude_prefixes or EXCLUDE_PREFIXES
        self.exclude_suffixes = exclude_suffixes or EXCLUDE_SUFFIXES
        self.depends = depends or []
        self.recursive = recursive

        self.defines = copy.deepcopy(defines or {})
        self.macros = copy.deepcopy(macros or {})
        self.defines_g = copy.deepcopy(global_macros or {})
        self.include_macros = copy.deepcopy(include_macros or {})
        self.params = copy.deepcopy(params or {})
        self.build_type = build_type

        self.relative = relative or True
        self.toml = toml or False

        self.defines_flags = []
        self.include_macros_flags = []
        self.inc_flags = []
        self._commands = []

        # COMMA
        self.C_PARTY_FLAGS = {}
        self.CXX_PARTY_FLAGS = {}
        self.AS_PARTY_FLAGS = {}

        # self
        self.reflections = []
        self.party_flags = []

        # 收集器
        self._g = FileGatherer(
            source_exts=self.source_exts,
            header_exts=self.header_exts,
            exclude_dirs=self.exclude_dirs,
            exclude_prefixes=self.exclude_prefixes,
            exclude_suffixes=self.exclude_suffixes,
            recursive=self.recursive,
            relative=relative,
        )

        # 源文件 obj reflection
        self.reflections = []

        # 头文件目录
        self.incs = []
        self.srcs = []

        # # 依赖
        # self._depends: list[str] = list(depends or [])

        # # 库
        # self._lib_paths: list[Path] = []
        # self._libs: list[str] = []

        # # 安装目录
        # self._install_dir: Path | None = None

        # 子类自定义
        self.setup()

    # ------------------------------------------------------------------
    # 子类必须实现
    # ------------------------------------------------------------------

    @abstractmethod
    def setup(self) -> None:
        """配置宏、依赖、排除规则等"""
        ...

    @abstractmethod
    def build(self) -> None:
        """编译/处理该组件"""
        ...

    # ------------------------------------------------------------------
    # 构建类型管理
    # ------------------------------------------------------------------
    @property
    def is_static(self) -> bool:
        return self.build_type == BuildType.STATIC.name

    @property
    def is_shared(self) -> bool:
        return self.build_type == BuildType.SHARED.name

    @property
    def is_object(self) -> bool:
        return self.build_type == BuildType.OBJECT.name

    # ------------------------------------------------------------------
    # 文件查询
    # ------------------------------------------------------------------

    def sources(
        self,
        *,
        child_dirs: list[str | Path] | None = None,
        exclude_dirs: list[str | Path] | None = None,
        exclude_prefixes: list[str] | None = None,
        exclude_suffixes: list[str] | None = None,
        recursive: bool | None = None,
    ) -> list[Path]:
        """
        child_dirs: self.dir/ [child_dir]
        example: child_dirs=["Core/1", "Core/2"]
        """
        dir = Path(self.dir)
        # log.error(f"sources dir: {dir}  {exclude_dirs}")
        srcs = self._g.sources(
            dir,
            include_dirs=child_dirs,
            exclude_dirs=exclude_dirs,
            exclude_prefixes=exclude_prefixes,
            exclude_suffixes=exclude_suffixes,
            recursive=recursive,
        )
        # log.debug(f"srcs: {srcs}")
        return srcs

    def headers(
        self,
        *,
        child_dirs: list[str | Path] | None = None,
        exclude_dirs: list[str | Path] | None = None,
        exclude_prefixes: list[str] | None = None,
        recursive: bool | None = None,
    ) -> list[Path]:
        """收集本组件的头文件"""
        dir = Path(self.dir)
        # log.error(f"headers: {dir}   ===")
        incs = self._g.headers(
            dir,
            include_dirs=child_dirs,
            exclude_dirs=exclude_dirs,
            exclude_prefixes=exclude_prefixes,
            recursive=recursive,
        )
        return incs

    def include_dirs(
        self,
        *,
        child_dirs: list[str | Path] | None = None,
        exclude_dirs: list[str | Path] | None = None,
        exclude_prefixes: list[str] | None = None,
        recursive: bool | None = None,
    ) -> list[Path]:
        """收集本组件的头文件目录（-I 参数）"""
        # log.error(f"include_dirs:    === {child_dirs}")
        dir = Path(self.dir)
        self.incs = self._g.include_dirs(
            dir,
            include_dirs=child_dirs,
            exclude_dirs=exclude_dirs,
            exclude_prefixes=exclude_prefixes,
            recursive=recursive,
        )
        return self.incs

    def compile_flags(
        self,
        *,
        include_dirs: list[str | Path] | None = None,
        exclude_dirs: list[str | Path] | None = None,
    ) -> list[str]:
        """返回编译器参数：-I 目录 + -D 宏"""
        incs = self.include_dirs(exclude_dirs=exclude_dirs)
        return (
            format_macro_flags(self.defines)
            # + format_macro_flags(self.defines_g)
            + format_macro_flags(self.include_macros)
            + format_include_flags(incs)
        )

    def set_party_flags(self, flags: list[str]) -> list[str]:
        self.party_flags = flags

    def set_defines_macros_incs(
        self, defines_flags: list[str], include_macros_flags: list[str], inc_flags: list[str]
    ) -> list[str]:
        self.defines_flags = defines_flags
        self.include_macros_flags = include_macros_flags
        self.inc_flags = inc_flags

        # print("=== {}")
        # print(f"=== {self.defines_flags}  {self.include_macros_flags} {self.inc_flags}")

    def info(self) -> str:
        """打印组件信息"""
        srcs = self.sources()
        incs = self.include_dirs()
        return (
            f"ThirdParty({self.name})\n"
            f"  root: {self.dir}\n"
            f"  sources: {len(srcs)}\n"
            f"  inc_dirs: {len(incs)}\n"
            f"  macros: {self.defines}\n"
            f"  depends: {self._depends}\n"
        )

    def get_reflection(self, obj_ext: str = ".o", obj_dir: list[str] = None) -> list:
        """
        get compile command
        get compile reflection
        build_type: HEADER,  give up reflection
        """
        log.info(f"get_reflection  {self.name} -=sources build_type {self.build_type}")
        if obj_dir is None:
            obj_dir = []
        self.reflections = []
        if self.build_type == BuildType.HEADER.name:
            return self.reflections

        # TODO setup() 依据获取,无需触发
        # log.debug(f"get_reflection  {self.name} -=sources  {self.srcs}")
        sources = self.srcs
        # sources = self.sources(
        #     exclude_dirs=self.exclude_dirs, exclude_prefixes=self.exclude_prefixes
        # )

        obj_pth = Path(".")
        for od in obj_dir:
            obj_pth = obj_pth / od
        obj_path = obj_pth / f"{self.name}"
        # log.debug(f"sources: {sources}")

        for src in sources:
            obj = obj_path / f"{src.stem}{obj_ext}"
            # obj = f"{self.name}_{src.stem}{obj_ext}"
            # obj = f"{self.name}_{src.stem}{self.helper._env['OBJ_EXT']}"
            # TODO 处理不同平台路径分隔符问题
            self.reflections.append([src.as_posix(), obj.as_posix()])

    # def _compile_commands_1(
    #     self, tools: dict[str, str], tool_flags: dict[str, list[str]]
    # ) -> list:
    #     """
    #     get compile command
    #     """
    #     self._commands = []

    #     for _refl in self.reflections:
    #         src = str(_refl[0])
    #         obj = str(_refl[1])
    #         tool = "gcc"
    #         src_suff = Path(src).suffix.lower()
    #         if src_suff in C_EXTS:
    #             tool = tools.get("CC", "gcc")
    #             flags = tool_flags.get("CC", [])
    #         elif src_suff in CXX_EXTS:
    #             tool = tools.get("CXX", "g++")
    #             flags = tool_flags.get("CXX", [])
    #         elif src_suff in ASM_EXTS:
    #             tool = tools.get("AS", "as")
    #             flags = tool_flags.get("AS", [])
    #         else:
    #             flags = tool_flags.get(src_suff, [])

    #         # log.error(f"self.inc_flags: {self.inc_flags}")
    #         tool_flags_ = " ".join(flags)
    #         # asm  no  defines
    #         if src_suff not in ASM_EXTS:
    #             defines_ = " ".join(self.defines_flags)
    #         else:
    #             defines_ = ""
    #         include_macros_flags_ = " ".join(self.include_macros_flags)
    #         inc_flags_ = " ".join(self.inc_flags)

    #         # DONOT ADD -o
    #         item_str = f"{tool} -c {tool_flags_} {defines_} {include_macros_flags_} {inc_flags_} "
    #         # if src_suff in ASM_EXTS:
    #         #     log.warn(item_str)
    #         # log.warn(item_str)

    #         item_dct = [item_str, f"{obj}", f"{src}"]

    #         # item_dct.update({"tool": [tool, "-c"]})
    #         # item_dct.update({"toolflag": tool_flags_        })
    #         # item_dct.update({"define": self.defines_flags})
    #         # item_dct.update({"include_macro": self.include_macros_flags})
    #         # item_dct.update({"inc_flag": self.inc_flags})
    #         # item_dct.update({"_o": ["-o"]})
    #         # item_dct.update({"obj": [str(obj)]})
    #         # item_dct.update({"src": [str(src)]})
    #         # item_dct.update({"VALID": 1})

    #         self._commands.append(item_dct)

    def _compile_commands(self, tools: dict[str, str], tool_flags: dict[str, list[str]]) -> list:
        """
        get compile command
        """
        self._commands = []

        for _refl in self.reflections:
            src = str(_refl[0])
            obj = str(_refl[1])
            tool = "gcc"
            src_suff = Path(src).suffix.lower()
            if src_suff in C_EXTS:
                tool = tools.get("CC", "gcc")
                flags = tool_flags.get("CC", [])
            elif src_suff in CXX_EXTS:
                tool = tools.get("CXX", "g++")
                flags = tool_flags.get("CXX", [])
            elif src_suff in ASM_EXTS:
                tool = tools.get("AS", "as")
                flags = tool_flags.get("AS", [])
            else:
                flags = tool_flags.get(src_suff, [])

            # log.error(f"self.inc_flags: {self.inc_flags}")
            tool_flags_ = " ".join(flags)
            # asm  no  defines
            if src_suff not in ASM_EXTS:
                defines_ = " ".join(self.defines_flags)
            else:
                defines_ = ""
            include_macros_flags_ = " ".join(self.include_macros_flags)
            inc_flags_ = " ".join(self.inc_flags)

            # DONOT ADD -o
            # if src_suff in ASM_EXTS:
            #     log.warn(item_str)
            # log.warn(item_str)

            item_dct = {}

            item_dct.update({"tool": tool})
            item_dct.update({"toolflag": tool_flags_})
            item_dct.update({"defines": defines_})
            item_dct.update({"include_macros": include_macros_flags_})
            item_dct.update({"includes": inc_flags_})
            # item_dct.update({"_o": ["-o"]})
            item_dct.update({"out": str(obj)})
            item_dct.update({"in": str(src)})
            # item_dct.update({"VALID": 1})

            self._commands.append(item_dct)

    def _compile_libs(
        self, tools: dict[str, str], tool_flags: dict[str, list[str]], out: str
    ) -> list:
        if not self.is_static and not self.is_shared:
            return None
        out_ = out.as_posix()  # Mac win
        tool = tools.get("AR", "as")
        flags = tool_flags.get("AR", [])
        tool_flags_ = " ".join(flags)
        in_ = [str(ref[1]) for ref in self.reflections]

        item_dct = {}
        item_dct.update({"tool": tool})
        item_dct.update({"toolflag": tool_flags_})
        # item_dct.update({"defines": defines_})
        # item_dct.update({"include_macros": include_macros_flags_})
        # item_dct.update({"includes": inc_flags_})
        # item_dct.update({"_o": ["-o"]})
        item_dct.update({"out": out_})
        item_dct.update({"in": " ".join(in_)})
        return item_dct

    def DependOn(self, party: str | list[str] = None) -> list[str]:
        if party is None:
            return self
        if isinstance(party, str):
            self.depends.append(party)
        if isinstance(party, ThirdParty):
            self.depends.append(party.name)
        if isinstance(party, list):
            for _p in party:
                if isinstance(_p, str):
                    self.depends.append(_p)
                if isinstance(_p, ThirdParty):
                    self.depends.append(_p.name)
        return self

    def get_track_flags(
        self, cflags: list[str], cxxflags: list[str], asflags: list[str]
    ) -> dict[str, object]:
        """
        track flags of party  ， cflag cxxflag
        """
        dct = {
            "flags": {
                "CFLAGS": cflags,
                "CXXFLAGS": cxxflags,
                "ASFLAGS": asflags,
            }
        }
        return dct

    def add_srcs(self, srcs: list[str]) -> None:
        return

    def remove_src(self, srcs: list[str]) -> None:
        return

    def add_incs(self, incs: list[str]) -> None:
        return

    def remove_inc(self, srcs: list[str]) -> None:
        return

    def clone(self):
        return copy.deepcopy(self)


# ---------------------------------------------------------------------------
# 常用组件子类
# ---------------------------------------------------------------------------


class GenericParty(ThirdParty):
    """通用组件：默认空实现，适合快速使用"""

    def setup(self) -> None:
        """
        If there is PYMAKEX.toml file， read config
        """
        pymake_toml = self.dir / TOML_PYMAKEX
        if pymake_toml.exists():
            with open(pymake_toml, "rb") as f:
                data = tomllib.load(f)
            # log.debug(f"{TOML_PYMAKEX} {data}")
            # srcs = data.get("target", {}).get("srcs", [])
            # incs = data.get("target", {}).get("incs", [])
            # defines = data.get("target", {}).get("defines", [])

            # log.debug(f"{TOML_PYMAKEX} {incs}  {type(incs)}")
            # log.debug(f"{TOML_PYMAKEX} {defines}  {type(defines)}")
            # log.debug(f"{TOML_PYMAKEX} {srcs}  {type(srcs)}")

            tgt = data.get("target", [])
            if tgt and isinstance(tgt, dict):
                srcs = tgt.get("srcs", [])
                incs = tgt.get("incs", [])
                defines = tgt.get("defines", [])
                include_macros = tgt.get("include_macros", [])
                if self.build_type != BuildType.HEADER.name:
                    for src in srcs:
                        self.srcs.append(self.dir / src)

                for inc in incs:
                    self.incs.append(self.dir / inc)
                # log.debug(f"{TOML_PYMAKEX} {self.srcs} {self.incs}")
                if defines and isinstance(defines, list):
                    for df in defines:
                        if not df:
                            continue
                        df_lst = df.split("=")
                        if len(df_lst) != 2:
                            continue
                        self.defines.update({df_lst[0]: df_lst[1]})
                if include_macros and isinstance(include_macros, list):
                    for macro in include_macros:
                        if not macro:
                            continue
                        macro_lst = macro.split("=")
                        if len(macro_lst) != 2:
                            continue
                        self.include_macros.update({macro_lst[0]: macro_lst[1]})
                # log.debug(f"{TOML_PYMAKEX} {self.include_macros}")
        else:
            self.incs = self.include_dirs(
                child_dirs=None,
                exclude_dirs=self.exclude_dirs,
                exclude_prefixes=self.exclude_prefixes,
                recursive=self.recursive,
            )
            if self.build_type == BuildType.HEADER.name:
                return
            self.srcs = self.sources(
                child_dirs=None,
                exclude_dirs=self.exclude_dirs,
                exclude_prefixes=self.exclude_prefixes,
                exclude_suffixes=self.exclude_suffixes,
                recursive=self.recursive,
            )

        # log.debug(f"setup....  PARTYNAME: {self.name}")
        # log.debug(f" {self.srcs}")
        # log.debug(f" {self.incs}")
        pass

    # def __toml(self):
    #     dct = {
    #         "target": {
    #             "srcs": [],
    #             "incs": [],
    #         },
    #     }
    #     pass

    def build(self) -> None:
        pass


class DefaultParty(ThirdParty):
    """通用组件：默认空实现，适合快速使用"""

    def setup(self) -> None:
        # log.debug(f"_DEFAULT....")
        pass

    def build(self) -> None:
        pass


class CommonDir(ThirdParty):
    """
    not recursive dir
    """

    def __init__(self, name: str, dir: str | Path, **kw):
        kw.setdefault("recursive", False)
        super().__init__(name, dir, **kw)

    def setup(self) -> None:
        self.incs = self.include_dirs()
        pass

    def build(self, order: list[ThirdParty]) -> None:
        pass


# # ---------------------------------------------------------------------------
# # 全局宏注册表（跨组件共享）
# # ---------------------------------------------------------------------------

# _GLOBAL_MACROS: dict[str, str] = {}


# def set_global_macro(key: str, value: str = "") -> None:
#     """设置全局宏（所有 ThirdParty 实例共享）"""
#     _GLOBAL_MACROS[key] = value


# def get_global_macros() -> dict[str, str]:
#     """获取全局宏"""
#     return dict(_GLOBAL_MACROS)


# def clear_global_macros() -> None:
#     """清除全部全局宏"""
#     _GLOBAL_MACROS.clear()


# ---------------------------------------------------------------------------
# 全局宏注册表（跨组件共享）
# ---------------------------------------------------------------------------

# PARTIES_DCT: dict[str, str] = {
#     "GENERIC": "GenericParty",
#     "COMMONDIR": "CommonDir",
# }
