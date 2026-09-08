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
command_builder — 命令接收器 + 依赖注入执行器

架构：
- CommandQueue:     命令接收器，默认打印命令，注入执行器后获得执行能力
- SequentialExecutor: 顺序执行器依赖
- ParallelExecutor:   并行执行器依赖
- CommandPrinter:     打印器依赖（增强打印）
- CommandBuilder:     传统批量构建器（兼容旧代码）
- inject:             通用依赖注入装饰器
"""

from __future__ import annotations

import queue
import threading

from nimmake.builders.Tracker import Tracker
from nimmake.executor import CmdExecutor, CmdExecutorCli, CmdResult
from nimmake.utils import Color, log

# =============================================================================
# CommandPrinter —— 打印器依赖
# =============================================================================


class CommandPrinter:
    """
    命令打印器 —— 只打印命令，不实际执行。

    可作为依赖注入到 CommandQueue，增强打印格式。

    使用示例::

        printer = CommandPrinter(prefix="[BUILD]", verbose=True)
        printer.add("gcc -c a.c -o a.o")
        printer.run()
    """

    def __init__(self, prefix: str = "[CMD]", verbose: bool = False):
        self._commands: list[str] = []
        self.prefix = prefix
        self.verbose = verbose

    def add(self, command: str) -> CommandPrinter:
        self._commands.append(command)
        # if self.verbose:
        #     print(f"+++{self.prefix}[{len(self._commands)}] {command}")
        # else:
        #     print(f"+++{self.prefix} {command}")
        # return self

    def add_batch(self, commands: list[str]) -> CommandPrinter:
        for cmd in commands:
            self.add(cmd)
        return self

    def run(self) -> CommandPrinter:
        """打印所有已记录的命令。"""
        if not self._commands:
            print(f"{self.prefix} (无命令)")
            return self
        for i, cmd in enumerate(self._commands):
            if self.verbose:
                print(f"***{self.prefix}[{i + 1}/{len(self._commands)}] {cmd}")
            else:
                print(f"***{self.prefix} {cmd}")
        return self

    def clear(self) -> CommandPrinter:
        self._commands.clear()
        return self

    @property
    def commands(self) -> list[str]:
        return list(self._commands)

    @property
    def count(self) -> int:
        return len(self._commands)


# =============================================================================
# SequentialExecutor —— 顺序执行器依赖
# =============================================================================


class SequentialExecutor:
    """
    顺序执行器 —— 逐条执行命令，前一条完成才执行下一条。

    注入到 CommandQueue 后，add() 的命令会按顺序逐一执行。

    使用示例::

        @inject(SequentialExecutor, verbose=True)
        class SeqQueue(CommandQueue):
            pass

        sq = SeqQueue()
        sq.start()
        sq.add("echo step1")
        sq.add("echo step2")
        sq.wait()
        sq.stop()
    """

    def __init__(
        self,
        executor: CmdExecutor | CmdExecutorCli | None = None,
        tracker: Tracker | None = None,
        quiet: bool = False,
        dry_run: bool = False,
        verbose: bool = False,
        silent: bool = False,
        toolpath: str | None = None,
        use_cli_executor: bool = False,
    ):
        if executor is not None:
            self._executor = executor
        elif use_cli_executor:
            self._executor = CmdExecutorCli()
        else:
            self._executor = CmdExecutor()
        self.tracker = tracker

        if toolpath:
            self._executor.add_path(toolpath, prepend=True)

        self.verbose = verbose
        self.silent = silent
        self.dry_run = dry_run
        self.quiet = quiet
        self._queue: queue.Queue = queue.Queue()
        self._results: list[CmdResult] = []
        self._running = False
        self._stop_event = threading.Event()
        self._worker: threading.Thread | None = None

    # ---- 生命周期 ----

    def start(self) -> SequentialExecutor:
        if self._running:
            return self
        self._running = True
        self._stop_event.clear()
        self._worker = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker.start()
        return self

    def wait(self) -> SequentialExecutor:
        self._queue.join()
        return self

    def stop(self) -> SequentialExecutor:
        if not self._running:
            return self
        self._running = False
        self._stop_event.set()
        self._queue.put(None)  # 唤醒 worker
        if self._worker:
            self._worker.join(timeout=5)
        return self

    # ---- 命令添加 ----

    def add(self, command: str | list[str], out: str = None, typ: str = None) -> SequentialExecutor:
        # log.debug(f"ParallelExecutor add: {self.tracker}")
        """
        command  str or dict
            dict {[out:"*.obj" , cmd: ["cmd", "objs" ] , typ:"OBJECTS" ,in:["src",hdr]}
        """
        cmd = {}
        if isinstance(command, str):
            cmd.update({"out": out})
            cmd.update({"cmd": [command]})
            cmd.update({"typ": "COMMANDS"})

        if isinstance(command, list):
            typ = "COMMANDS"
            if len(command) == 3:
                typ = command[2]
                cmd.update({"out": out})
                cmd.update({"typ": typ})
                cmd.update({"cmd": command})
        self._queue.put(cmd)

    def preprocess(self, command: dict) -> str:
        """预处理命令，添加环境变量"""
        ret = ""
        is_valid = True
        typ = command.get("typ", "")
        if typ is None:
            return command.get("cmd", "")
        if typ in ["COMMANDS"]:
            ret = command.get("cmd", "")[0]
        if typ in ["OBJECTS", "LIBS", "TARGETS", "STATIC", "SHARED"]:
            out = command.get("out", "")
            cmd_lst = command.get("cmd", "")
            typ = command.get("typ", "")
            if out and cmd_lst:
                ret, is_valid = self.tracker.Track(out, cmd_lst)
        return ret, is_valid

    # ---- 状态 ----

    @property
    def results(self) -> list[CmdResult]:
        return list(self._results)

    @property
    def is_running(self) -> bool:
        return self._running

    # ---- 内部 ----

    def _worker_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                cmd = self._queue.get(timeout=0.1)
            except queue.Empty:
                continue
            # log.warn(f"SequentialExecutor: {cmd}")

            if cmd is None:
                break
            new_cmd, is_valid = self.preprocess(cmd)
            # log.warn(f"SequentialExecutor add: {new_cmd} - -{is_valid}  {self.dry_run}")
            # log.debug(f"SequentialExecutor add: {new_cmd} - -{is_valid}")
            if self.dry_run:
                log.output(f"\n{new_cmd}")
                self._queue.task_done()
                continue

            if not is_valid:
                self._queue.task_done()
                continue

            try:
                r = self._executor.run(new_cmd, log_mode="off")
            except Exception as e:
                r = CmdResult(returncode=-1, stdout="", stderr=str(e), command=cmd)

            self._results.append(r)
            self._output_result(r, cmd.get("out", ""), cmd.get("typ", ""))
            self._queue.task_done()

    def _output_result(self, r: CmdResult, out: str = None, typ: str = None) -> None:
        if self.silent:
            return
        if self.verbose:
            log.output(r.command)
            if r.stdout:
                log.output(r.stdout)
            if r.stderr:
                log.output(r.stderr)
        else:
            # status = "OK" if r.success else f"FAIL(rc={r.returncode})"
            status = (
                f"{Color.GREEN}OK{Color.END}"
                if r.success
                else f"{Color.RED}FAIL(rc={r.returncode}){Color.END}"
            )
            if out:
                log.output(f"  [{status}] {out}")
                return
            cmd_lst = r.command.split()
            if typ in ["STATIC", "SHARED"]:
                log.output(f"  [{status}] {cmd_lst[2]}")
            elif typ in ["COMMANDS"]:
                log.output(f"  [{status}] {r.command}")
                log.output(f"{r.stdout}")
            else:
                log.output(f"  [{status}] {cmd_lst[-1] if r.command else ''}")

            if r.returncode != 0:
                log.output(f"{r.stderr}")

            # if "rcs" in cmd_lst:
            #     log.output(f"  [{status}] {cmd_lst[2]}")
            # else:
            #     log.output(f"  [{status}] {cmd_lst[-1] if r.command else ''}")


# =============================================================================
# ParallelExecutor —— 并行执行器依赖
# =============================================================================


class ParallelExecutor:
    """
    并行执行器 —— 多线程并行执行命令，add() 非阻塞立即返回。

    注入到 CommandQueue 后，add() 的命令会由后台线程池并行执行。

    使用示例::

        @inject(ParallelExecutor, max_workers=4, verbose=True)
        class ParQueue(CommandQueue):
            pass

        pq = ParQueue()
        pq.start()
        pq.add("gcc -c a.c -o a.o")
        pq.add("gcc -c b.c -o b.o")
        pq.wait()
        pq.stop()
    """

    _SENTINEL = object()

    def __init__(
        self,
        executor: CmdExecutor | CmdExecutorCli | None = None,
        tracker: Tracker | None = None,
        max_workers: int = 4,
        quiet: bool = False,
        verbose: bool = False,
        silent: bool = False,
        dry_run: bool = False,
        fail_fast: bool = False,
        toolpath: str | None = None,
        use_cli_executor: bool = False,
    ):
        if executor is not None:
            self._executor = executor
        elif use_cli_executor:
            self._executor = CmdExecutorCli()
        else:
            self._executor = CmdExecutor()
        self.tracker = tracker

        if toolpath:
            self._executor.add_path(toolpath, prepend=True)

        self.max_workers = max_workers
        self.verbose = verbose
        self.silent = silent
        self.dry_run = dry_run
        self.quiet = quiet
        self.fail_fast = fail_fast

        self._queue: queue.Queue = queue.Queue()
        self._results: list[CmdResult] = []
        self._results_lock = threading.Lock()
        self._workers: list[threading.Thread] = []
        self._running = False
        self._stop_event = threading.Event()

        log.info(f"ParallelExecutor: {self.max_workers} workers")
        log.info(
            f"ParallelExecutor: verbose {self.verbose} silent {self.silent} dry_run {self.dry_run}  "
        )

    # ---- 生命周期 ----

    def start(self) -> ParallelExecutor:
        if self._running:
            return self
        self._running = True
        self._stop_event.clear()

        for i in range(self.max_workers):
            t = threading.Thread(
                target=self._worker_loop,
                name=f"par-exec-{i}",
                daemon=True,
            )
            t.start()
            self._workers.append(t)

        log.info(f"ParallelExecutor: {self.max_workers} workers start")
        return self

    def wait(self) -> ParallelExecutor:
        self._queue.join()
        return self

    def stop(self) -> ParallelExecutor:
        if not self._running:
            return self
        self._running = False
        self._stop_event.set()

        for _ in self._workers:
            self._queue.put(self._SENTINEL)
        for t in self._workers:
            t.join(timeout=5)

        self._workers.clear()
        log.info("ParallelExecutor: stop")
        return self

    # ---- 命令添加 ----

    def add(self, command: str | list[str], out: str = None, typ: str = None) -> ParallelExecutor:
        # log.debug(f"ParallelExecutor add: {self.tracker}")
        """
        command  str or dict
            dict {[out:"*.obj" , cmd: ["cmd", "objs" ] , typ:"OBJECTS" ,in:["src",hdr]}
        """
        cmd = {}
        if isinstance(command, str):
            cmd.update({"out": out})
            cmd.update({"cmd": [command]})
            cmd.update({"typ": "COMMANDS"})

        if isinstance(command, list):
            typ = "COMMANDS"
            if len(command) == 3:
                typ = command[2]
                cmd.update({"out": out})
                cmd.update({"typ": typ})
                cmd.update({"cmd": command})
        self._queue.put(cmd)

    def preprocess(self, command: dict) -> str:
        """预处理命令，添加环境变量"""
        ret = ""
        is_valid = True
        typ = command.get("typ", "")
        if typ is None:
            return command.get("cmd", "")
        if typ in ["COMMANDS"]:
            ret = command.get("cmd", "")[0]
        if typ in ["OBJECTS", "LIBS", "TARGETS", "STATIC", "SHARED"]:
            out = command.get("out", "")
            cmd_lst = command.get("cmd", "")
            typ = command.get("typ", "")
            if out and cmd_lst:
                ret, is_valid = self.tracker.Track(out, cmd_lst)
        return ret, is_valid

    # def cmd_process(self, command: dict) -> str:
    #     """预处理命令，添加环境变量"""
    #     ret = ""
    #     typ = command.get("typ", "")
    #     if typ is None:
    #         return command.get("cmd", "")
    #     if typ in ["COMMANDS"]:
    #         ret = command.get("cmd", "")[0]
    #     if typ in ["OBJECTS", "LIBS", "TARGETS", "STATIC", "SHARED"]:
    #         out = command.get("out", "")
    #         cmd_lst = command.get("cmd", "")
    #         typ = command.get("typ", "")
    #         if out and cmd_lst:
    #             ret = self.tracker.Track(out, cmd_lst)
    #     return ret

    # ---- 状态 ----

    @property
    def results(self) -> list[CmdResult]:
        with self._results_lock:
            return list(self._results)

    @property
    def is_running(self) -> bool:
        return self._running

    # ---- 内部 ----

    def _worker_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                cmd = self._queue.get(timeout=0.1)
            except queue.Empty:
                continue
            if cmd is self._SENTINEL:
                break

            new_cmd, is_valid = self.preprocess(cmd)
            # log.warn(f"ParallelExecutor add: {new_cmd} - -{is_valid} ++ {self.dry_run}")

            if self.dry_run:
                log.output(f"\n{new_cmd}")
                self._queue.task_done()
                continue

            if not is_valid:
                self._queue.task_done()
                continue

            # if self.dry_run:
            #     log.output(f"{new_cmd}")
            #     self._queue.task_done()
            #     continue

            try:
                r = self._executor.run(new_cmd, log_mode="off")
            except Exception as e:
                r = CmdResult(returncode=-1, stdout="", stderr=str(e), command=cmd)

            with self._results_lock:
                self._results.append(r)

            self._output_result(r, cmd.get("out", ""), cmd.get("typ", ""))
            self._queue.task_done()

            if self.fail_fast and not r.success:
                log.error(f"ParallelExecutor fail_fast: {cmd}")
                self._stop_event.set()

    def _output_result(self, r: CmdResult, out: str = None, typ: str = None) -> None:
        if self.silent:
            return
        if self.verbose:
            log.output(r.command)
            if r.stdout:
                log.output(r.stdout)
            if r.stderr:
                log.output(r.stderr)
        else:
            # status = "OK" if r.success else f"FAIL(rc={r.returncode})"
            status = (
                f"{Color.GREEN}OK{Color.END}"
                if r.success
                else f"{Color.RED}FAIL(rc={r.returncode}){Color.END}"
            )
            if out:
                log.output(f"  [{status}] {out}")
                return
            cmd_lst = r.command.split()

            if typ in ["STATIC", "SHARED"]:
                log.output(f"  [{status}] {cmd_lst[2]}")
            elif typ in ["COMMANDS"]:
                log.output(f"  [{status}] {r.command}")
            if r.returncode != 0:
                log.output(f"{r.stderr}")
            # log.output(f"  [{status}] {cmd_lst[-1] if r.command else ''}")
            # if "rcs" in cmd_lst:
            #     log.output(f"  [{status}] {cmd_lst[2]}")
            # else:
            #     log.output(f"  [{status}] {cmd_lst[-1] if r.command else ''}")


# =============================================================================
# CommandQueue —— 命令接收器（默认打印，注入执行器后获得执行能力）
# =============================================================================


class CommandQueue:
    """
    命令接收器 —— 默认打印命令，注入执行器后支持实际执行。

    核心机制：
    - 默认行为：add() 打印命令，不执行
    - 注入 SequentialExecutor：add() 顺序执行
    - 注入 ParallelExecutor：add() 并行执行
    - 注入 CommandPrinter：增强打印格式
    - 支持同时注入多个依赖

    使用示例::

        # 1) 默认：只打印
        cq = CommandQueue()
        cq.add("echo hello")   # 输出: [CMD] echo hello

        # 2) 注入并行执行器
        @inject(ParallelExecutor, max_workers=4, verbose=True)
        class BuildQueue(CommandQueue):
            pass

        bq = BuildQueue()
        bq.start()
        bq.add("gcc -c a.c -o a.o")   # 打印 + 并行执行
        bq.add("gcc -c b.c -o b.o")
        bq.wait()
        bq.stop()
    """

    def __init__(
        self,
        prefix: str = "[CMD]",
        verbose: bool = True,
        **kwargs,
    ):
        """
        Args:
            prefix: 打印前缀
            verbose: 是否显示序号
        """
        self._commands: list[str] = []
        self.prefix = prefix
        self.verbose = verbose

    # ------------------------------------------------------------------
    # 命令添加（默认打印）
    # ------------------------------------------------------------------

    def add(self, command: str | list[str], out: str = None) -> CommandQueue:
        """
        添加命令（默认打印到控制台）。
        如果注入了执行器，还会委托给执行器。

        Args:
            command: 命令字符串

        Returns:
            self，支持链式调用
        """
        self._commands.append(command)
        # if self.verbose:
        #     print(f"---{self.prefix}[{len(self._commands)}] {command}")
        # else:
        #     print(f"---{self.prefix} {command}")
        return self

    def add_batch(self, commands: list[str]) -> CommandQueue:
        for cmd in commands:
            self.add(cmd)
        return self

    # ------------------------------------------------------------------
    # 生命周期（默认空操作，注入执行器后委托）
    # ------------------------------------------------------------------

    def start(self) -> CommandQueue:
        """启动（默认空操作，注入执行器后委托给执行器）。"""
        return self

    def wait(self) -> CommandQueue:
        """等待（默认空操作，注入执行器后委托给执行器）。"""
        return self

    def stop(self) -> CommandQueue:
        """停止（默认空操作，注入执行器后委托给执行器）。"""
        return self

    # ------------------------------------------------------------------
    # 状态查询
    # ------------------------------------------------------------------

    def clear(self) -> CommandQueue:
        self._commands.clear()
        return self

    @property
    def commands(self) -> list[str]:
        return list(self._commands)

    @property
    def count(self) -> int:
        return len(self._commands)


# =============================================================================
# inject —— 通用依赖注入装饰器
# =============================================================================

_LIFECYCLE_METHODS = ("start", "wait", "stop")


def inject(dependency_cls, attr_name: str = None, **dep_kwargs):
    """
    类装饰器：将依赖类实例注入到 CommandQueue 子类中。

    注入后：
    - __init__ 中自动创建依赖实例
    - add() 自动委托给依赖的 add()（如果存在）
    - start() / wait() / stop() 自动委托给依赖（如果存在）

    Args:
        dependency_cls: 依赖类（SequentialExecutor / ParallelExecutor / CommandPrinter 等）
        attr_name: 注入后的属性名，默认取类名小写加下划线前缀
        **dep_kwargs: 传递给依赖类构造函数的参数

    使用示例::

        # 注入并行执行器
        @inject(ParallelExecutor, max_workers=4, verbose=True)
        class BuildQueue(CommandQueue):
            pass

        bq = BuildQueue()
        bq.start()
        bq.add("gcc -c a.c -o a.o")   # 打印 + 并行执行
        bq.wait()
        bq.stop()
        print(bq._parallelexecutor.results)  # 访问注入的依赖

        # 同时注入多个依赖
        @inject(CommandPrinter, prefix="[BUILD]", verbose=True)
        @inject(SequentialExecutor, verbose=True)
        class DebugQueue(CommandQueue):
            pass
    """

    if attr_name is None:
        attr_name = f"_{dependency_cls.__name__.lower()}"

    def decorator(cls):
        _original_init = cls.__init__
        _dep_prefix = attr_name + "__"

        # ---- hook __init__ ----
        def _new_init(self, *args, **kwargs):
            # 从 kwargs 中提取以此依赖为前缀的参数
            runtime_dep_kwargs = {}
            for k in list(kwargs.keys()):
                if k.startswith(_dep_prefix):
                    runtime_dep_kwargs[k[len(_dep_prefix) :]] = kwargs.pop(k)

            _original_init(self, *args, **kwargs)

            # 合并：装饰时默认值 < 实例化时覆盖值
            merged = {**dep_kwargs, **runtime_dep_kwargs}
            dep_instance = dependency_cls(**merged)
            setattr(self, attr_name, dep_instance)

        cls.__init__ = _new_init

        # ---- hook add() ----
        if hasattr(dependency_cls, "add"):
            _original_add = cls.add

            def _new_add(self, command: str, *args, **kwargs):
                dep = getattr(self, attr_name, None)
                if dep is not None:
                    dep.add(command, *args, **kwargs)
                return _original_add(self, command, *args, **kwargs)

            cls.add = _new_add

        # ---- hook 生命周期方法 ----
        for method_name in _LIFECYCLE_METHODS:
            if hasattr(dependency_cls, method_name):
                _original_method = getattr(cls, method_name)

                def _make_lifecycle_hook(_name, _orig):
                    def _hook(self, *args, **kwargs):
                        dep = getattr(self, attr_name, None)
                        if dep is not None:
                            getattr(dep, _name)(*args, **kwargs)
                        return _orig(self, *args, **kwargs)

                    return _hook

                setattr(cls, method_name, _make_lifecycle_hook(method_name, _original_method))

        return cls

    return decorator


# =============================================================================
# 预定义子类
# =============================================================================


@inject(ParallelExecutor, max_workers=4, verbose=True)
class ParallelQueue(CommandQueue):
    """预定义：带并行执行器的 CommandQueue。"""

    pass


@inject(SequentialExecutor, verbose=True)
class SequentialQueue(CommandQueue):
    """预定义：带顺序执行器的 CommandQueue。"""

    pass


@inject(CommandPrinter, prefix="[QUEUE]", verbose=True)
class PrinterQueue(CommandQueue):
    """预定义：带增强打印器的 CommandQueue。"""

    pass


if __name__ == "__main__":
    # ============================================================
    # 示例 1: CommandQueue 默认 —— 只打印，不执行
    # ============================================================
    print("\n===== 1. 默认：只打印 =====")
    cq = CommandQueue()
    cq.add("echo 任务A")
    cq.add("echo 任务B")
    print(f"已记录 {cq.count} 条命令")

    # ============================================================
    # 示例 2: 注入 ParallelExecutor —— 打印 + 并行执行
    # ============================================================
    print("\n===== 2. 注入并行执行器 =====")
    pq = ParallelQueue()
    pq.start()
    pq.add("echo 编译 a.c ...")
    pq.add("echo 编译 b.c ...")
    pq.add("echo 编译 c.c ...")
    pq.wait()
    pq.add("echo 编译 d.c ...")
    pq.wait()
    print(f"完成 {len(pq._parallelexecutor.results)} 条")
    pq.stop()

    # ============================================================
    # 示例 3: 注入 SequentialExecutor —— 打印 + 顺序执行
    # ============================================================
    print("\n===== 3. 注入顺序执行器 =====")
    sq = SequentialQueue()
    sq.start()
    sq.add("echo 步骤1")
    sq.add("echo 步骤2")
    sq.add("echo 步骤3")
    sq.wait()
    sq.stop()

    # ============================================================
    # 示例 4: 同时注入多个依赖
    # ============================================================
    print("\n===== 4. 多依赖注入 =====")

    @inject(CommandPrinter, prefix="[BUILD]", verbose=True)
    @inject(SequentialExecutor, verbose=True)
    class DebugQueue(CommandQueue):
        pass

    dq = DebugQueue()
    dq.start()
    dq.add("echo hello")
    dq.add("echo world")
    dq.wait()
    dq._commandprinter.run()  # 打印所有历史记录
    dq.stop()
