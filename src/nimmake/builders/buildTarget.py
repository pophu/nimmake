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

"""BuildTarget"""

from pathlib import Path
from typing import Any

from nimmake.configs import PARTY_LIB_PREFIX, BuildType
from nimmake.thirdParties import ThirdParty
from nimmake.utils import (
    format_include_flags,
    format_lib_pathes_flags,
    format_libs_flags,
    format_macro_flags,
    log,
)

from .base import Targets


class BuildTargetCommands:
    """
    parse parties to build target
    """

    def __init__(
        self,
        helper: dict[str, Any] = None,
        target: str | Targets = None,
        parties: dict[str, ThirdParty] = None,
        target_type: str = "TARGETS",
    ):
        self.target_type = target_type
        if not self.target_type:
            self.target_type = "TARGETS"
        self.helper = helper
        self.target = target
        if self.target:
            self.target_type = self.target.typ
        self.target_out = self.target.name

        # BUILD DIR OBJDIR
        self.build_dir = Path(".") / self.helper["BUILDDIR"]
        self.obj_dir = Path(".") / self.helper["BUILDDIR"] / self.helper["OBJDIR"]
        if not self.obj_dir.exists():
            self.obj_dir.mkdir(parents=True, exist_ok=True)

        self.parties = parties
        self.parties_valid = {}
        self.order_parties = []
        self.commands_just_target = {}
        self.commands = {}
        self.party_libs = []

    def run(self):
        log.debug(f"run   {self.target}  {self.target_type} ")
        if self.target_type == "":
            return self.commands

        self.lib_by_target = []
        if self.target_type == "TARGETS":
            # log.debug(f"target_type: ==  {self.target_type}  ")
            # log.debug(f"__gen_cache  ... 遍历party ， 因为不实际编译，最终builder控制编译")
            self.target_out = self.build_dir / f"{self.target.name}{self.helper['TARGET_SUFFIX']}"
        if self.target_type == "STATIC":
            self.target_out = self.obj_dir / f"{self.target.name}{self.helper['STATIC_LIB_EXT']}"
        if self.target_type == "SHARED":
            self.target_out = self.obj_dir / f"{self.target.name}{self.helper['SHARED_LIB_EXT']}"

        self.target_out = self.target_out.as_posix()
        self.__valid_parties()
        self.__commands_for_valid_parties()

        self.gen_cache()
        return self.commands

    def __valid_parties(self):
        """
        target_commands_and_valid_parties
        """
        if self.target_type == "TARGETS":
            self.parties_valid = self.parties
            return
        if self.target_type in ["STATIC", "SHARED"]:
            # parties build_type = BuildType.HEADER.name, except lib
            for party in self.parties.values():
                if party.name.upper() == self.target.name.upper():
                    party.build_type = self.target_type
                    self.parties_valid.update({party.name: party.clone()})
                    continue
                party.build_type = BuildType.HEADER.name
                # log.error(f"::__valid_parties {party.name} -> {party.build_type} ")
            valid_names = list(self.parties_valid.keys())
            # valid parites , build_typ
            for party in valid_names:
                party_deps = self.parties_valid[party].depends
                for deps in party_deps:
                    if deps not in self.parties_valid:
                        self.parties_valid.update({deps: self.parties[deps].clone()})
                        if deps not in valid_names:
                            self.parties_valid[deps].build_type = BuildType.HEADER.name

        # for party in self.parties_valid.values():
        #     log.debug(f"::__valid_parties {party.name} -> {party.build_type} ")
        # for party in self.parties.values():
        #     log.info(f"::__parties {party.name} -> {party.build_type} ")

    def __commands_for_valid_parties(self):
        self.resolve_order()
        self.__parties_reflection()
        # log.debug(f"after  __parties_reflection ")

        self.__parties_flags()
        # log.debug(f"after  __parties_flags")

        # 处理 lib  libdir
        self._libs = self.__get_libs()
        self._lib_pathes = self.__get_lib_pathes()

        # all compile commands  party_libs
        self._compile_commands = []
        # self.get_compile_commands()
        self.get_compile_commands()

    def resolve_order(self) -> list[ThirdParty]:
        """
        拓扑排序：按依赖关系排序组件（被依赖的排前面）
        使用三色标记法（白=未访问，灰=递归栈中，黑=已完成）检测循环依赖
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        # log.debug(f"resolve_order  {self.parties}")
        name_map: dict[str, ThirdParty] = self.parties
        color: dict[str, int] = dict.fromkeys(name_map, WHITE)
        self.order_parties: list[ThirdParty] = []
        # log.warn(f"all 组件  {name_map} ")

        def _dfs(name: str) -> None:
            if color.get(name) == BLACK:
                return
            if color.get(name) == GRAY:
                # 检测到循环依赖：当前 name 在递归栈中再次出现
                log.warn(f"循环依赖检测: 组件 '{name}' 存在互相依赖，请检查 depends 配置")
                return
            color[name] = GRAY
            p = name_map.get(name)
            if p is None:
                color[name] = BLACK
                return
            for dep in p.depends:
                if dep not in name_map:
                    log.error(f"组件 '{name}' 依赖了不存在的组件 '{dep}'，已跳过")
                    continue
                _dfs(dep)
            color[name] = BLACK
            self.order_parties.append(p)

        for v in self.parties.values():
            _dfs(v.name)
        # log.info(f"order_parties: {self.order_parties}")
        return self.order_parties

    def __parties_reflection(self) -> None:
        """
        get parties reflect , incs
        build_type: HEADER,  give up reflection
        transfer new build_type, decic
        """
        # log.error(f"__parties_reflection  ")
        obj_ext = self.helper["OBJ_EXT"]
        obj_dir = [self.helper["BUILDDIR"], self.helper["OBJDIR"]]
        for party in self.parties.values():
            # log.warn(f" __parties_reflection {party.build_type}")
            party.get_reflection(obj_ext, obj_dir)
            # log.error(f"party: {party.name}, build_type: {party.build_type}")
            # log.error(f"party: {party.name}, refl: {party.reflections}")
            pass

    def __parties_flags(self) -> None:
        """
        all module
        """
        for party in self.parties.values():
            # log.error(f"party: {party.name}, depends: {party.depends}")
            incs = []
            defines = {}
            incs_, defines_, _ = self._party_incs_macros(party)
            incs += incs_
            defines.update(defines_)

            # TODO add  helper's defines and INCS
            # if self.helper["DEFINES"]:
            #     defines.update(self.helper["DEFINES"])
            # if self.helper["INCS"]:
            #     log.error(f"system incs: {self.helper['INCS']}")
            #     for inc in self.helper["INCS"]:
            #         if inc not in incs:
            #             incs.append(inc)

            # add total defines and include_macros
            # include_macros = party.include_macros
            # log.error(f" incs: {incs_}, defines: {defines_}")
            party.set_defines_macros_incs(
                format_macro_flags(defines),
                format_macro_flags(party.include_macros),
                format_include_flags(incs),
            )
        # log.debug(f"complete __parties_flags  ")
        pass

    def get_compile_commands(self) -> list[dict[str, object]]:
        """
        get compile commands by party
        include party libs
        """
        self._compile_commands = []
        tools = {
            "CC": self.helper["CC"],
            "CXX": self.helper["CXX"],
            "AS": self.helper["AS"],
            "AR": self.helper["AR"],
        }
        toolflags = {
            "CC": self.helper["CFLAGS"],
            "CXX": self.helper["CXXFLAGS"],
            "AS": self.helper["ASFLAGS"],
            "AR": self.helper["ARFLAGS"],
        }
        # log.warn(f"party: {self.parties}")
        for party in self.parties.values():
            party._compile_commands(tools, toolflags)
            self._compile_commands += party._commands

        for party in self.parties.values():
            out = self._get_party_lib_path(party.name, party.build_type)
            lib = party._compile_libs(tools, toolflags, out)
            # log.debug(f"lib: {lib}")
            if lib:
                self.party_libs.append(lib)

    def gen_cache(self) -> list[dict[str, object]]:
        # 缓存文件不存在
        # {OBJECTS, TARGETS, ACTIONS, FLAGS}
        self.commands_just_target = self.__gen_targets()

        libs = self.__gen_cache_party_libs()
        objects = self.__gen_cache_objs()

        flags = {
            "CFLAGS": self.helper["CFLAGS"],
            "CXXFLAGS": self.helper["CXXFLAGS"],
            "ASFLAGS": self.helper["ASFLAGS"],
        }
        self.commands = {}
        self.commands.update({"FLAGS": flags})

        self.commands.update({"OBJECTS": objects})
        self.commands.update({"TARGETS": self.commands_just_target})
        self.commands.update({"LIBS": libs})
        self.commands.update({"deps": {}})

        # log.error(f"self.commands: {self.commands_just_target}")
        # log.info(f"self.commands: {self.commands['OBJECTS']}")
        # log.info(f"self.commands: {self.commands['TARGETS']}")
        # log.info(f"self.commands: {self.commands['LIBS']}")

        return self.commands
        pass

    def __gen_cache_objs2(self) -> list[dict[str, object]]:
        pass

    def __gen_cache_objs(self) -> list[dict[str, object]]:
        objects = {}
        # log.warn(f"self._compile_commands ====== {self._compile_commands}")
        for _c_comm_dct in self._compile_commands:
            out_ = _c_comm_dct.get("out", "")
            in_ = _c_comm_dct.get("in", "")
            tool = _c_comm_dct.get("tool", "")
            flag = _c_comm_dct.get("toolflag", "")
            defines = _c_comm_dct.get("defines", "")
            include_macros = _c_comm_dct.get("include_macros", "")
            includes = _c_comm_dct.get("includes", "")
            # log.error(f"includes ====== {in_}  {type(in_)} {Path(in_).resolve()}  ")
            # tm_stamp = Path(in_).stat().st_mtime  # TODO 文件时间戳还是当时时间戳，还是obj时间戳
            # tm_stamp = time.time()
            cmd_str = f"{tool} -c {flag} {defines} {include_macros} {includes} "
            # objects.update({out_: [cmd_str, in_, tm_stamp]})
            objects.update({out_: [cmd_str, in_, "OBJECTS"]})
        return objects

    def __gen_cache_party_libs(self) -> list[dict[str, object]]:
        libs = {}
        for party in self.party_libs:
            out = party.get("out", "")
            in_ = party.get("in", "")
            flags = party.get("tool", "")
            flags += " " + party.get("toolflag", "")
            # flags += " " + in_
            libs.update({out: [flags, in_, "LIBS"]})
        return libs
        pass

    def __gen_targets(self) -> list[dict[str, object]]:
        log.debug(f"__gen_targets ====== TYPE={self.target_type}")
        targets = {}
        if self.target and self.target.typ == "TARGETS":
            cmd = self.get_target_commands()
            out = cmd["target"][0]
            flags = " ".join(cmd["tool"])
            flags += " "
            flags += " ".join(cmd["toolflags"])
            flags += " "
            flags += " ".join(cmd["obj"])
            flags += " "
            flags += " ".join(cmd["libs"])
            flags += " "
            flags += " ".join(cmd["libpathes"])
            src = " ".join(cmd["obj"])
            # log.error(f" {cmd} ")
            # log.error(f" {flags} ")
            # log.error(f"  {src}")
            targets.update({out: [flags, src, "TARGETS"]})

        # static, shared
        elif self.target and self.target.typ in ["STATIC", "SHARED"]:
            out = self.target
            libs_ = self.get_tgt_lib_commands()
            for k, v in libs_.items():
                targets.update({k: v})
        # log.debug(f"targets: {targets}")
        return targets

    def get_tgt_lib_commands(self) -> list[dict[str, object]]:
        """
        get target commands
        judge , if need to update, add new time stamp
        """
        cmd_dct = {}
        self.parties_valid = {}
        if self.target_type == "TARGETS":
            for party in self.parties.values():
                if (
                    party.build_type == BuildType.STATIC.name
                    or party.build_type == BuildType.SHARED.name
                ):
                    # hard copy party
                    self.parties_valid.update({party.name: party.clone})
        if self.target_type in ["STATIC", "SHARED"]:
            for party in self.parties.values():
                if party.name.upper() == self.target.name.upper():
                    party.build_type = self.target_type
                    self.parties_valid.update({party.name: party.clone()})
        # log.debug(f"parties_valid: {self.parties_valid}")

        for party in self.parties_valid.values():
            party_cmd = self.__get_lib_commands_by_party(party)
            # log.warn(f"party_cmd: {party_cmd}")
            out = party_cmd.get("out_", "")
            cmd_lst = []
            cmd_ = f"{self.helper['AR']} "
            cmd_ += " ".join(self.helper["ARFLAGS"])
            # cmd_ += f" {out} "
            objs = party_cmd.get("in_", [])
            obj_str = " ".join(objs)
            # cmd_ += obj_str
            cmd_lst.append(cmd_)
            cmd_lst.append(obj_str)
            cmd_lst.append(self.target_type)
            cmd_dct.update({out: cmd_lst})

        # log.debug(f"TARGet LIB cmd_dct: {cmd_dct}")
        return cmd_dct
        pass

    def get_target_commands(self) -> list[dict[str, object]]:
        """
        get target commands
        judge , if need to update, add new time stamp
        """
        if not self.target:
            return []
        cmd_dct = {}
        cmd_dct.update({"toolflags": self.helper["LINKFLAGS"]})

        cmd_dct.update({"tool": [self.helper["LD"]]})
        cmd_dct.update({"target": [self.target_out]})

        objs = []
        lib = set()
        lib_pathes = set()

        for party in self.parties.values():
            # log.error(f"party: {party.build_type}")
            if party.is_object:
                for refl in party.reflections:
                    # refl[1]
                    objs.append(refl[1])
            if party.is_static:
                libpath_ = self._get_lib_path(party.name, party.build_type)
                prefix = f"{PARTY_LIB_PREFIX}" if PARTY_LIB_PREFIX else ""
                lib.add(f"-l{prefix}{party.name.lower()}")
                lib_pathes.add(f"-L{libpath_.parent.as_posix()}")
                # log.warn(f"  == {len(objs)}  {lib}  {lib_pathes}  ")
            if party.is_shared:
                libpath_ = self._get_lib_path(party.name, party.build_type)
                prefix = f"{PARTY_LIB_PREFIX}" if PARTY_LIB_PREFIX else ""
                lib.add(f"-l{prefix}{party.name}")
                lib_pathes.add(f"-L{libpath_.parent.as_posix()}")

        cmd_dct.update({"obj": objs})
        # cmd_dct.update({"SUFF": self.helper["TARGET_SUFFIX"]})
        # log.error(f"lib: {objs}")
        for lib_ in self.helper["LIBS"]:
            lib.add(f"-l{lib_}")
        cmd_dct.update({"libs": list(lib)})
        for libpath_ in self.helper["LIBPATH"]:
            lib_pathes.add(f"-L{libpath_}")
        cmd_dct.update({"libpathes": list(lib_pathes)})
        # cmd_dct.update({"TARGET": self.helper["TARGET_NAME"]})
        cmd_dct.update({"VALID": 1})

        # log.debug(f"cmd_dct: {cmd_dct}  {self.helper['LIBS']}")
        # self._compile_commands.append(cmd_dct)
        return cmd_dct

    def __get_lib_commands_by_party(self, party: ThirdParty) -> list[dict[str, object]]:
        cmd_dct = {}
        cmd_lst = []
        # if target is static shared, skip
        if self.target_type in ["STATIC", "SHARED"]:
            return
        if party.build_type == BuildType.STATIC.name:
            libname = self._get_lib_path(party.name).as_posix()
            cmd_str_ = f"{self.helper['AR']} "
            cmd_str_ += " ".join(self.helper["ARFLAGS"])
            cmd_str_ += f" {str(libname)} "
            cmd_dct.update({"tool": [self.helper["AR"]]})
            cmd_dct.update({"toolflags": self.helper["ARFLAGS"]})
            obj = []
            for refl in party.reflections:
                obj.append(str(refl[1]))
            # cmd_dct.update({"_o": ["-o"]})
            # cmd_dct.update({"obj": [str(self._get_lib_path(party.name))]})
            obj_str = " ".join(obj)
            cmd_dct.update({"out_": libname})
            # cmd_dct.update({"out": libname})
            cmd_dct.update({"in_": obj})
            cmd_dct.update({"VALID": 1})
            cmd_str_ += " "
            cmd_str_ += obj_str
            cmd_lst += [cmd_str_, obj_str, "STATIC"]
        # log.debug(f"cmd_lst: {cmd_lst}")

        if party.build_type == BuildType.SHARED.name:
            libname = self._get_lib_path(party.name, "shared").as_posix()
            # f"{self.helper['AR']} {self._get_lib_path(party.name, 'shared')}"
            cmd_str_ = f"{self.helper['AR']} rcs {libname} "
            cmd_str_ += " ".join(self.helper["ARFLAGS"])
            cmd_dct.update({"tool": [self.helper["AR"]]})
            cmd_dct.update({"toolflags": self.helper["ARFLAGS"]})
            obj = []
            for refl in party.reflections:
                obj.append(str(refl[1]))
            obj_str = " ".join(obj)
            cmd_dct.update({"_o": ["-o"]})
            # cmd_dct.update({"obj": [str(self._get_lib_path(party.name, "shared"))]})
            cmd_dct.update({"out_": libname})
            cmd_dct.update({"in_": obj})
            cmd_dct.update({"VALID": 1})
            cmd_str_ += " "
            cmd_str_ += obj_str
            cmd_lst += [cmd_str_, obj_str, "SHARED"]
        # log.debug(f"cmd_lst: {cmd_dct}")
        return cmd_dct

    def _party_incs_macros(self, party: ThirdParty) -> tuple[list[str], dict[str, str]]:
        """
        return incs, defines_g , defines
        recursive get all incs, defines
        sort incs, defines_g
        """

        defines_g_ = party.defines_g
        incs_ = self.merged_include_dirs_for(party, self.order_parties)
        defines_ = self.merged_defines_for(party, self.order_parties)

        for inc in self.helper["INCPATH"]:
            incs_.append(inc)

        return incs_, defines_, defines_g_
        pass

    def _get_party_lib_path(self, partyname: str, lib_type: str = "STATIC") -> Path:
        pth = Path(".")
        if self.helper["BUILDDIR"]:
            pth = pth / self.helper["BUILDDIR"].strip("")
        if self.helper["LIBDIR"]:
            pth = pth / self.helper["LIBDIR"].strip("")
        if lib_type == BuildType.STATIC.name:
            prefix = f"{PARTY_LIB_PREFIX}" if PARTY_LIB_PREFIX else ""
            return pth / f"lib{prefix}{partyname.lower()}{self.helper['STATIC_LIB_EXT']}"
        if lib_type == BuildType.SHARED.name:
            prefix = f"{PARTY_LIB_PREFIX}" if PARTY_LIB_PREFIX else ""
            return pth / f"lib{prefix}{partyname.lower()}_{self.helper['SHARED_LIB_EXT']}"

    def _get_lib_path(self, partyname: str, lib_type: str = "STATIC") -> Path:
        pth = Path(".")
        if self.helper["BUILDDIR"]:
            pth = pth / self.helper["BUILDDIR"].strip("")
        if self.helper["LIBDIR"]:
            pth = pth / self.helper["LIBDIR"].strip("")
        if lib_type == BuildType.STATIC.name:
            return pth / f"lib{partyname.lower()}{self.helper['STATIC_LIB_EXT']}"
        if lib_type == BuildType.SHARED.name:
            return pth / f"lib{partyname.lower()}_{self.helper['SHARED_LIB_EXT']}"

    def __get_libs(self) -> list[str]:
        """
        get libs from extra_libs and lib_dirs
        """
        return format_libs_flags(self.helper["LIBS"])

    def __get_lib_pathes(self) -> list[str]:
        """
        get lib_pathes from extra_lib_pathes and lib_dirs
        """
        return format_lib_pathes_flags(self.helper["LIBPATH"])

    # ---------------------------------------------------------------------------
    # defines 合并
    # ---------------------------------------------------------------------------

    def merged_defines_for(self, party: ThirdParty, order: list[ThirdParty]) -> dict[str, str]:
        """收集组件的全部宏（自身 + 所有依赖组件的全局宏）"""
        defines: dict[str, str] = {}
        name_map = {p.name: p for p in order}
        visited: set[str] = set()

        def _collect(name: str) -> None:
            if name in visited:
                return
            visited.add(name)
            p = name_map.get(name)
            if p is None:
                return
            for dep in p.depends:
                _collect(dep)
            # 全局宏（来自依赖）
            for k, v in p.defines.items():
                defines[k] = v

        _collect(party.name)
        return defines

    def merged_include_dirs_for(self, party: ThirdParty, order: list[ThirdParty]) -> list[Path]:
        """收集组件的全部头文件目录（自身 + 所有依赖组件）"""
        inc_dirs: set[Path] = set()
        seen: set[Path] = set()
        name_map = {p.name: p for p in order}
        visited: set[str] = set()
        # log.debug(f"party: {party.name}, depends: {party.depends} name_map: {name_map}")

        def _collect(name: str) -> None:
            # log.warn(f"p : {name}  visited: {visited}  ")
            if name in visited:
                return
            visited.add(name)
            p = name_map.get(name)
            if p is None:
                return
            # log.debug(f"p : {p.depends}    ")
            for dep in p.depends:
                _collect(dep)
            # log.debug(f"p : {p.name} {p.include_dirs()}   ")
            # for d in p.include_dirs():
            for d in p.incs:
                if d not in seen:
                    seen.add(d.as_posix())
                    inc_dirs.add(d.as_posix())

        _collect(party.name)
        return list(inc_dirs)

    def merged_lib_paths_for(self, party: ThirdParty, order: list[ThirdParty]) -> list[Path]:
        """收集组件的全部库搜索路径（自身 + 所有依赖组件）"""
        dirs: list[Path] = []
        seen: set[Path] = set()
        name_map = {p.name: p for p in order}
        visited: set[str] = set()

        def _collect(name: str) -> None:
            if name in visited:
                return
            visited.add(name)
            p = name_map.get(name)
            if p is None:
                return
            for dep in p.depends:
                _collect(dep)
            for d in p.lib_paths:
                if d not in seen:
                    seen.add(d)
                    dirs.append(d)

        _collect(party.name)
        return dirs

    def merged_libs_for(party: ThirdParty, order: list[ThirdParty]) -> list[str]:
        """收集组件的全部链接库名（自身 + 所有依赖组件）"""
        result: list[str] = []
        seen: set[str] = set()
        name_map = {p.name: p for p in order}
        visited: set[str] = set()

        def _collect(name: str) -> None:
            if name in visited:
                return
            visited.add(name)
            p = name_map.get(name)
            if p is None:
                return
            for dep in p.depends:
                _collect(dep)
            for lib in p.libs:
                if lib not in seen:
                    seen.add(lib)
                    result.append(lib)

        _collect(party.name)
        return result

    def print_compile_commands(self) -> None:
        print(" ")
        print(" === compile_commands: === ")
        for cmd in self._compile_commands:
            print(cmd)
        print(" =======================")

        # print(" =======================")
        # if self.target:
        #     print(self.get_target_commands())
        # print(" =======================")
        print(" ")

    def print_parties(self) -> None:
        print(" ")
        print("==== Partie  Dict: ====")
        for party in self.helper["PARTIES"]:
            print(f"[{party['name']}]")
            for _k, _v in party.items():
                print(f"\t{_k}: {_v}")
        print("=======================")
        print(" ")

    def resolve_order2(self) -> list[ThirdParty]:
        """
        拓扑排序：按依赖关系排序组件（被依赖的排前面）
        递归调用，直到所有组件都被访问过，
        有两个模块互相依赖，会出错
        """
        name_map: dict[str, ThirdParty] = dict(self.parties.items())
        visited: set[str] = set()
        self.order_parties: list[ThirdParty] = []

        # log.info(f"resolve_order name_map: {name_map}")

        def _dfs(name: str) -> None:
            # log.info(f"_dfs name: {name}")
            if name in visited:
                return
            visited.add(name)
            p = name_map.get(name)
            if p is None:
                return
            # log.info(f"p: {p.name} {p}")
            for dep in p.depends:
                _dfs(dep)
            # log.info(f"add: {p.name}  {p}")
            self.order_parties.append(p)

        for v in self.parties.values():
            # log.info(f"for party: {v.name}")
            _dfs(v.name)
        # log.info(f"order_parties: {self.order_parties}")
        return self.order_parties

    # def __target_commands_and_valid_parties(self):
    #     """
    #     target_commands_and_valid_parties
    #     """

    #     # self.commands_just_target = copy.deepcopy(self.__gen_targets())
    #     log.debug(f"static targets ====== {self.target_type}")

    #     # change depend parties to HEADER
    #     if self.target_type == "TARGETS":
    #         self.parties_valid = self.parties

    #     if self.target_type in ["STATIC", "SHARED"]:
    #         valid_names = list(self.parties_valid.keys())
    #         # log.debug(f"valid_names: {valid_names}")
    #         # log.debug(f"valid_names: {self.parties}")
    #         # log.debug(f"valid_names: {self.parties_valid}")
    #         # log.debug(f"valid_names: {type(self.parties_valid)}")

    #         for party in valid_names:
    #             party_deps = self.parties_valid[party].depends
    #             for deps in party_deps:
    #                 if deps not in self.parties_valid:
    #                     self.parties_valid.update({deps: self.parties[deps].clone()})
    #                     if deps not in valid_names:
    #                         self.parties_valid[deps].build_type = BuildType.HEADER.name
    #     log.debug(f"valid_names: {self.parties_valid}")
    #     for party in self.parties_valid.values():
    #         print(party.name, party.build_type)
    #         # print(party.build_type)
    #         # party.build_type = BuildType.HEADER.name

    #     pass
