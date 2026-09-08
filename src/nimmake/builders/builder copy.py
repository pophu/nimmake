"""
builder — 多组件编译命令行生成器

将多个 ThirdParty 组装，解析依赖顺序，
为每个源文件生成完整的编译命令行。
"""

from __future__ import annotations

from pathlib import Path

from nimmake.builders.CommandBuilder import ParallelQueue, SequentialQueue
from nimmake.executor import CmdExecutor, CmdExecutorCli
from nimmake.utils import log

# from .parseParties import ParseParties
from .Tracker import Tracker


class MyBuilder:
    """
    -Q --quiet ，donotdisplay program log
    -s --silent ，donotdisplay any log, hide cmd, like "gcc  -- "
    --dry_run ，donot run any command, just print it
    --verbose ，display verbose log, cmd return code

    """

    def __init__(
        self,
        commands: dict | None = None,
        tracker: Tracker | None = None,
        executor: CmdExecutor | None = None,
        max_workers: int = 1,
        dry_run: bool = False,
        verbose: bool = False,
        silent: bool = False,
        toolpath: str = None,
        parallel: bool = True,
        # jobs: int = 1,
        *args,
        **kwargs,
    ):
        self.commands = commands or {}
        self._executor = executor
        self.toolpath = toolpath
        self.max_workers = max_workers
        self.dry_run = dry_run
        self.verbose = verbose
        self.silent = silent
        self.parallel = parallel or True

        # self._quiet = False
        self._silent = False
        self._verbose = False
        self._dry_run = False
        self.parse_mode("")

        log.info(f"BUILDER-> verbose:{self.verbose},dry_run:{self.dry_run},silent:{self.silent}")

        self.tracker = tracker
        self._current_queue = None

        if not self._executor:
            self._executor = CmdExecutorCli()
        if self.toolpath:
            self._executor.add_path(self.toolpath, prepend=True)

    def parse_mode(self, mode: str) -> None:
        if self.dry_run:
            self._dry_run = True
            self._verbose = False
            self._silent = False
            return
        if self.verbose:
            self._verbose = True
            self._silent = False
            return
        if self.silent:
            self._silent = True
            self._verbose = False
        # self._quiet =False
        # self._silent = self.silent
        # self._verbose = self.verbose
        # self._dry_run = self.dry_run

    def set_parallel(self, parallel: bool) -> None:
        self.parallel = parallel

    def set_tracker(self, tracker: Tracker) -> None:
        self.tracker = tracker

    def set_executor(self, executor: CmdExecutor) -> None:
        self._executor = executor

    def set_target_commands(self, commands: dict) -> None:
        self.commands = commands
        # log.info(f"set_target_commands {self.commands}")

    def __parallel(self, outs: dict[str, list[str]]):
        pq = ParallelQueue(
            _parallelexecutor__max_workers=self.max_workers,
            _parallelexecutor__executor=self._executor,
            _parallelexecutor__tracker=self.tracker,
            _parallelexecutor__dry_run=self._dry_run,
            _parallelexecutor__verbose=self._verbose,
            _parallelexecutor__silent=self._silent,
        )
        self._current_queue = pq

        # log.info(pq._parallelexecutor.__dict__)
        log.info(f"__parallel  self._verbose: {self._verbose}")

        pq.start()
        for out, cmdlst in outs.items():
            # cmdlst = self.tracker.commands["OBJECTS"][out]
            out_pth = Path(out).parent
            if not out_pth.exists():
                out_pth.mkdir(parents=True, exist_ok=True)

            pq.add(cmdlst, out)

        pq.wait()
        log.debug(f"finish {len(pq._parallelexecutor.results)} items")
        pq.stop()
        self._current_queue = None

    def __sequential(self, outs: dict[str, list[str]]):
        pq = SequentialQueue(
            # _sequentialexecutor__max_workers=8,
            _sequentialexecutor__executor=self._executor,
            _sequentialexecutor__tracker=self.tracker,
            _sequentialexecutor__dry_run=self._dry_run,
            _sequentialexecutor__verbose=self._verbose,
            _sequentialexecutor__silent=self._silent,
        )
        self._current_queue = pq

        # log.info(pq._sequentialexecutor.__dict__)
        pq.start()
        for out, cmdlst in outs.items():
            # cmdlst = self.tracker.commands["OBJECTS"][out]
            out_pth = Path(out).parent

            if not out_pth.exists():
                out_pth.mkdir(parents=True, exist_ok=True)
            pq.add(cmdlst, out)

        pq.wait()
        log.debug(f"finish {len(pq._sequentialexecutor.results)} items")
        pq.stop()
        self._current_queue = None

    def command(self, outs: list[str]) -> None:
        pq = SequentialQueue(
            # _sequentialexecutor__max_workers=8,
            _sequentialexecutor__executor=self._executor,
            _sequentialexecutor__tracker=self.tracker,
            _sequentialexecutor__dry_run=self._dry_run,
            _sequentialexecutor__verbose=self._verbose,
        )

        # log.info(pq._sequentialexecutor.__dict__)
        pq.start()
        for cmd in outs:
            pq.add(cmd)

        pq.wait()
        pq.stop()

    def run(self, outs: dict[str, list[str]]) -> None:
        # objs = self.commands.get("OBJECTS", {})
        try:
            if self.parallel:
                self.__parallel(outs)
            else:
                self.__sequential(outs)
        except KeyboardInterrupt:
            log.warn("Ctrl+C received, stopping build...")
            if self._current_queue is not None:
                self._current_queue.stop()
                self._current_queue = None

    def target(
        self,
    ) -> None:
        objs = self.commands.get("OBJECTS", {})
        libs = self.commands.get("LIBS", {})
        tgts = self.commands.get("TARGETS", {})

        # for k, v in self.tracker.cache["OBJECTS"].items():
        #     log.info(f"target: {k} {v['mtime']}")

        if objs:
            if self.parallel:
                self.__parallel(objs)
            else:
                self.__sequential(objs)
        if libs:
            self.__sequential(libs)
        if tgts:
            self.__sequential(tgts)
        # for k, v in self.tracker.cache["OBJECTS"].items():
        #     log.info(f"target: {k} {v['mtime']}")
        self.tracker._save()

    def target_test_track(
        self,
    ) -> None:
        """
        test self.tracker.Track
        """
        objs = self.commands.get("OBJECTS", {})
        libs = self.commands.get("LIBS", {})
        tgts = self.commands.get("TARGETS", {})

        # for k, v in self.tracker.cache["OBJECTS"].items():
        #     log.info(f"target: {k} {v['mtime']}")

        # for obj, cmdlst in objs.items():
        #     # if "_DEFAULT/1.o" not in obj:
        #     #     continue
        #     cmd, is_valid = self.tracker.Track(obj, cmdlst)
        #     log.warn(obj, is_valid)
        #     pass
        for lib, cmdlst in libs.items():
            cmd, is_valid = self.tracker.Track(lib, cmdlst)
            log.warn("[lib] ", lib, is_valid)
            pass
        for tgt, cmdlst in tgts.items():
            cmd, is_valid = self.tracker.Track(tgt, cmdlst)
            log.warn("[tgt] ", tgt, is_valid)
        # self.tracker._save()

    def build(self) -> None:
        print("\n===== 3. 注入顺序执行器 =====")
        sq = SequentialQueue()
        sq.start()
        sq.add("echo 步骤1")
        sq.add("echo 步骤2")
        sq.add("echo 步骤3")
        sq.wait()
        sq.stop()


# class BuilderCli:
#     """
#     dry run  -- no
#     silent  -- didnot display obj command result
#     verbose  -- display obj command and result
#     installed: bool = False
#     can run in another subporcess
#     """

#     def __init__(
#         self,
#         commands: dict[str, str] = None,
#         executor: CmdExecutorCli = None,
#         max_workers: int = 1,
#         dry_run: bool = False,
#         verbose: bool = False,
#         silent: bool = False,
#         toolpath: str = None,
#         # jobs: int = 1,
#         *args,
#         **kwargs,
#     ):
#         """
#         Args:
#             parties: 组件列表
#             global_options: 全局编译选项（如 "-O2 -g -Wall"），与 flags/toolchain 二选一
#         """
#         log.output(" ")
#         log.output("====  Builder init  ====")
#         log.output(" ")

#         self.target = ""

#         self.commands = commands or {}
#         self._executor = executor
#         self.toolpath = toolpath
#         self.max_workers = max_workers
#         self.dry_run = dry_run
#         self.verbose = verbose
#         self.silent = silent

#         log.info(f"BUILDER-> verbose:{self.verbose},dry_run:{self.dry_run},silent:{self.silent}")

#         if not self._executor:
#             self._executor = CmdExecutorCli()
#         if self.toolpath:
#             self._executor.add_path(self.toolpath, prepend=True)

#         self.target_dirs = []
#         # self.build()

#     def SetCommands(self, commands: dict[str, str]) -> None:
#         self.commands = commands

#     def _check_out_dir(self, obj: str) -> None:
#         obj_path: Path = Path(obj)
#         if obj_path.parent not in self.target_dirs:
#             if not obj_path.parent.exists():
#                 obj_path.parent.mkdir(parents=True, exist_ok=True)
#                 self.target_dirs.append(obj_path.parent)

#     def build(self) -> None:
#         log.debug(
#             f"builder verbose: {self.verbose}  silent: {self.silent}  dry_run: {self.dry_run}"
#         )
#         self.__build_objs()
#         self.__build_libs()
#         self.__build_targets()

#         # log.debug(f"builder end ... , modify cache... ")

#         # log.debug(f"builder end ... , modify cache... ")
#         # log.debug(f"if lib, install")
#         pass

#     def install(self, target_type: str) -> None:
#         if not target_type:
#             return
#         if target_type == "target":
#             log.debug(" target, install, to do ...")
#             # self.__install_target()
#         else:
#             log.debug(" lib, install, to do ...")
#             # self.__install_lib()
#         pass

#     def __build_objs_seq(self) -> bool:
#         cmds = []
#         objs = self.commands.get("OBJECTS", {})
#         for obj, cmd in objs.items():
#             self._check_out_dir(obj)
#             cmds.append(cmd)

#         if not cmds:
#             log.warn("no OBJECTS commands to execute")
#             return False

#         if self.dry_run:
#             for cmd in cmds:
#                 log.info(f" {cmd}")
#             return True

#         mode_ = True if self.verbose else False
#         mode_ = True
#         log.error(f"mode_: {mode_}")
#         self._exec_cmd(
#             cmds,
#             parallel=False,
#             max_workers=self.max_workers,
#             fail_fast=True,
#             show_command=True,  # display command
#             show_output=True,  # display output
#             verbose=self.verbose,
#         )
#         return True

#         # try:
#         #     # results = self._exec_cmd(cmds, parallel=True, max_workers=4, fail_fast=True)
#         #     results = self._exec_cmd(
#         #         cmds,
#         #         parallel=True,
#         #         max_workers=4,
#         #         fail_fast=True,
#         #         show_command=False,
#         #         show_output=False,
#         #     )
#         #     # log.warn(f"results: {results}")

#         #     failed = [r for r in results if r]
#         #     if failed:
#         #         log.error(f"{len(failed)}/{len(results)} commands failed")
#         #         for r in failed[:3]:
#         #             log.output(f"  FAIL: {r.command}")
#         #             if r.stderr:
#         #                 log.output(f"        {r.stderr.strip()}")
#         #     else:
#         #         log.info(f"all {len(results)} objs succeeded")

#         # except Exception as e:
#         #     log.error(f"build obj exception: {type(e).__name__}: {e}")

#     def __build_objs(self) -> bool:
#         cmds = []
#         objs = self.commands.get("OBJECTS", {})
#         for obj, cmd in objs.items():
#             self._check_out_dir(obj)
#             cmds.append(cmd)

#         if not cmds:
#             log.warn("no compiled objects ")
#             # return False

#         # dry_run, not execute command
#         if self.dry_run:
#             for cmd in cmds:
#                 log.info(f" {cmd}")
#             return True

#         # mode_ = "verbose" if self.verbose else "simple"
#         # log.debug(f"mode_ verbose: {mode_}  ")
#         verbose_ = True if self.verbose else False
#         log.debug(f"mode_ verbose: {verbose_}  ")

#         try:
#             # results = self._exec_cmd(cmds, parallel=True, max_workers=4, fail_fast=True)
#             results = self._exec_cmd(
#                 cmds,
#                 parallel=True,
#                 max_workers=self.max_workers,  # 4
#                 fail_fast=True,
#                 show_command=False,
#                 show_output=False,
#                 verbose=verbose_,
#             )
#             # log.warn(f"results: {results}")

#             failed = [r for r in results if r]
#             if failed:
#                 log.error(f"{len(failed)}/{len(results)} commands failed")
#                 for r in failed[:3]:
#                     log.output(f"  FAIL: {r.command}")
#                     if r.stderr:
#                         log.output(f"        {r.stderr.strip()}")
#                 exit(1)
#                 return False
#             else:
#                 log.info(f"all {len(results)} objs succeeded")

#             # if results:
#             #     failed = [r for r in results if not r.success]
#             #     if failed:
#             #         log.error(f"{len(failed)}/{len(results)} commands failed")
#             #         for r in failed[:3]:
#             #             log.output(f"  FAIL: {r.command}")
#             #             if r.stderr:
#             #                 log.output(f"        {r.stderr.strip()}")
#             # else:
#             #     log.info(f"all {len(results)} commands succeeded")
#         except Exception as e:
#             log.error(f"build obj exception: {type(e).__name__}: {e}")
#             return False

#         return True

#     def __build_libs(self) -> None:
#         # log.debug(f"builder execute lib  ... ")
#         libs = self.commands.get("LIBS", {})
#         # log.debug(f"builder execute lib  ...  {libs}")
#         for _lib, cmd in libs.items():
#             if self.dry_run:
#                 log.info(f"{cmd}")
#                 continue
#             self._check_out_dir(_lib)
#             r = self._executor.run(cmd)
#             log.output(r.command)
#             if r.stderr:
#                 log.output(r.stderr)
#                 return

#     def __build_targets(self) -> None:
#         log.debug("builder __build_targets  ... ")
#         tgts = self.commands.get("TARGETS", {})
#         for _tgt, cmd in tgts.items():
#             if self.dry_run:
#                 log.info(f"{cmd}")
#                 continue
#             self._check_out_dir(_tgt)
#             r = self._executor.run(cmd)
#             log.output(r.command)
#             if r.stderr:
#                 log.output(r.stderr)
#             self.target = _tgt

#     def _exec_cmd(
#         self,
#         commands: str | list[str],
#         *,
#         parallel: bool = False,
#         max_workers: int | None = None,
#         stop_on_error: bool = False,
#         fail_fast: bool = False,
#         show_command: bool = True,
#         show_output: bool = True,
#         verbose: bool = False,  # verbose |simple
#     ) -> list:
#         """
#         执行命令，支持单条顺序、多条顺序、多条并行三种模式。
#         并行模式下每条命令执行完毕立即打印日志，支持遇错即停。

#         Args:
#             commands: 单条命令字符串，或多条命令的列表
#             parallel: True 并行执行，False 顺序执行
#             max_workers: 并行时最大线程数，默认 CPU 核心数
#             stop_on_error: 顺序执行时遇错停止后续
#             fail_fast: 并行执行时任一条失败即取消剩余
#             show_command: 是否打印命令
#             show_output: 是否打印 stderr

#         Returns:
#             CmdResult 列表

#         examples:
#             builder._exec_cmd(cmd, parallel=True, fail_fast=True)
#                 │
#                 └── self._executor.exec_commands(..., on_result=_on_result)
#                         │
#                         ├── 顺序 ── _exec_sequential ── for cmd: self.run() → on_result()
#                         │
#                         └── 并行 ── _exec_parallel ── ThreadPoolExecutor
#                                     │  as_completed → on_result() 即完即报
#                                     │  fail_fast → 取消剩余 futures
#                                     └  exception → CmdResult(returncode=-1, ...)
#         """

#         def _on_result(cmd_str: str, r) -> None:
#             # if show_command:
#             #     log.info(f"{cmd_str}\n")
#             if show_output and r.stderr:
#                 log.output(f"{r.stderr}\n")

#         return self._executor.exec_commands(
#             commands,
#             parallel=parallel,
#             max_workers=max_workers,
#             stop_on_error=stop_on_error,
#             fail_fast=fail_fast,
#             on_result=_on_result,
#             verbose=verbose,
#         )


# class Builder:
#     """
#     dry run  -- no
#     silent  -- didnot display obj command result
#     verbose  -- display obj command and result
#     installed: bool = False
#     """

#     def __init__(
#         self,
#         commands: dict[str, str] = None,
#         executor: CmdExecutor = None,
#         max_workers: int = 4,
#         dry_run: bool = False,
#         verbose: bool = False,
#         silent: bool = False,
#         toolpath: str = None,
#         *args,
#         **kwargs,
#     ):
#         """
#         Args:
#             parties: 组件列表
#             global_options: 全局编译选项（如 "-O2 -g -Wall"），与 flags/toolchain 二选一
#         """
#         log.output(" ")
#         log.output("====  Builder init  ====")
#         log.output(" ")

#         self.commands = commands or {}
#         self._executor = executor
#         self.toolpath = toolpath
#         self.max_workers = max_workers
#         self.dry_run = dry_run
#         self.verbose = verbose
#         self.silent = silent

#         log.info(f"toolpath: {self.toolpath}")

#         if not self._executor:
#             self._executor = CmdExecutor()
#         if self.toolpath:
#             self._executor.add_path(self.toolpath, prepend=True)

#         self.target_dirs = []
#         self.__build()

#     def _check_out_dir(self, obj: str) -> None:
#         obj_path: Path = Path(obj)
#         if obj_path.parent not in self.target_dirs:
#             if not obj_path.parent.exists():
#                 obj_path.parent.mkdir(parents=True, exist_ok=True)
#                 self.target_dirs.append(obj_path.parent)

#     def __build(self) -> None:
#         log.error("builder execute target  ... ")
#         # self.__build_targets()
#         # self.__build_libs()
#         self.__build_objs()
#         self.__build_libs()
#         self.__build_targets()

#         log.error("builder end ... , modify cache... ")
#         log.error("if lib, install")
#         pass

#     def __build_objs_seq(self) -> None:
#         cmds = []
#         objs = self.commands.get("OBJECTS", {})
#         for obj, cmd in objs.items():
#             self._check_out_dir(obj)
#             cmds.append(cmd)

#         if not cmds:
#             log.warn("no OBJECTS commands to execute")
#             return

#         self._executor.run_batch(["echo x", "echo y"], stop_on_error=True)

#         # try:
#         #     # results = self._exec_cmd(cmds, parallel=True, max_workers=4, fail_fast=True)
#         #     results = self._exec_cmd(
#         #         cmds,
#         #         parallel=True,
#         #         max_workers=4,
#         #         fail_fast=True,
#         #         show_command=False,
#         #         show_output=False,
#         #     )
#         #     # log.warn(f"results: {results}")

#         #     failed = [r for r in results if r]
#         #     if failed:
#         #         log.error(f"{len(failed)}/{len(results)} commands failed")
#         #         for r in failed[:3]:
#         #             log.output(f"  FAIL: {r.command}")
#         #             if r.stderr:
#         #                 log.output(f"        {r.stderr.strip()}")
#         #     else:
#         #         log.info(f"all {len(results)} objs succeeded")

#         # except Exception as e:
#         #     log.error(f"build obj exception: {type(e).__name__}: {e}")

#     def __build_objs(self) -> None:
#         cmds = []
#         objs = self.commands.get("OBJECTS", {})
#         for obj, cmd in objs.items():
#             self._check_out_dir(obj)
#             cmds.append(cmd)

#         if not cmds:
#             log.warn("no OBJECTS commands to execute")
#             return

#         try:
#             # results = self._exec_cmd(cmds, parallel=True, max_workers=4, fail_fast=True)
#             self._executor.run_parallel(
#                 ["echo x", "echo y"], max_workers=4, stop_on_error=True
#             )  # failed = [r for r in results if r]
#             # if failed:
#             #     log.error(f"{len(failed)}/{len(results)} commands failed")
#             #     for r in failed[:3]:
#             #         log.output(f"  FAIL: {r.command}")
#             #         if r.stderr:
#             #             log.output(f"        {r.stderr.strip()}")
#             # else:
#             #     log.info(f"all {len(results)} objs succeeded")

#             # if results:
#             #     failed = [r for r in results if not r.success]
#             #     if failed:
#             #         log.error(f"{len(failed)}/{len(results)} commands failed")
#             #         for r in failed[:3]:
#             #             log.output(f"  FAIL: {r.command}")
#             #             if r.stderr:
#             #                 log.output(f"        {r.stderr.strip()}")
#             # else:
#             #     log.info(f"all {len(results)} commands succeeded")
#         except Exception as e:
#             log.error(f"build obj exception: {type(e).__name__}: {e}")

#     def __build_libs(self) -> None:
#         log.error("builder execute lib  ...  ")
#         libs = self.commands.get("LIBS", {})
#         log.error(f"builder execute lib  ... {libs} ")
#         for _lib, cmd in libs.items():
#             self._check_out_dir(_lib)
#             self._executor.run(cmd)

#     def __build_targets(self) -> None:
#         log.error("builder __build_targets  ... ")
#         tgts = self.commands.get("TARGETS", {})
#         for _tgt, cmd in tgts.items():
#             # log.error(f"builder __build_targets  ... {_tgt}")
#             self._check_out_dir(_tgt)
#             r = self._executor.run(cmd)
#             print(r.command)
#             if r.stderr:
#                 print(r.stderr)

#     def _exec_cmd(
#         self,
#         commands: str | list[str],
#         *,
#         parallel: bool = False,
#         max_workers: int | None = None,
#         stop_on_error: bool = False,
#         fail_fast: bool = False,
#         show_command: bool = True,
#         show_output: bool = True,
#         mode: str = "simple",  # verbose | silent |simple
#     ) -> list:
#         """
#         执行命令，支持单条顺序、多条顺序、多条并行三种模式。
#         并行模式下每条命令执行完毕立即打印日志，支持遇错即停。

#         Args:
#             commands: 单条命令字符串，或多条命令的列表
#             parallel: True 并行执行，False 顺序执行
#             max_workers: 并行时最大线程数，默认 CPU 核心数
#             stop_on_error: 顺序执行时遇错停止后续
#             fail_fast: 并行执行时任一条失败即取消剩余
#             show_command: 是否打印命令
#             show_output: 是否打印 stderr

#         Returns:
#             CmdResult 列表

#         examples:
#             builder._exec_cmd(cmd, parallel=True, fail_fast=True)
#                 │
#                 └── self._executor.exec_commands(..., on_result=_on_result)
#                         │
#                         ├── 顺序 ── _exec_sequential ── for cmd: self.run() → on_result()
#                         │
#                         └── 并行 ── _exec_parallel ── ThreadPoolExecutor
#                                     │  as_completed → on_result() 即完即报
#                                     │  fail_fast → 取消剩余 futures
#                                     └  exception → CmdResult(returncode=-1, ...)
#         """

#         def _on_result(cmd_str: str, r) -> None:
#             # if show_command:
#             #     log.info(f"{cmd_str}\n")
#             if show_output and r.stderr:
#                 log.output(f"{r.stderr}\n")

#         return self._executor.exec_commands(
#             commands,
#             parallel=parallel,
#             max_workers=max_workers,
#             stop_on_error=stop_on_error,
#             fail_fast=fail_fast,
#             on_result=_on_result,
#             mode=mode,
#         )
