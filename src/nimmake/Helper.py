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

import copy
import json
import os
import platform
import sys
from pathlib import Path
from typing import Any

# from .ThirdParties import BuildType, GenericParty, ThirdParty
from nimmake.Backends import BaseBackend, get_backend_cls
from nimmake.builders.base import Aliases, Commands, Phonies, Targets

# from .builders.command import Commands
# from .builders.phony import Aliases, Phonies
from nimmake.configs import (
    BARE_TARGET_OS_LST,
    TASK_GRPAPH_HEADER,
    TOML_PYMAKEX_CFG,
    BuildType,
)

# from .builder import Builder
from .flags import FlagsConfig
from .thirdParties import MyParties
from .utils import log


class Helper:
    """
    Helper class :
    double config,   self._env["CFG"] and  self._cfg. self._cfg easy to modify
    hlp = Helper()

    after cfg refresh , you adjust the flags. It is not easy to modify.

    hlp["CFG"] = FlagsConfig()
    hlp.from_cfg( )
    hlp.Prepend(CFLAGS=["-g"])
    hlp.Append(CFLAGS=["-g"])
    hlp.Update({"TOOLPATH": toolpath_armgcc, "TOOL": tool, "TOOL_PREFIX": prefix})
    """

    def __init__(self, register: bool = True, **kwargs):
        self._register = register
        self._cfg: FlagsConfig = FlagsConfig()
        self._backend: BaseBackend = None
        self._env: dict[str, Any] = {
            "CFG": {},  # config
            "CC": "gcc",
            "CXX": "g++",
            "LD": "ld",
            "AR": "ar",
            "AS": "as",
            "NM": "nm",
            "STRIP": "strip",
            "SIZE": "as",
            "OBJCOPY": "objcopy",
            "OBJDUMP": "objdump",
            # flags
            "CFLAGS": ["-Wall", "-g"],
            "CXXFLAGS": ["-Wall", "-g", "-std=c++17"],
            "ASFLAGS": [],
            "ARFLAGS": [],
            "LINKFLAGS": [],
            "INCPATH": [],  # header path -I
            "LIBPATH": [],  # lib path -L
            "LIBS": [],  # lib -lxxx
            "DEFINES": {},  # define -Dxxx=yyy
            # "MACROS": [],
            # TOOL TAGTER PLATFORM
            "TOOL": "gcc",
            "TOOL_PREFIX": "",
            "TOOL_WITH_PREFIX": "",
            "TOOLPATH": [],
            "TARGET_CPU": "",
            "TARGET_FPU": "",
            "TARGET_ABI": "",
            "TARGET_THUMB": "",
            "TARGET_ARCH": "",  # x86_64 arm64 arm
            "TARGET_VENDOR": "",  # NONE ELF LINUX  w64 ,vendor/system
            "TARGET_OS": "",  # os/eabi/runtime  mingw32 eabi
            # PLATFORM
            "PLATFORM_SYSTEM": platform.system(),  # linux win32 windows
            "PLATFORM_MACHINE": platform.machine(),  # x86_64
            "PLATFORM_ARCH": platform.architecture(),  # x86_64
            "PLATFORM_PROCESSOR": platform.processor(),  # x86_64
            # [[type，name，affialiate, tag]]
            # [ ["target", name, " "] , ["phony", name, " "], ["alias", name, " "] ]
            # [ ["target", "main", " "] , ["command", name, "main", "pre/post"] ]
            "TARGETS": [],
            "TARGET": [],
            "TARGET_NAME": "",
            "TARGET_SUFFIX": ".ELF",
            # Vendor and model
            "VENDOR": "",
            "MODEL": "",
            # Source files
            "SOURCES": [],
            # Header files
            "INCS": [],
            # third parties
            "PARTIES": {},
            # Objects
            "OBJ_EXT": ".o",
            "STATIC_LIB_EXT": ".a",
            "SHARED_LIB_EXT": ".so",
            # Action COMMAND
            "ACTIONS": [],
            "PRE_ACTIONS": [],
            "POST_ACTIONS": [],
            "COMMANDS": {},
            "PHONIES": {},
            "ALIASES": {},
            # BUILD OBJ DIR
            "BUILDDIR": "BUILD",
            "OBJDIR": "OBJ",
            "LIBDIR": "LIB",
            # install
            "INSTALLDIR": "install",
            "RELEASEDIR": "release",
            # mode  --nijia makefile
            "MODE": [],
            # verbose  dry-run silent
            "VERBOSE": False,
            "DRY_RUN": False,
            "SILENT": False,
        }
        self.Replace(**kwargs)

        self._cfg: FlagsConfig = FlagsConfig()

        # self.parties: dict[str, ThirdParty] = {}
        self.toolchain: BaseBackend | None = None
        self.srcs: list[str | Path] = []
        self.incs: list[str | Path] = []

        # TODO: 处理 TOOL 前缀 toolchain  backend
        # 加入自动检测工具链的功能
        # if not self._env["TOOL"]:
        #     self._env["TOOL"] = self._env["CC"]

        # if self._register:
        #     # print(f"register ................ {self._env}")
        #     atexit.register(self.__cache)

    def __getitem__(self, key: str) -> Any:
        return self._env[key]

    def get(self, key, default=None):
        """env.get(key, default)"""
        try:
            return self[key]
        except KeyError:
            return default

    def __setitem__(self, key: str, value: Any) -> None:
        self._env[key] = value

    def Set(self, key, value):
        self._dict[key] = value
        return self

    def __cache(self):
        print("==== Helper __cache ====")
        # print(f" sys.argv = {sys.argv}")

        params_raw = ""
        dct = {}
        try:
            idx = sys.argv.index("--pymake-args")
            params_raw = sys.argv[idx + 1]
        except (ValueError, IndexError):
            pass
        if params_raw:
            dct["PARAMS"] = json.loads(params_raw)
        print(f"====   {dct.get('PARAMS', {})}")

        # self._parse_party = ParseParties(self._env, silent=True, params=dct.get("PARAMS", {}))

        # self._parse_party = ParseParties(self._env, silent=True, params=dct["PARAMS"])
        # self._parse_party = ParseParties(self._env, silent=True)
        # print(self._env.get("ALIASES", {}), "--------")
        # dct = {"cache": True, "toolpath": self._env["TOOLPATH"]}
        # dct.update({"COMMANDS": self._env.get("COMMANDS", {})})
        # dct.update({"ALIASES": self._env.get("ALIASES", {})})
        # dct.update({"TARGETS": self._env.get("TARGETS", {})})
        # dct.update({"TARGET": self._parse_party.target})

        # os._exit(0)  # 快速退出

        # sys.stderr.write(json.dumps(dct))

        pass

    def Config(self, cfg: FlagsConfig | dict):
        if isinstance(cfg, FlagsConfig):
            self._env["CFG"] = cfg.to_dict()
            self._cfg = cfg
        elif isinstance(cfg, dict):
            self._cfg.from_dict(cfg)
            self._env["CFG"] = self._cfg.to_dict()
        else:
            self._env["CFG"] = {}
            self._cfg = FlagsConfig()
        return self

    def _default_target(self, **kwargs):
        """
        exchange build data to main process
        """
        # print(self.Dump(), file=sys.stderr)
        sys.stderr.write(self.Dump())
        # sys.stdout.write(self.Dump())
        # print(self.Dump(), file=sys.stderr)
        # return self._env

    def Dump(self) -> None:
        self._env["typ"] = "HELPER"
        self._env["name"] = "HELPER"
        return json.dumps(self._env)

    def Update(self, env: dict[str, Any]) -> None:
        self._env.update(**env)
        # print_debug("Update===", self._env)

    def Replace(self, **kwargs) -> None:  # noqa: ANN003
        for k, v in kwargs.items():
            self._env[k] = v

    def Append(self, **kwargs) -> None:
        for k, v in kwargs.items():
            if k not in self._env:
                if isinstance(v, dict):
                    self._env[k] = {}
                elif isinstance(v, list):
                    self._env[k] = []
                else:
                    self._env[k] = ""

            if isinstance(self._env[k], dict):
                if isinstance(v, dict):
                    self._env[k].update(v)
                else:
                    self._env[k] = v
            elif isinstance(self._env[k], list):
                if isinstance(v, list):
                    self._env[k].extend(v)
                else:
                    self._env[k].append(v)
            else:
                self._env[k] = f"{self._env[k]} {v}".strip()

    def Prepend(self, **kwargs) -> None:
        for k, v in kwargs.items():
            if k not in self._env:
                if isinstance(v, dict):
                    self._env[k] = {}
                elif isinstance(v, list):
                    self._env[k] = []
                else:
                    self._env[k] = ""

            if isinstance(self._env[k], dict):
                if isinstance(v, dict):
                    self._env[k].update(v)
                else:
                    self._env[k] = v
            elif isinstance(self._env[k], list):
                if isinstance(v, list):
                    self._env[k] = v + self._env[k]
                else:
                    self._env[k].insert(0, v)
            else:
                self._env[k] = f"{v} {self._env[k]}".strip()

    def MergeFlags(self, flags_dict: dict[str, Any]) -> None:
        self.Append(**flags_dict)

    def Clone(self, **kwargs) -> "Helper":
        new_env = Helper()
        new_env._env = copy.deepcopy(self._env)
        new_env.Replace(**kwargs)
        return new_env

    def output_flags(self) -> None:
        print()
        print("=" * 40)
        print(f"cflags: {self._backend._flags.cflags}")
        print(f"cxxflags: {self._backend._flags.cxxflags}")
        print(f"asflags: {self._backend._flags.asflags}")
        print(f"arflags: {self._backend._flags.arflags}")
        print(f"ldflags: {self._backend._flags.ldflags}")
        print(f"defines: {self._backend._flags.defines}")

        print(f"self._env['CFLAGS']: {self._env['CFLAGS']}")
        print(f"self._env['CXXFLAGS']: {self._env['CXXFLAGS']}")
        print(f"self._env['ASFLAGS']: {self._env['ASFLAGS']}")
        print(f"self._env['ARFLAGS']: {self._env['ARFLAGS']}")
        print(f"self._env['LINKFLAGS']: {self._env['LINKFLAGS']}")
        print(f"self._env['DEFINES']: {self._env['DEFINES']}")
        print("=" * 40)

    def import_from_backend(self) -> None:
        self._env["CFLAGS"] = self._backend._flags.cflags
        self._env["CXXFLAGS"] = self._backend._flags.cxxflags
        self._env["ASFLAGS"] = self._backend._flags.asflags
        self._env["ARFLAGS"] = self._backend._flags.arflags
        self._env["LINKFLAGS"] = self._backend._flags.ldflags
        self._env["DEFINES"] = self._backend._flags.defines

    def Dictionary(self) -> dict[str, Any]:
        return copy.deepcopy(self._env)

    def DAG(self) -> dict[str, Any]:
        cmd_dct = {"name": "DAG"}
        cmd_dct.update({"typ": "COMMANDS"})
        sys.stdout.write(f"{TASK_GRPAPH_HEADER}{json.dumps(cmd_dct)}\n")
        sys.stdout.flush()
        # print(f"{TASK_GRPAPH_HEADER}{json.dumps(cmd_dct)}")
        # return copy.deepcopy(self._env)

    @property
    def Flags(self) -> str:
        info = "\n"
        info += "=" * 40 + "\n"
        info += f"CFLAGS: {self._env['CFLAGS']}\n"
        info += f"CXXFLAGS: {self._env['CXXFLAGS']}\n"
        info += f"ASFLAGS: {self._env['ASFLAGS']}\n"
        info += f"ARFLAGS: {self._env['ARFLAGS']}\n"
        info += f"LINKFLAGS: {self._env['LINKFLAGS']}\n"
        info += f"DEFINES: {self._env['DEFINES']}\n"
        info += "=" * 40 + "\n"
        info += "\n"
        return info

    @property
    def Toolchain(self) -> str:
        info = "\n"
        info += "=" * 40 + "\n"
        info += f"CC: {self._env['CC']}\n"
        info += f"CXX: {self._env['CXX']}\n"
        info += f"AS: {self._env['AS']}\n"
        info += f"AR: {self._env['AR']}\n"
        info += f"LINK: {self._env['LD']}\n"
        info += f"Size: {self._env['SIZE']}\n"
        info += "=" * 40 + "\n"
        info += "\n"
        return info

    def _flatten_env(self) -> dict[str, str]:
        flat = {}
        for k, v in self._env.items():
            if isinstance(v, list):
                flat[k] = " ".join(v)
            else:
                flat[k] = str(v)
        return flat

    def Parties(
        self,
        name: str,
        root: str | Path,
        third_party: str = "GENERIC",
        build_type: BuildType = BuildType.OBJECT.name,
        source_exts: list[str] = None,
        header_exts: list[str] = None,
        recursive: bool = True,
        depends: list[str] = None,
        exclude_dirs: list[str] = None,
        exclude_prefixes: list[str] = None,
        exclude_suffixes: list[str] = None,
        # macros: dict[str, str] = None,
        # global_macros: dict[str, str] = None,
        include_macros: dict[str, str] = None,
        defines: dict[str, str] = None,
        relative: bool = True,
        params: dict[str, str] = None,
    ) -> None:
        # log.info(f"Parties: {name}, {root}, {third_party}, {build_type}, {source_exts}, {header_exts}, {recursive}, {depends}, {exclude_dirs}, {exclude_prefixes}, {exclude_suffixes}, {defines}, {relative}, {params}")
        party = MyParties(
            name=name.upper(),
            root=root,
            third_party=third_party,
            build_type=build_type,
            source_exts=source_exts,
            header_exts=header_exts,
            recursive=recursive,
            depends=depends,
            exclude_dirs=exclude_dirs,
            exclude_prefixes=exclude_prefixes,
            exclude_suffixes=exclude_suffixes,
            include_macros=include_macros,
            defines=defines,
            relative=relative,
            params=params,
        )
        # cmd_dct = party.Dictionary()
        # cmd_dct.update({"typ": "PARTIES"})
        dump_party = party.Dump()
        cmd_str = TASK_GRPAPH_HEADER + dump_party + "\n"
        sys.stdout.write(cmd_str)
        sys.stdout.flush()
        return party

        # if party.name.upper() in self._env["PARTIES"]:
        #     log.error(f"Party {party.name.upper()} already exists")
        # self._env["PARTIES"].update({party.name.upper(): party.handler})
        # return party.handler  # return party handler,had dependon method
        pass

    def Refresh(self) -> None:
        """
        from self._cfg to self._env["CFG"]
        get combined flags from toolchain and parties.
        such as CFLAGS, CXXFLAGS, ASFLAGS, ARFLAGS, LINKFLAGS, DEFINES
        """
        # get BACKEND cls
        # log.error(f"self._env['DEFINES']: {self._env['DEFINES']}")
        backend_cls = get_backend_cls(self._env["TOOL"], self._env["TOOL_PREFIX"])
        if not backend_cls:
            log.error(f"backend cls not found: {self._env['TOOL']} {self._env['TOOL_PREFIX']}")
            return

        # create backend
        # log.debug(f"toolchain : {self._env['TOOL']} {self._env['TOOL_PREFIX']}")
        # log.info(f"backend_cls : {backend_cls}")
        self._backend = backend_cls(toolpath=self._env.get("TOOLPATH", None))
        if self._env["TOOL"] == "clang" and self._env["TOOL_PREFIX"].lower() in [
            "arm",
            "llvm",
        ]:
            tool = f"{self._env['TOOL']}"
        else:
            tool = f"{self._env['TOOL_PREFIX']}{self._env['TOOL']}"

        if not self._backend.is_tool_exsited(tool):
            log.error(f"toolchain not found: {tool}")
            return
        log.output(f"Toolchain : [{tool}] is detected.")

        self.__set_toolchain()
        # self.__set_triple()
        # self.__suffix()

        if self._env["TARGET_OS"].lower() in BARE_TARGET_OS_LST and not self._env["CFG"]["cpu"]:
            log.error("MCU bare system, NO CPU INFO")
            return

        log.debug(
            f"_cfg: {self._backend.cpu} {self._backend.arch} -{self._backend.fpu} {self._backend.abi}"
        )
        self._backend.set("cpu", self._env["CFG"].get("cpu", ""))
        self._backend.set("arch", self._env["CFG"].get("arch", ""))
        self._backend.set("fpu", self._env["CFG"].get("fpu", ""))
        self._backend.set("abi", self._env["CFG"].get("abi", ""))

        # log.error(f"_cfg: {self._env['CFG']} ")

        # get flags
        # self.__collect()
        self._backend.collect(**self._env["CFG"])

        self.import_from_backend()
        # log.error(f"_cfg: {self._backend}")
        self.__set_triple()
        self.__suffix()

        dump_ = self.Dump()
        dump_helper_str = TASK_GRPAPH_HEADER + dump_ + "\n"
        sys.stdout.write(dump_helper_str)
        sys.stdout.flush()

        # self.output_flags()
        # fill CFLAGS, CXXFLAGS, ASFLAGS, ARFLAGS, LINKFLAGS, DEFINES
        pass

    def TOML(self) -> None:
        import tomllib

        toml_pymake_pth = Path(TOML_PYMAKEX_CFG)
        if not toml_pymake_pth.exists():
            log.warn(f"toml file not found: {TOML_PYMAKEX_CFG}")
            exit(1)

        try:
            with open(TOML_PYMAKEX_CFG, "rb") as f:
                data = tomllib.load(f)
        except FileNotFoundError:
            log.warn(f"toml file not found: {TOML_PYMAKEX_CFG}")
            return

        if data:
            self._env["CFG"].update(**data)
        pass

    def Program(self, target: str = None, sources: list[str | Path] = None) -> None:
        if not target:
            log.error("target is None")
            return
        tgt_ = Targets(target, sources=sources)
        dump_tgt = tgt_.Dump()
        tgt_str = TASK_GRPAPH_HEADER + dump_tgt + "\n"
        sys.stdout.write(tgt_str)
        sys.stdout.flush()
        return tgt_
        # if "_DEFAULT" not in self._env["PARTIES"]:
        #     default = self.Parties(
        #         "_DEFAULT", root=Path("."), third_party="_DEFAULT", recursive=False
        #     )
        # else:
        #     log.error(f"target have exsited")
        #     default = self._env["PARTIES"]["_DEFAULT"]
        # target_suf = f"{target}"
        # if target in self._env["TARGETS"]:
        #     log.error(f"target {target} already exists")
        #     return
        # self._env["TARGETS"].append([target, "target"])  # 目标类型 target
        # if sources:
        #     self.AddSrcs(target=None, sources=sources)
        # return target

        pass

    def Library_STATIC(self, lib_name: str, sources: list[str | Path] = None) -> None:
        if not lib_name:
            log.error("static lib is None")
            return
        print(f"***** * target: {lib_name}")
        tgt_ = Targets(lib_name, sources=sources, typ="STATIC")
        dump_tgt = tgt_.Dump()
        tgt_str = TASK_GRPAPH_HEADER + dump_tgt + "\n"
        sys.stdout.write(tgt_str)
        sys.stdout.flush()
        return tgt_

        # target_suf = f"{target}"
        if lib_name in self._env["TARGETS"]:
            log.error(f"lib {lib_name} already exists")
            return
        self._env["TARGETS"].append([lib_name, "static", " "])  # 目标类型 target
        # log.warn(f"target {self._env['TARGETS']}  ")
        return lib_name

    def Library_SHARED(self, lib_name: str, sources: list[str | Path] = None) -> None:
        if not lib_name:
            log.error("shared lib is None")
            return
        tgt_ = Targets(lib_name, sources=sources, typ="SHARED")
        dump_tgt = tgt_.Dump()
        tgt_str = TASK_GRPAPH_HEADER + dump_tgt + "\n"
        sys.stdout.write(tgt_str)
        sys.stdout.flush()
        return tgt_

        # # target_suf = f"{target}"
        # if lib_name in self._env["TARGETS"]:
        #     log.error(f"lib {lib_name} already exists")
        #     return
        # self._env["TARGETS"].append([lib_name, "shared", " "])  # 目标类型 target
        # # log.warn(f"target {self._env['TARGETS']}  ")
        # return lib_name

    # ---------------- 构建器：预先拼接完整命令列表传入 BuildTarget ----------------

    def Action(self, action: list[str], action_type: str = "") -> None:
        if not action:
            return
        self._env["ACTIONS"].append([action_type, action])
        # self.builder.add_pre_action(action)
        pass

    def Command(self, name: str, cmd: str | list[str], cmd_type: str = "") -> None:
        if not cmd:
            return
        cmd_ = Commands(name, cmd)
        dump_cmd = cmd_.Dump()
        cmd_str = TASK_GRPAPH_HEADER + dump_cmd + "\n"
        sys.stdout.write(cmd_str)
        sys.stdout.flush()
        return cmd_
        # cmd_lst = []
        # if isinstance(cmd, str):
        #     cmd_lst = [cmd]
        # elif isinstance(cmd, list):
        #     cmd_lst = cmd
        # else:
        #     log.error(f"Command {name} {cmd} is not a string or list")
        #     return
        # self._env["COMMANDS"].update({name: cmd_lst})
        # return name
        pass

    def Phony(self, name: str, phony: str | list[str]) -> None:
        if not phony:
            return
        phony_obj = Phonies(name, phony)
        dump_ = phony_obj.Dump()
        dump_str = TASK_GRPAPH_HEADER + dump_ + "\n"
        sys.stdout.write(dump_str)
        sys.stdout.flush()
        return phony_obj

    def Alias(self, name: str, alias: str | list[str]) -> None:
        """multiple target"""
        if not alias:
            return
        alias_ = Aliases(name, alias)
        dump_ = alias_.Dump()
        dump_str = TASK_GRPAPH_HEADER + dump_ + "\n"
        sys.stdout.write(dump_str)
        sys.stdout.flush()
        return alias_

    def DefaultTarget(self, name: str | Targets = None) -> None:
        if not name:
            return
        if isinstance(name, Targets):
            name = name.name
        dct = {
            "name": name,
            "typ": "DEFAULTTARGET",
        }
        dump_ = json.dumps(dct)
        dump_str = TASK_GRPAPH_HEADER + dump_ + "\n"
        sys.stdout.write(dump_str)
        sys.stdout.flush()
        self._env["TARGET"] = name
        # return name

        # tgt_lst = [tgt[0] for tgt in self._env["TARGETS"]]
        # if name not in tgt_lst:
        #     log.error(f"Default target {name} not exists")
        #     return
        # self._env["TARGET"] = name

    def Clean(self) -> None:
        for tgt in self.targets:
            if os.path.exists(tgt.name):
                os.remove(tgt.name)
                print(f"清理 {tgt.name}")
        print("清理完成")

    def AddSrcs(self, target: str, sources: str | Path | list[str | Path]) -> None:
        """
        donot need parameter target,   to default target
        """
        if "_DEFAULT" not in self._env["PARTIES"]:
            default = self.Parties("_DEFAULT", root=Path("."), third_party="_DEFAULT")
        else:
            default = self._env["PARTIES"]["_DEFAULT"]
        srcs = []
        if isinstance(sources, str):
            srcs.append(Path(sources))
        elif isinstance(sources, Path):
            srcs.append(sources)
        elif isinstance(sources, list):
            for src_ in sources:
                if isinstance(src_, str):
                    srcs.append(Path(src_))
                elif isinstance(src_, Path):
                    srcs.append(src_)
        for src in srcs:
            if src.is_file() and src not in self._env["SOURCES"]:
                self._env["SOURCES"].append(src)

        # self.builder.add_pre_action(action)
        return default
        pass

    # def AddSrcs2(self, sources: str | Path | list[str | Path], target: str = None) -> None:
    #     """
    #     donot need parameter target,   to default target
    #     """
    #     if "_DEFAULT" not in self._env["PARTIES"]:
    #         default = self.Parties("_DEFAULT", root=Path("."), third_party="_DEFAULT")
    #     else:
    #         default = self._env["PARTIES"]["_DEFAULT"]
    #     srcs = []
    #     if isinstance(sources, str):
    #         srcs.append(Path(sources))
    #     elif isinstance(sources, Path):
    #         srcs.append(sources)
    #     elif isinstance(sources, list):
    #         for src_ in sources:
    #             if isinstance(src_, str):
    #                 srcs.append(Path(src_))
    #             elif isinstance(src_, Path):
    #                 srcs.append(src_)
    #     for src in srcs:
    #         if src.is_file() and src not in self._env["SOURCES"]:
    #             self._env["SOURCES"].append(src)

    #     # self.builder.add_pre_action(action)
    #     return default
    #     pass

    def AddIncs(self, target: str, incs: str | Path | list[str | Path]) -> None:
        incs = []
        if isinstance(incs, str):
            incs.append(Path(incs))
        elif isinstance(incs, Path):
            incs.append(incs)
        elif isinstance(incs, list):
            for inc_ in incs:
                if isinstance(inc_, str):
                    incs.append(Path(inc_))
                elif isinstance(inc_, Path):
                    incs.append(inc_)
        for inc in incs:
            if inc.is_dir() and inc not in self._env["INCLUDES"]:
                self._env["INCS"].append(inc)

    # def AddIncs2(self, incs: str | Path | list[str | Path]) -> None:
    #     incs = []
    #     if isinstance(incs, str):
    #         incs.append(Path(incs))
    #     elif isinstance(incs, Path):
    #         incs.append(incs)
    #     elif isinstance(incs, list):
    #         for inc_ in incs:
    #             if isinstance(inc_, str):
    #                 incs.append(Path(inc_))
    #             elif isinstance(inc_, Path):
    #                 incs.append(inc_)
    #     for inc in incs:
    #         if inc.is_dir() and inc not in self._env["INCLUDES"]:
    #             self._env["INCS"].append(inc)

    # def AddPreAction(self, action: str) -> None:
    #     # self.builder.add_pre_action(action)
    #     pass

    # def AddPostAction(self, action: str) -> None:
    #     # self.builder.add_post_action(action)
    #     pass

    def __get_triple_cmd(self) -> Any:
        if "gcc" in self._env["CC"]:
            return [self._env["CC"], "-dumpmachine"]
        elif "clang" in self._env["CC"]:
            return [self._env["CC"], "--print-target-triple"]
        else:
            return []
        pass

    def __set_toolchain(self) -> Any:
        toolchain = {}
        # log.error(f"__set_toolchain ")
        toolchain = self._backend._tool(self._env["TOOL"], self._env["TOOL_PREFIX"])
        # toolchain = _tool_clang(self._env["TOOL"], self._env["TOOL_PREFIX"])
        # log.debug(f"__set_toolchain = {toolchain} ")
        for k, v in toolchain.items():
            self._env[k.upper()] = v
            pass
        # log.debug(f"__set_toolchain = {self._env['CC']} {self._env['CXX']}  ")
        # log.error(f"toolchain {toolchain} {self._env['TOOL_PREFIX']} {self._env['CC']}")
        pass

    def __set_triple(self) -> Any:
        triple_cmd_lst = self.__get_triple_cmd()
        if triple_cmd_lst:
            triple = self._backend.get_triple(triple_cmd_lst)
            if triple:
                lst = triple.split("-")
                if len(lst) >= 3:  # 标准格式: arch-vendor-os
                    self._env["TARGET_ARCH"] = lst[0]
                    self._env["TARGET_VENDOR"] = lst[1]
                    self._env["TARGET_OS"] = lst[2]
                elif len(lst) == 2:  # 简化格式: arch-os
                    self._env["TARGET_ARCH"] = lst[0]
                    self._env["TARGET_VENDOR"] = "unknown"
                    self._env["TARGET_OS"] = lst[1]
                else:  # 异常情况: 只有arch或空
                    self._env["TARGET_ARCH"] = lst[0] if len(lst) >= 1 else "unknown"
                    self._env["TARGET_VENDOR"] = "unknown"
                    self._env["TARGET_OS"] = "unknown"
        # log.error(
        #     f"__set_triple = {self._env['TARGET_ARCH']} {self._env['TARGET_VENDOR']} {self._env['TARGET_OS']}"
        # )

    def set_cfg(self, key: str, value: str) -> Any:
        self._env["CFG"][key] = value
        self._cfg.set(key, value)

    def __suffix(self) -> Any:
        """
        target suffix
        msvc :动态链 两个文件 .dll .lib
        mingw -win : 两个文件 .dll .a or .dll.a
        linux, shared , 可以传版本号 SONAME 软链接,也可以不传版本号,默认版本号
        -Wl,-soname,libcalc.so.1
        """
        # target_suf, obj_ext, lib_ext, dylib_ext = get_suffix(
        #     self._env["CC"].lower(),
        #     self._env["TARGET_OS"].lower(),
        #     self._env["CFLAGS"],
        # )
        # self.__set_extensions(target_suf, obj_ext, lib_ext, dylib_ext)
        # log.debug(f"__suffix = {target_suf}, {obj_ext}, {lib_ext}, {dylib_ext}")
        # self.__set_extensions(aa[0], aa[1], aa[2], aa[3])
        # log.debug(
        #     f"self._env['CFLAGS'], self._env['CC'] = {self._env['CFLAGS']} {self._env['CC']}"
        # )
        # return

        # log.debug(f"Platfrom = {platform.system()}  {platform.machine()}")
        if self._env["TOOL"].lower() == "armclang":
            self.__set_extensions(".axf", ".o", ".a", ".a")
            return
        if self.is_toolchain_msvc:
            self.__set_extensions(".exe", ".obj", ".lib", ".lib")
            return

        # gcc
        if self.is_toolchain_gcc:
            if self.is_target_OS_bare:
                self.__set_extensions(".elf", ".o", ".a", ".a")
            if self.is_target_OS_windows:
                self.__set_extensions(".exe", ".o", ".a", ".dll")
            if self.is_target_OS_linux:
                self.__set_extensions("", ".o", ".a", ".so")
            if self.is_target_OS_mac:
                self.__set_extensions(".app", ".o", ".a", ".dylib")
            return

        # clang
        if self.is_toolchain_clang:
            cflags = self._env["CFLAGS"]
            _target = ""
            plat = ""
            for flag in cflags:
                if flag.startswith("--target"):
                    _target = flag.split("=")[1]
                    break
            # log.error(f"__suffix = {_target}  {self._env['CFLAGS']}")
            if not _target:
                plat = self._env["PLATFORM_SYSTEM"]
            else:
                _target_triple = _target.split("-")
                if len(_target_triple) >= 3:
                    plat = _target_triple[-2]
                else:
                    plat = self._env["PLATFORM_SYSTEM"]

            if plat.lower() in ["windows"]:
                self.__set_extensions(".exe", ".o", ".a", ".dll.a")
            elif plat.lower() in ["linux"]:
                self.__set_extensions("", ".o", ".a", ".so")
            elif plat.lower() in ["apple", "darwin"]:
                self.__set_extensions(".app", ".o", ".a", ".dylib")
            else:
                self.__set_extensions(".elf", ".o", ".a", ".a")
        return
        # return
        # log.error(f"__suffix = {self._env['TARGET_OS']} suff={self._env['TARGET_SUFFIX']}")

    # def __suffix_0(self) -> Any:
    #     """
    #     target suffix
    #     msvc :动态链 两个文件 .dll .lib
    #     mingw -win : 两个文件 .dll .a or .dll.a
    #     linux, shared , 可以传版本号 SONAME 软链接,也可以不传版本号,默认版本号
    #     -Wl,-soname,libcalc.so.1
    #     """
    #     if self._env["TOOL"].lower() == "armclang":
    #         self.__set_extensions(".axf", ".o", ".a", ".a")
    #         return
    #     if self.is_target_OS_bare:
    #         self.__set_extensions(".elf", ".o", ".a", ".a")
    #         return
    #     if self.is_target_OS_windows and self.is_toolchain_msvc:
    #         self.__set_extensions(".exe", ".obj", ".lib", ".lib")
    #         # return
    #     if self.is_target_OS_windows and self.is_toolchain_gcc:
    #         self.__set_extensions(".exe", ".o", ".a", ".dll")
    #     # if self.is_target_OS_windows and self.is_toolchain_clang:
    #     #     self.__set_extensions(".exe", ".o", ".a", ".dll.a")

    #     if self.is_target_OS_linux and not self._env["TOOL_PREFIX"]:
    #         self.__set_extensions("", ".o", ".a", ".so")
    #         # return

    def __set_extensions(
        self, target_suf: str, obj_ext: str, static_lib_ext: str, shared_lib_ext: str
    ) -> bool:
        self._env["TARGET_SUFFIX"] = target_suf
        self._env["OBJ_EXT"] = obj_ext
        self._env["STATIC_LIB_EXT"] = static_lib_ext
        self._env["SHARED_LIB_EXT"] = shared_lib_ext

    @property
    def is_target_OS_bare(self) -> bool:
        return self._env["TARGET_OS"].lower() in BARE_TARGET_OS_LST

    @property
    def is_target_OS_windows(self) -> bool:
        return self._env["TARGET_OS"].lower() in ["windows"]

    @property
    def is_target_OS_linux(self) -> bool:
        return self._env["TARGET_OS"].lower() in ["linux"]

    @property
    def is_target_OS_mac(self) -> bool:
        return self._env["TARGET_OS"].lower() in ["apple", "darwin"]

    @property
    def is_toolchain_msvc(self) -> bool:
        return self._env["TOOL"].lower() == "msvc"

    @property
    def is_toolchain_armclang(self) -> bool:
        return self._env["TOOL"].lower() == "armclang"

    @property
    def is_toolchain_clang(self) -> bool:
        return "gcc" == self._env["TOOL"].lower() or "clang" == self._env["TOOL"].lower()

    @property
    def is_toolchain_gcc(self) -> bool:
        return "gcc" == self._env["TOOL"].lower()

    def target_out(self, name: str = "") -> str:
        if not name:
            name = self._env["TARGET"]
        return f"{self._env['BUILDDIR']}/{name}{self._env['TARGET_SUFFIX']}"

    def hex_out(self, name: str = "") -> str:
        if not name:
            name = self._env["TARGET"]
        return f"{self._env['BUILDDIR']}/{name}.hex"

    def bin_out(self, name: str = "") -> str:
        if not name:
            name = self._env["TARGET"]
        return f"{self._env['BUILDDIR']}/{name}.bin"

    def hex_cmd(self, name: str = "") -> str:
        cmd = f"{self._env['OBJCOPY']} -O ihex {self.target_out(name)} {self.hex_out(name)}"
        if "armclang" in self._env["TOOL"].lower():
            cmd = f"fromelf --i32 --output= {self.bin_out(name)} {self.target_out(name)}"
        return cmd

    def bin_cmd(self, name: str = "") -> str:
        cmd = f"{self._env['OBJCOPY']} -O binary {self.target_out(name)} {self.bin_out(name)}"
        if "armclang" in self._env["TOOL"].lower():
            cmd = f"fromelf --bin --output= {self.bin_out(name)} {self.target_out(name)}"
        return cmd

    def open_cmd(self, link: str, target_cpu: str, addr: int = 0x08000000) -> str:
        cmd = 'openocd -f {link} -c "program {self.bin_out(name)} verify exit'
        cmd = "openocd -f interface/$$interface$$ -f target/$$TARGETCPU$$.cfg "
        cmd += "-c init -c reset -c halt -c "
        cmd += f'"program {self.bin_out()} exit {addr:#08x}" '
        cmd += "-c reset -c shutdown"
        link_ = link
        if link.upper() == "DAPLINK":
            link_ = "cmsis-dap.cfg"
        elif link.upper() == "STLINK":
            link_ = "stlink.cfg"
        target_cpu_ = target_cpu
        cmd = cmd.replace("$$TARGETCPU$$", target_cpu_)
        cmd = cmd.replace("$$interface$$", link_)
        return cmd

    # def __suffix2(self) -> Any:
    #     """
    #     target suffix
    #     """
    #     if self._env["TARGET_OS"].lower() in BARE_TARGET_OS_LST:
    #         self._env["CFG"]["TARGET_SUFFIX"] = ".elf"
    #         self._env["CFG"]["OBJ_EXT"] = ".o"
    #         self._env["CFG"]["STATIC_LIB_EXT"] = ".a"
    #         self._env["CFG"]["SHARED_LIB_EXT"] = ".a"
    #         return
    #     if self._env["TARGET_OS"].lower() in ["windows"]:
    #         self._env["CFG"]["TARGET_SUFFIX"] = ".exe"
    #         self._env["CFG"]["OBJ_EXT"] = ".obj"
    #         self._env["CFG"]["STATIC_LIB_EXT"] = ".lib"
    #         self._env["CFG"]["SHARED_LIB_EXT"] = ".dll"
    #         return
    #     if self._env["TARGET_OS"].lower() in ["linux"]:
    #         self._env["CFG"]["TARGET_SUFFIX"] = ".exe"
    #         self._env["CFG"]["OBJ_EXT"] = ".o"
    #         self._env["CFG"]["STATIC_LIB_EXT"] = ".a"
    #         self._env["CFG"]["SHARED_LIB_EXT"] = ".so"
    #         return


# ===================== 使用示例 =====================
if __name__ == "__main__":
    # helper_1()
    # helper_flags_config()
    pass
