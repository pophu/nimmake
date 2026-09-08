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

"""Parse Parties"""

import shutil
from pathlib import Path

from nimmake.builders.base import Targets
from nimmake.builders.builder import MyBuilder
from nimmake.builders.buildTarget import BuildTargetCommands
from nimmake.builders.compiledb import Compiledb
from nimmake.builders.ninja import Ninja
from nimmake.builders.Tracker import Tracker
from nimmake.configs import CACHE_FILENAME, TOML_PYMAKEX
from nimmake.executor import CmdExecutorCli
from nimmake.thirdParties import GenericParty
from nimmake.thirdParties.MyParties import PARTIES_DCT
from nimmake.utils import LogLevel, log


class ParseParties:
    def __init__(
        self,
        # helper: dict[str, Any] = None,
        graph_header: dict = None,
        params: dict = None,
    ):
        # self.helper = helper
        self.graph_header = graph_header.copy()
        self.params = params.copy()
        self.helper = self.graph_header.get("HELPER", {})
        self.helper = self.helper.get("HELPER", {}).copy()  # self.graph_header["HELPER"]["HELPER"]
        self.parties = self.graph_header.get("PARTIES", {})
        self.commands = self.graph_header.get("COMMANDS", {})
        self.aliases = self.graph_header.get("ALIASES", {})
        self.phonies = self.graph_header.get("PHONIES", {})
        self.depends = self.graph_header.get("DEPENDS", {})
        self.targets = self.graph_header.get("TARGETS", {})
        self.default_target = self.graph_header.get("DEFAULTTARGET", {})
        self.parties_parsed = {}

        # log.warn(f"self.logger: {params}  {self.params}")
        # log.warn(f"self.logger:   {list(self.graph_header.keys())}")
        # log.warn(f"HELPER:   {self.graph_header.get('HELPER', {})}")

        #########  TARGET #########

        self.target: Targets = None
        self.target_type = "target"  # target lib
        self.target_out = ""  # target lib
        self.target_commands_generated = False  # target cmd has generated
        self.target_generated = False
        self.positional_cmdline_tasks = []
        self.mixed_commands = []  # include target and commands

        self.mode = self.params.get("mode", "build")

        # self.print_info()
        ## TRACKER EXECUTOR  ###
        self.tracker: Tracker = None
        self._executor = CmdExecutorCli()
        if self.helper.get("TOOLPATH", ""):
            self._executor.add_path(self.helper["TOOLPATH"], prepend=True)

        self.__params()
        # self.__alias()
        self.__phony()
        self.__clean()
        self.__get_mixed_commands_target()
        self.__get_target()
        self.__parse_parties()

        if not self.mixed_commands:
            log.info("No commands, No Target")

        self.mb = MyBuilder(
            max_workers=self.jobs,
            verbose=self.verbose,
            silent=self.silent,
            dry_run=self.dry_run,
        )
        self.pre_commands = []
        self.post_commands = []
        self.target_commands = {}  # commands from target
        # self.builder = BuilderCli(None, executor=self._executor)
        log.debug(f" mixed_commands: {self.mixed_commands},TARGET TYPE: {self.target_type}")
        # log.error(self.post_commands)

        self.__parse_mode()
        self.__mode()

    def print_info(self):
        log.debug(f"self.helper: {self.helper['TOOLPATH']}")
        log.debug(f"self.parties: {self.parties}")
        # log.debug(f"self.commands: {self.commands}")
        # log.debug(f"self.aliases: {self.aliases}")
        # log.debug(f"self.phonies: {self.phonies}")
        # log.debug(f"self.depends: {self.depends}")
        # log.debug(f"self.targets: {self.targets}")

    def idle(self):
        pass

    def __params(self):
        self.verbose = self.params.get("verbose", False)
        self.silent = self.params.get("silent", False)
        self.dry_run = self.params.get("dry_run", False)
        self.logger = self.params.get("logger", 0)
        self.clean = self.params.get("clean", False)
        self.mode = self.params.get("mode", "build")
        self.jobs = self.params.get("jobs", 1)
        self.toml = self.params.get("toml", None)
        self.party = self.params.get("party", None)
        self.cache = self.params.get("cache", False)
        # self.buildcache = self.params.get("buildcache", False)
        self.compiledb = self.params.get("compiledb", False)
        self.ninja = self.params.get("ninja", False)

        log.warn(
            f"self.logger: {self.logger},verbose: {self.verbose}, silent: {self.silent}, dry_run: {self.dry_run}"
        )
        if self.logger == 0:
            log.set_level(LogLevel.WARN.name)
        elif self.logger == 1:
            log.set_level(LogLevel.INFO.name)
        elif self.logger == 2:
            log.set_level(LogLevel.DEBUG.name)
        else:
            log.set_level(LogLevel.WARN.name)

    def __alias(self):
        self.positional = self.params.get("positional", [])
        self.lib_target = self.params.get("lib", [])
        self.positional_cmdline = ""
        log.info(f"self.positional: {self.positional}")
        if self.positional:
            self.positional_cmdline = self.positional[0]
        if self.__check_alias():
            self.target = ""

    def __check_alias(self) -> None:
        # no alias
        # log.debug(f"alias_task: {self.positional_cmdline_tasks}")
        if not self.positional_cmdline:
            return False

        aliases_ = self.aliases.get(self.positional_cmdline, {})

        #  alias not in self.helper["ALIASES"]
        if not aliases_ or not aliases_.get("aliases", []):
            log.warn(f"alias_task: [{self.positional_cmdline}] not in ALIASES")
            return False

        # parse alias task
        alias_task = aliases_.get("aliases", [])
        if isinstance(alias_task, str):  # alias compatible str list
            alias_task = [alias_task]
        for task in alias_task:
            if task in self.targets:
                self.positional_cmdline_tasks.append(task)
            if task in self.commands:
                self.positional_cmdline_tasks.append(task)
            if task in self.phonies:
                self.positional_cmdline_tasks.append(task)
        log.debug(f"alias_task: {self.positional_cmdline_tasks}")
        return True

    def __phony(self):
        self.positional = self.params.get("positional", [])
        self.lib_target = self.params.get("lib", [])
        self.positional_cmdline = ""
        # log.info(f"self.positional: {self.positional}")
        if self.positional:
            self.positional_cmdline = self.positional[0]
        if self.__check_phony():
            self.target = ""

    def __check_phony(self) -> None:
        # no alias
        # log.debug(f"alias_task: {self.positional_cmdline_tasks}")
        if not self.positional_cmdline:
            return False

        phonies_ = self.phonies.get(self.positional_cmdline, {})

        #  alias not in self.helper["ALIASES"]
        if not phonies_ or not phonies_.get("phonies", []):
            log.warn(f"phony_task: [{self.positional_cmdline}] not in PHONIES")
            return False
        # log.debug(f"phony_task: 2  {self.targets} {self.commands}")

        # parse phony task
        phony_task = phonies_.get("phonies", [])
        if isinstance(phony_task, str):  # phony_task compatible str list
            phony_task = [phony_task]
        for task in phony_task:
            if task in self.targets:
                self.positional_cmdline_tasks.append(task)
            if task in self.commands:
                self.positional_cmdline_tasks.append(task)
            if task in self.phonies:
                self.positional_cmdline_tasks.append(task)
        log.debug(f"phony_task: {self.positional_cmdline_tasks}")
        return True

    def __get_mixed_commands_target(self):
        """
        get mixed commands from alias_cmdline_tasks
        target+commands(list)
        target :str
        commands :list
        """
        log.debug(f"__get_mixed_commands_target: {self.positional_cmdline_tasks}")
        if self.positional_cmdline_tasks:
            for task in self.positional_cmdline_tasks:
                if task in self.targets:
                    self.mixed_commands.append(task)
                    continue
                if task in self.commands:
                    self.mixed_commands.append(self.commands[task]["commands"])
                    continue
        else:
            # log.debug(f" no alias, target: {self.default_target}")
            if self.default_target:
                default_tgt = list(self.default_target.keys())[0]
                # if len(self.mixed_commands) == 0:
                self.mixed_commands.append(default_tgt)
            pass

    def __get_target(self):
        """
        # cannot exsit multiple target , especially target + multi lib ?
        # if not , cannot judge which srcs should be compiled
        """
        targets_ = [tgt for tgt in self.mixed_commands if isinstance(tgt, str)]
        if len(targets_) > 1:
            log.error(f"Exist multiple target. {targets_}")
            self.target_type = ""
            self.target = ""
            return

        if len(targets_) == 0:
            self.target_type = ""
            self.target = ""
            return

        for tgt in self.mixed_commands:
            # log.info(f"tgt: {tgt}   {self.targets}, DEFAULT: {self.default_target}")
            if tgt in self.targets:
                self.target_type = self.targets[tgt]["typ"]
                self.target = Targets(**self.targets[tgt])
                # log.warn(f"helper: {list(self.helper.keys())}")
                t_out = (
                    Path(self.helper["BUILDDIR"])
                    / f"{self.target.name}{self.helper['TARGET_SUFFIX']}"
                )
                self.target_out = t_out.as_posix()
                break
        if self.target_type in ["STATIC", "SHARED"]:
            if self.target.name.upper() in self.parties:
                log.info(f"static party exsited {self.target.name.upper()}")
            else:
                log.error(f"static party not exsited {self.target.name.upper()}")
                log.error(f"parties ：{self.parties.keys()}")
                exit(1)

    # def __get_target_type(self):
    #     """
    #     # cannot exsit multiple target , especially target + multi lib ?
    #     # if not , cannot judge which srcs should be compiled
    #     """
    #     targets_ = [tgt for tgt in self.mixed_commands if isinstance(tgt, str)]
    #     if len(targets_) > 1:
    #         log.error(f"Exist multiple target. {targets_}")
    #         self.target_type = ""
    #         self.target = ""
    #         return

    #     if len(targets_) == 0:
    #         self.target_type = ""
    #         self.target = ""
    #         return

    #     for tgt in self.mixed_commands:
    #         if tgt in self.targets:
    #             self.target_type = self.targets[tgt]["typ"]
    #             self.target = Targets(**self.targets[tgt])
    #             break
    #     log.info(f"target_type: {self.target_type}  target: {self.target}   ")

    def __parse_parties(self):
        self.parties_parsed = {}
        for party in self.parties.values():
            # log.error(f"party: {party}")
            partt_3rd = "GENERIC"
            if party.get("third_party", ""):
                partt_3rd = party.get("third_party", "")
            if partt_3rd not in PARTIES_DCT.keys():
                log.error(f"third_party [{partt_3rd}] not in PARTIES_DCT")
            party_cls = PARTIES_DCT.get(partt_3rd, GenericParty)
            party_obj = party_cls(**party)
            # DEPENDS
            if party_obj.name in self.depends:
                party_obj.depends.extend(self.depends[party_obj.name].get("depends", []))
            self.parties_parsed.update({party_obj.name: party_obj})
        # log.error(f"parties_parsed: {self.target}")
        if self.target:
            party_cls = PARTIES_DCT.get("_DEFAULT", GenericParty)
            party_obj = party_cls("_DEFAULT", ".")
            if self.target.sources:
                for src in self.target.sources:
                    if isinstance(src, str):
                        party_obj.srcs.append(Path(src))
                    elif isinstance(src, Path):
                        party_obj.srcs.append(src)
            self.parties_parsed.update({party_obj.name: party_obj})
        pass

    def __parse_mode(self):
        dct = {"ninja": self.ninja, "cache": self.cache, "compiledb": self.compiledb}
        mode_dct = {}
        for k, v in dct.items():
            if v:
                mode_dct[k] = v
        size = len(mode_dct)
        # log.error(f"dct: {dct}  {mode_dct}  size: {size}")
        if size > 1:
            log.warn(f"Exist multiple mode. {mode_dct}")
            self.mode = ""
        elif size == 1:
            self.mode = list(mode_dct.keys())[0]

        mode = self.toml if self.toml else self.party
        # log.info(f"mode: {mode} {self.parties_parsed.get(mode, None)}")
        if not mode:
            return
        mode = mode.upper()
        log.info(f"mode: {mode} {self.parties_parsed.get(mode, None)}")
        if self.parties_parsed.get(mode, None):
            self.toml = mode
            self.mode = "toml"
        else:
            log.warn(f"No party {mode} available for TOML")
            exit(1)
        pass

    def __mode(self):
        log.info(f"mode: [{self.mode}]  {self.target_commands_generated}")
        if not self.mode:
            exit(1)

        if self.mode in ["build", "ninja", "cache", "compiledb"]:
            self.__command(self.mixed_commands)
            if self.target_commands_generated:
                self.__target_commands()
        log.info(f"mode: [{self.mode}]  {self.target_commands_generated}")

        match self.mode:
            case "clean":
                self.clean = True
                self.__clean()
                return
            case "cache":
                self.__command(self.mixed_commands)
                if self.target_commands_generated:
                    self.__target_commands()
                    self.__tracker()
                else:
                    log.warn("target is empty. Failed to build cache!")
                return
            case "build":
                self.__pre_build()
                self.__mybuild()
                self.__post_build()
                return
            case "ninja":
                self.__command(self.mixed_commands)
                if self.target_commands_generated:
                    self.__target_commands()
                    # self.__tracker()
                    self.__ninja()
                else:
                    log.warn("target is empty. Failed to generate ninja!")
                return
            case "compiledb":
                self.__command(self.mixed_commands)
                if self.target_commands_generated:
                    self.__target_commands()
                    # self.__tracker()
                    self.__compiledb()
                else:
                    log.warn("target is empty. Failed to generate compile json!")
                return
            case "toml":
                # log.info(f"mode toml -> : {self.toml}")
                self.__toml_party()
                return

    def __clean(self):
        if not self.clean:
            return
        log.info(f"clean: {self.mode}")
        dir = Path(self.helper["BUILDDIR"])

        # check build dir exists or not
        if not dir.exists():
            log.warn(f"目录不存在: {dir}")
            return

        for item in dir.iterdir():
            # print(item)
            if item.is_file():
                try:
                    item.unlink()
                except PermissionError as e:
                    log.warn(f"权限不足，无法删除 {item}: {e}")
                except Exception as e:
                    log.warn(f"删除 {item} 时发生错误: {e}")
            else:
                try:
                    shutil.rmtree(item)
                except Exception as e:
                    log.warn(f"删除目录 {item} 时发生错误: {e}")
        exit(0)

    def __target_commands(self):
        # log.debug(f"mixed_commands  : {self.mixed_commands}")
        for tgt in self.mixed_commands:
            log.debug(f"mixed_commands  : {tgt}")
            if isinstance(tgt, str) and self.target:
                btc = BuildTargetCommands(
                    self.helper, self.target, self.parties_parsed, self.target_type
                )
                # log.debug(f"__target_commands before run.")
                self.target_commands = btc.run()
                # log.debug(f"__target_commands::build target commands ok.")
                continue

    def __cache(self):
        # log.debug(f"__cache mixed_commands: {self.mixed_commands} {self.target}")
        for tgt_cmd in self.mixed_commands:
            # log.debug(f"mixed_commands vvv: {tgt_cmd}")
            if isinstance(tgt_cmd, str) and self.target:
                # bt = BuildTarget(self.helper, self.target, self.parties_parsed, self.target_type)
                # self.target_commands = bt.run()
                # log.debug(f"cache::build target ok.")
                # # self.__tracker()
                # # log.debug(f"cache::tracker ok.")
                # self.target_generated = True
                # self.target_commands_generated = True
                self.__command([])
                self.target_commands_generated = True
                continue
            if isinstance(tgt_cmd, list):
                # log.info(f"CMD: {tgt_cmd}  command")
                self.__command(tgt_cmd)
                continue
        if self.target_commands:
            self.__tracker()
            log.debug("cache::tracker ok.  ")
        # log.debug(f"__cache mixed_commands: {self.mixed_commands}")

    def __compiledb(self):
        log.info(f"compiledb: {self.mode}")
        self._compiledb = Compiledb(self.helper, self.target_commands)
        log.info(f"compiledb: {self.mode}")

    def __ninja(self):
        log.info(f"ninja: {self.mode}")
        # flags = {
        #     "CFLAGS": self.helper.get("CFLAGS", []),
        #     "CXXFLAGS": self.helper.get("CXXFLAGS", []),
        #     "ASFLAGS": self.helper.get("ASFLAGS", []),
        #     "ARFLAGS": self.helper.get("ARFLAGS", []),
        #     "LDFLAGS": self.helper.get("LDFLAGS", []),
        # }
        self._ninja = Ninja(
            self.helper,
            self.target_commands,
            self.parties_parsed,
            target=self.target,
            default_target=self.helper.get("TARGET", ""),
            phonies=self.phonies,
            commands=self.commands,
        )
        self._ninja.gen()
        log.info(f"ninja: {self.mode}")

    def __mybuild(self):
        # objs = self.target_commands.get("OBJECTS", None)
        # libs = self.target_commands.get("LIBS", None)
        # tgts = self.target_commands.get("TARGETS", None)

        # log.debug(f"tracker: 0")
        cache_file = CACHE_FILENAME
        self.tracker = Tracker(
            self.target_commands, cache_file, fmt="json", executor=self._executor
        )
        # self.tracker.Invalid()
        self.tracker.build_cache_reset()

        # mb = MyBuilder()
        self.mb.set_tracker(self.tracker)
        self.mb.set_executor(self._executor)
        self.mb.set_target_commands(self.target_commands)

        self.mb.target()
        size_cmd_str = self.__size_cmd()
        if size_cmd_str:
            self.mb.command([size_cmd_str])

        # self.mb.target_test_track()
        # mb.run()

    def __tracker(self):
        objs = self.target_commands.get("OBJECTS", None)
        libs = self.target_commands.get("LIBS", None)
        tgts = self.target_commands.get("TARGETS", None)

        # log.debug(f"tracker: 0")
        cache_file = CACHE_FILENAME
        self.tracker = Tracker(
            self.target_commands, cache_file, fmt="json", executor=self._executor
        )
        # self.tracker.Invalid()
        self.tracker.build_cache_reset()

        for k, v in objs.items():
            self.tracker.Track(k, v)
        for k, v in libs.items():
            self.tracker.Track(k, v)
        for k, v in tgts.items():
            self.tracker.Track(k, v)
        self.tracker._save()
        # log.warn(f"tracker: {self.tracker.cache['TARGETS']}")
        # log.warn(f"tracker: {self.tracker.cache['LIBS']}")
        # t = Thread(target=self.tracker.Refresh)
        # t.start()
        # t.join()
        # log.info(f"tracker: end")

    def __build(self):
        # log.info(f"__build verbose:{self.verbose}, silent:{self.silent}, dry_run:{self.dry_run}")
        log.info(f"__build target_generated:{self.target_commands_generated} target:{self.target}")
        self.__pre_build()

        if not self.target:
            self.__post_build()
            return

        if not self.tracker:
            log.warn("tracker is None")
        self.valid_commands = self.tracker._get_valid_commands()
        # log.info(f"valid_commands: {self.valid_commands}")
        # log.info(f"valid_commands: {self.valid_commands.get('LIBS')}")
        # log.info(f"valid_commands: {self.valid_commands.get('OBJECTS')}")
        # log.info(f"valid_commands target: {self.valid_commands.get('TARGETS')}")
        valid = [len(self.valid_commands.get(key, {})) for key in self.valid_commands.keys()]
        # log.info(f"valid_commands: {valid}")
        if not any(valid):
            log.warn("no  build item in obj lib target! ")
            self.target_generated = True
            self.__post_build()
            return

        if self.dry_run:
            log.debug("============ dry_run: ===========")
        else:
            self.builder.SetCommands(self.valid_commands)
            self.builder.verbose = self.verbose
            self.builder.silent = self.silent
            self.builder.dry_run = self.dry_run
            self.builder.max_workers = self.jobs
            self.builder.build()
            # self.builder.install(self.target_type)

        # log.debug(f"__size: {self.target}")
        self.target_generated = True
        if self.target and self.target.typ == "TARGETS":
            self.__size()
        self.__post_build()

    def __size(self):
        cmds = []
        # print(self.target_type, self.helper["TARGET_SUFFIX"].upper(), self.builder.target)
        if self.builder.target and self.helper["TARGET_SUFFIX"].upper() == ".ELF":
            cmd = f"{self.helper['SIZE']} {self.builder.target}"
            cmds.append(cmd)
        # print(cmd, "000")
        if self.dry_run:
            log.output(f"{cmd}")
            return
        if cmds:
            self._exec_cmd(cmd, verbose="verbose", is_compile=False)

    def __size_cmd(self):
        cmd = None
        if self.target_type == "TARGETS" and self.helper["TARGET_SUFFIX"].upper() == ".ELF":
            cmd = f"{self.helper['SIZE']} {self.target_out}"
        return cmd

    def __pre_build(self):
        if self.dry_run:
            for cmd in self.pre_commands:
                log.output(f"\n[pre_build]: {cmd}")
            return

        log.output(" ==== Precommands: Before Builiding  ==== ")
        log.info(f" verbose: {self.verbose} ")
        self.mb.verbose = self.verbose
        self.mb.silent = self.silent
        self.mb.dry_run = self.dry_run
        self.mb.command(self.pre_commands)
        # self._exec_cmd(
        #     self.pre_commands,
        #     parallel=False,
        #     max_workers=4,
        #     fail_fast=True,
        #     show_command=True,  # display command
        #     show_output=True,  # display output
        #     verbose=self.verbose,
        #     is_compile=False,
        # )

    def __post_build(self):
        # log.warn(f"__post_build: {self.post_commands} --- {self.dry_run}")
        if self.dry_run:
            for cmd in self.post_commands:
                log.output(f"\n[post_build]: {cmd}")
            return
        log.output(" ==== Postcommands: After Builiding  ==== ")
        log.debug(self.post_commands)

        if self.post_commands:
            self._exec_cmd(
                self.post_commands,
                parallel=False,
                max_workers=4,
                fail_fast=True,
                show_command=True,  # display command
                show_output=True,  # display output
                verbose=self.verbose,
                is_compile=False,
            )

    def __command(self, command: list[str]):
        self.target_commands_generated = False
        self.pre_commands = []
        self.post_commands = []
        for tgt_cmd in self.mixed_commands:
            if isinstance(tgt_cmd, str) and self.target:
                self.target_commands_generated = True
                continue
            if isinstance(tgt_cmd, list):
                if not self.target_commands_generated:
                    self.pre_commands.extend(tgt_cmd)
                else:
                    self.post_commands.extend(tgt_cmd)
        pass

    def dict_to_toml(self, data: dict) -> str:
        """
        纯原生Python实现：字典转 TOML 字符串，无第三方库
        自动递归转换 Path 对象为字符串
        """
        tables = []

        def normalize_val(val):
            # Path 对象转字符串
            if isinstance(val, Path):
                return str(val)
            # 布尔
            if isinstance(val, bool):
                return "true" if val else "false"
            # 数字直接转字符串
            if isinstance(val, (int, float)):
                return str(val)
            # 字符串 加双引号
            if isinstance(val, str):
                return f'"{val}"'
            # 列表处理
            if isinstance(val, (list, tuple)):
                items = ", ".join(normalize_val(i) for i in val)
                return f"[{items}]"
            raise TypeError(f"不支持类型: {type(val)}")

        def handle_table(table_data: dict, parent_name: str = ""):
            for k, v in table_data.items():
                full_key = f"{parent_name}.{k}" if parent_name else k
                if isinstance(v, dict):
                    # 嵌套字典 = TOML table
                    tables.append(f"[{full_key}]")
                    handle_table(v, full_key)
                else:
                    # 普通键值，放到对应table下
                    tables.append(f"{k} = {normalize_val(v)}")

        handle_table(data)
        return "\n".join(tables)

    def __toml_party(self):
        log.info(f"toml_party: {self.toml}")
        party = self.parties.get(self.toml, {})
        party_obj = GenericParty(**party)
        dct = {
            "target": {},
        }
        dct["target"].update({"srcs": party_obj.sources()})
        dct["target"].update({"incs": party_obj.include_dirs()})
        pymake_toml = party_obj.dir / TOML_PYMAKEX
        if pymake_toml.exists():
            log.warn(f"file: {pymake_toml} has exists")
        log.output()
        log.output(f"pls copy the followed text to {pymake_toml}  ")
        log.output()
        out_str = self.dict_to_toml(dct)

        log.output("#" * 40)
        log.output(f"{out_str}")
        log.output("#" * 40)

    def _exec_cmd(
        self,
        commands: str | list[str],
        *,
        parallel: bool = False,
        max_workers: int | None = None,
        stop_on_error: bool = False,
        fail_fast: bool = False,
        show_command: bool = True,
        show_output: bool = True,
        verbose: bool = False,  # verbose | silent |simple
        is_compile: bool = True,
    ) -> list:
        """
        执行命令，支持单条顺序、多条顺序、多条并行三种模式。
        并行模式下每条命令执行完毕立即打印日志，支持遇错即停。

        Args:
            commands: 单条命令字符串，或多条命令的列表
            parallel: True 并行执行，False 顺序执行
            max_workers: 并行时最大线程数，默认 CPU 核心数
            stop_on_error: 顺序执行时遇错停止后续
            fail_fast: 并行执行时任一条失败即取消剩余
            show_command: 是否打印命令
            show_output: 是否打印 stderr

        Returns:
            CmdResult 列表

        examples:
            builder._exec_cmd(cmd, parallel=True, fail_fast=True)
                │
                └── self._executor.exec_commands(..., on_result=_on_result)
                        │
                        ├── 顺序 ── _exec_sequential ── for cmd: self.run() → on_result()
                        │
                        └── 并行 ── _exec_parallel ── ThreadPoolExecutor
                                    │  as_completed → on_result() 即完即报
                                    │  fail_fast → 取消剩余 futures
                                    └  exception → CmdResult(returncode=-1, ...)
        """

        def _on_result(cmd_str: str, r) -> None:
            # if show_command:
            #     log.info(f"{cmd_str}\n")
            if show_output and r.stderr:
                log.output(f"{r.stderr}\n")

        return self._executor.exec_commands(
            commands,
            parallel=parallel,
            max_workers=max_workers,
            stop_on_error=stop_on_error,
            fail_fast=fail_fast,
            on_result=_on_result,
            verbose=verbose,
            is_compile=is_compile,
        )
