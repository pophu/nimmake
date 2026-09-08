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
subprocess-based system command executor.

Provides three core capabilities:
1. Execute system commands (supports str or list form)
2. Pass custom environment variables, with support for quickly appending PATH directories
3. Capture stdout/stderr output
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from collections.abc import Iterator, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

_PATH_SEP = ";" if sys.platform == "win32" else ":"

# ---------------------------------------------------------------------------
# cmd return datatype
# ---------------------------------------------------------------------------


@dataclass
class CmdResult:
    """命令执行结果"""

    returncode: int
    stdout: str
    stderr: str
    command: str
    timed_out: bool = False

    @property
    def success(self) -> bool:
        """返回码为 0 且未超时"""
        return self.returncode == 0 and not self.timed_out


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


def _detect_encoding() -> str:
    """自动检测当前系统编码"""
    if sys.platform == "win32":
        return "utf-8" if sys.getfilesystemencoding() == "utf-8" else "gbk"
    return "utf-8"


def _decode(data: bytes, encoding: str) -> str:
    """安全解码字节，多编码 fallback"""
    for enc in (encoding, "utf-8", "gbk", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode(encoding, errors="replace")


_WIN_BUILTINS = {
    "echo",
    "dir",
    "cd",
    "md",
    "rd",
    "rmdir",
    "del",
    "erase",
    "copy",
    "move",
    "ren",
    "rename",
    "type",
    "cls",
    "date",
    "time",
    "ver",
    "set",
    "path",
    "prompt",
    "title",
    "color",
    "pushd",
    "popd",
    "vol",
    "label",
    "assoc",
    "ftype",
}


def _is_builtin_cmd(command: str) -> bool:
    """判断是否是 Windows 内置命令（需要 shell）"""
    if sys.platform != "win32":
        return False
    cmd = command.strip().split(maxsplit=1)[0].lower()
    return cmd in _WIN_BUILTINS


def _resolve_shell(command: str | Sequence[str], shell: bool | None) -> bool:
    """决定是否使用 shell"""
    if shell is not None:
        return shell
    if isinstance(command, str):
        return True
    return _is_builtin_cmd(command[0])


def _format_command(command: str | Sequence[str]) -> str:
    """将命令转为可读字符串"""
    return command if isinstance(command, str) else subprocess.list2cmdline(command)


def _print_parallel_result(idx: int, label: str, r: CmdResult) -> None:
    """打印单条并行结果（stderr），分隔清晰"""
    print(f"[{idx}] {label}  (rc={r.returncode})", file=sys.stderr, flush=True)
    if r.stdout:
        print(r.stdout, end="", file=sys.stderr, flush=True)
    if r.stderr:
        print(r.stderr, end="", file=sys.stderr, flush=True)


# ---------------------------------------------------------------------------
# 构建环境变量
# ---------------------------------------------------------------------------


def build_env(*, inherit: bool = True, **kwargs: str) -> dict[str, str]:
    """
    构建子进程环境变量字典。
    get sys.environ, and add kwargs. Get new env
    not add PATH
    """
    env: dict[str, str] = dict(os.environ) if inherit else {}
    env.update(kwargs)
    return env


# ---------------------------------------------------------------------------
# 核心类
# ---------------------------------------------------------------------------


class CmdExecutor:
    """
    系统命令执行器。

    将公共配置固化在实例中，避免每次调用重复传参。

    Args:
        env: 环境变量字典（通过 ``build_env()`` 构建）
        cwd: 子进程工作目录
        timeout: 默认超时秒数
        shell: 是否通过 shell 执行。None 表示自动判断
        encoding: 输出解码编码。None 表示自动检测
        check: 默认是否在失败时抛出 ``RuntimeError``
        log_mode: 日志输出模式

    example : just enviroment variable,  not change path
        def demo_env_RISCV():

            env = build_env(APP_HOME="C:/myapp", DEBUG="1")
            # print(env)
            exe = CmdExecutor(env=env)

            r = exe("echo APP_HOME=%APP_HOME%, DEBUG=%DEBUG%")
            print(f"env vars   {r.stdout.strip()}")

            # per-call 临时覆盖
            r2 = exe("echo %APP_HOME%", env=build_env(APP_HOME="C:/override"))
            print(f"overridden {r2.stdout.strip()}")

            # 实例环境未变
            r3 = exe("echo %APP_HOME%")
            print(f"restored   {r3.stdout.strip()}")

    """

    LOG_OFF = "off"
    LOG_CMD = "command"
    LOG_OUTPUT = "output"
    LOG_ALL = "all"

    def __init__(
        self,
        *,
        env: Mapping[str, str] | None = None,
        cwd: str | None = None,
        timeout: float | None = None,
        shell: bool | None = None,
        encoding: str | None = None,
        check: bool = False,
        log_mode: str = "off",
    ):
        self.env = dict(env) if env is not None else None
        self.cwd = cwd
        self.timeout = timeout
        self.shell = shell
        self.encoding = encoding or _detect_encoding()
        self.check = check
        self.log_mode = log_mode

    def set_log_mode(self, mode: str) -> CmdExecutor:
        """设置日志输出模式，返回 self 以便链式调用。"""
        self.log_mode = mode
        return self

    # ------------------------------------------------------------------
    # PATH 管理
    # ------------------------------------------------------------------

    def _ensure_env(self) -> None:
        """确保 self.env 已初始化"""
        if self.env is None:
            self.env = dict(os.environ)

    def _split_path(self) -> list[str]:
        """返回当前 PATH 的列表"""
        current = self.env.get("PATH", "") if self.env else ""
        return current.split(_PATH_SEP) if current else []

    def add_path(self, *paths: str, prepend: bool = False) -> None:
        """
        向子进程的 PATH 环境变量中添加目录。

        Args:
            *paths: 要添加的目录路径
            prepend: True 插入到 PATH 最前，False（默认）追加到末尾
        """
        if not paths:
            return
        self._ensure_env()
        parts = self._split_path()
        for p in paths:
            if not p:
                continue
            if str(p) not in parts:
                parts.insert(0, str(p)) if prepend else parts.append(str(p))

        self.env["PATH"] = _PATH_SEP.join(parts)

    def remove_path(self, *substrings: str) -> None:
        """
        从子进程的 PATH 中移除包含指定子串的目录。

        Args:
            *substrings: 要移除的目录路径或关键词（子串匹配）
        """
        if not substrings or self.env is None:
            return
        parts = self._split_path()
        if not parts:
            return

        kept = [p for p in parts if not any(s in p for s in substrings)]
        if len(kept) != len(parts):
            self.env["PATH"] = _PATH_SEP.join(kept)

    def is_command_valid(self, command: str | Sequence[str]) -> str | None:
        """
        检查命令是否可执行（是否在 PATH 中能找到）。

        Args:
            command: 命令名称或命令列表（取首个元素）

        Returns:
            命令的完整路径，若未找到则返回 None
        """
        if isinstance(command, str):
            name = command.strip().split(maxsplit=1)[0]
        else:
            name = command[0] if command else ""

        if not name:
            return None

        exe_path = self.env.get("PATH") if self.env is not None and "PATH" in self.env else None
        return shutil.which(name, path=exe_path)

    # ------------------------------------------------------------------
    # 核心执行
    # ------------------------------------------------------------------

    def _merge_env(self, per_call_env: Mapping[str, str] | None) -> dict[str, str] | None:
        """合并实例 env 与 per-call env"""
        if self.env is None and per_call_env is None:
            return None
        merged = dict(self.env) if self.env is not None else {}
        if per_call_env is not None:
            merged.update(per_call_env)
        return merged

    def _log_cmd(self, cmd_str: str, mode: str) -> None:
        """按日志模式输出命令原文"""
        if mode in (self.LOG_CMD, self.LOG_ALL):
            print(f"> {cmd_str}", file=sys.stderr, flush=True)

    def _log_output(self, stdout: str, stderr: str, mode: str) -> None:
        """按日志模式输出执行结果"""
        if mode in (self.LOG_OUTPUT, self.LOG_ALL):
            if stdout:
                print(stdout, end="", file=sys.stderr, flush=True)
            if stderr:
                print(stderr, end="", file=sys.stderr, flush=True)

    # def _run_popen(
    #     self,
    #     command: str | Sequence[str],
    #     use_shell: bool,
    #     merged_env: dict[str, str] | None,
    #     effective_cwd: str | None,
    # ) -> subprocess.Popen:
    #     """启动子进程"""
    #     return subprocess.Popen(
    #         command,
    #         stdin=subprocess.DEVNULL,
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.PIPE,
    #         shell=use_shell,
    #         env=merged_env,
    #         cwd=effective_cwd,
    #     )

    def _run_popen(
        self,
        command: str | Sequence[str],
        use_shell: bool,
        merged_env: dict[str, str] | None,
        effective_cwd: str | None,
    ) -> subprocess.Popen:
        """启动子进程"""
        # Windows: 当 shell 模式下的命令字符串超过 cmd.exe 限制 (~8191) 时，
        # 自动拆分为列表并关闭 shell，利用 CreateProcess 更高的限制 (~32767)
        if sys.platform == "win32" and use_shell and isinstance(command, str):
            if len(command) > 8000:
                import shlex

                try:
                    command = shlex.split(command, posix=False)
                    use_shell = False
                except Exception:
                    pass

        return subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=use_shell,
            env=merged_env,
            cwd=effective_cwd,
        )

    def _read_stream(
        self,
        proc: subprocess.Popen,
        timeout_val: float | None,
        line_callback,
    ) -> tuple[str, str, int, bool]:
        """
        从已启动的 Popen 中逐行读取 stdout/stderr 并回调。

        Args:
            proc: 已启动的 Popen 对象（须 text=True 模式启动）
            timeout_val: 超时秒数
            line_callback: 接收 (line: str) 的可调用对象，每行回调一次

        Returns:
            (stdout, stderr, returncode, timed_out)
        """
        import threading

        stdout_lines: list[str] = []
        stderr_lines: list[str] = []
        lock = threading.Lock()

        def _reader(pipe, storage):
            for raw in iter(pipe.readline, ""):
                # 同时支持bytes和str类型
                if isinstance(raw, bytes):
                    line = _decode(raw.rstrip(b"\r\n"), self.encoding)
                else:
                    line = raw.rstrip("\r\n")

                with lock:
                    storage.append(line)

                # env exchange build data, not output
                if line_callback:
                    if pipe == proc.stdout:
                        line_callback(line, 0)
                    if pipe == proc.stderr:
                        line_callback(line, 1)
            pipe.close()

        t_out = threading.Thread(target=_reader, args=(proc.stdout, stdout_lines), daemon=True)
        t_err = threading.Thread(target=_reader, args=(proc.stderr, stderr_lines), daemon=True)
        t_out.start()
        t_err.start()

        try:
            proc.wait(timeout=timeout_val)
            timed_out = False
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            timed_out = True

        t_out.join()
        t_err.join()

        stdout = "\n".join(stdout_lines)
        stderr = "\n".join(stderr_lines)
        rc = proc.returncode if not timed_out else -1

        return stdout, stderr, rc, timed_out

    def _run_popen_stream(
        self,
        command: str | Sequence[str],
        use_shell: bool,
        merged_env: dict[str, str] | None,
        effective_cwd: str | None,
    ) -> subprocess.Popen:
        """启动子进程（text 模式，供流式读取用，增强编码处理）"""
        # 复制环境变量并设置PYTHONIOENCODING
        stream_env = dict(merged_env) if merged_env else dict(os.environ)
        stream_env["PYTHONIOENCODING"] = self.encoding + ":replace"

        # Windows: 当 shell 模式下的命令字符串超过 cmd.exe 限制 (~8191) 时，
        # 自动拆分为列表并关闭 shell，利用 CreateProcess 更高的限制 (~32767)
        if sys.platform == "win32" and use_shell and isinstance(command, str):
            if len(command) > 8000:
                import shlex

                try:
                    command = shlex.split(command, posix=False)
                    use_shell = False
                except Exception:
                    pass

        return subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=use_shell,
            env=stream_env,  # 使用增强后的环境变量
            cwd=effective_cwd,
            text=True,
            encoding=self.encoding,
            errors="replace",
            bufsize=1,
        )

    def run(
        self,
        command: str | Sequence[str],
        *,
        env: Mapping[str, str] | None = None,
        cwd: str | None = None,
        timeout: float | None = None,
        shell: bool | None = None,
        check: bool | None = None,
        log_mode: str | None = None,
        line_callback: Optional = None,
    ) -> CmdResult:
        """
        执行一条命令。

        Args:
            command: 命令字符串或列表
            env: 临时覆盖的环境变量（优先级高于实例配置）
            cwd: 临时覆盖的工作目录
            timeout: 临时覆盖的超时时间
            shell: 临时覆盖的 shell 策略
            check: 临时覆盖的 check 模式。None 表示使用实例默认值
            log_mode: 临时覆盖的日志模式。None 表示使用实例默认值
            line_callback: 可选。设置后以流式模式运行，
                每读到一行 stdout/stderr 立即调用 callback(line)。
                返回的 CmdResult 仍包含完整 stdout/stderr。

        Returns:
            CmdResult

        Raises:
            RuntimeError: 当 ``check=True`` 且命令失败时
            FileNotFoundError: 命令不存在时
        """
        cmd_str = _format_command(command)
        use_shell = _resolve_shell(command, shell if shell is not None else self.shell)
        merged_env = self._merge_env(env)
        effective_cwd = cwd if cwd is not None else self.cwd
        effective_check = check if check is not None else self.check
        effective_log_mode = log_mode if log_mode is not None else self.log_mode

        self._log_cmd(cmd_str, effective_log_mode)

        timeout_val = timeout if timeout is not None else self.timeout

        if line_callback is not None:
            # ── 流式模式 — text=True Popen + 逐行回调 ──
            try:
                proc = self._run_popen_stream(
                    command,
                    use_shell,
                    merged_env,
                    effective_cwd,
                )
            except FileNotFoundError:
                raise
            except OSError as e:
                return CmdResult(returncode=1, stdout="", stderr=str(e), command=cmd_str)
            stdout, stderr, rc, timed_out = self._read_stream(
                proc,
                timeout_val,
                line_callback,
            )
        else:
            # ── 标准模式（communicate） ──
            try:
                proc = self._run_popen(command, use_shell, merged_env, effective_cwd)
            except FileNotFoundError:
                raise
            except OSError as e:
                return CmdResult(returncode=1, stdout="", stderr=str(e), command=cmd_str)

            try:
                stdout_bytes, stderr_bytes = proc.communicate(timeout=timeout_val)
                timed_out = False
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout_bytes, stderr_bytes = proc.communicate()
                timed_out = True
            stdout = _decode(stdout_bytes, self.encoding)
            stderr = _decode(stderr_bytes, self.encoding)
            rc = proc.returncode if not timed_out else -1

        result = CmdResult(
            returncode=rc,
            stdout=stdout,
            stderr=stderr,
            command=cmd_str,
            timed_out=timed_out,
        )

        self._log_output(stdout, stderr, effective_log_mode)

        if effective_check and not result.success:
            reason = "timed out" if timed_out else f"returned non-zero exit code {rc}"
            raise RuntimeError(f"Command {cmd_str!r} {reason}")

        return result

    # ------------------------------------------------------------------
    # 批量执行
    # ------------------------------------------------------------------

    def run_batch(
        self,
        commands: Sequence[str | Sequence[str]],
        *,
        stop_on_error: bool = False,
        env: Mapping[str, str] | None = None,
        cwd: str | None = None,
        timeout: float | None = None,
        shell: bool | None = None,
        check: bool | None = None,
        log_mode: str | None = None,
    ) -> list[CmdResult]:
        """
        批量顺序执行多条命令。

        Args:
            commands: 命令列表
            stop_on_error: 遇到失败时是否停止后续执行
            其余参数同 ``run()``

        Returns:
            ``[CmdResult, ...]`` 列表，顺序与输入一致
        """
        results: list[CmdResult] = []
        for cmd in commands:
            result = self.run(cmd, env=env, cwd=cwd, timeout=timeout, shell=shell, check=check)
            results.append(result)
            if stop_on_error and not result.success:
                break
        return results

    # ------------------------------------------------------------------
    # 并行执行
    # ------------------------------------------------------------------
    def run_parallel(
        self,
        commands: Sequence[str | Sequence[str]],
        *,
        max_workers: int | None = None,
        stop_on_error: bool = False,
        env: Mapping[str, str] | None = None,
        cwd: str | None = None,
        timeout: float | None = None,
        shell: bool | None = None,
        check: bool | None = None,
        log_mode: str | None = None,
    ) -> list[CmdResult]:
        """
        并行执行多条命令，完成后按序分组输出结果，避免输出交错。

        Args:
            commands: 命令列表
            max_workers: 最大并行数，默认 CPU 核心数
            stop_on_error: 遇到失败时取消剩余任务（已启动的可能无法中止）
            其余参数同 ``run()``

        Returns:
            ``[CmdResult, ...]`` 列表，顺序与输入一致
        """
        effective_log_mode = log_mode if log_mode is not None else self.log_mode
        need_cmd_str = effective_log_mode in (self.LOG_CMD, self.LOG_ALL)

        def _worker(cmd: str | Sequence[str]) -> CmdResult:
            return self.run(
                cmd,
                env=env,
                cwd=cwd,
                timeout=timeout,
                shell=shell,
                check=check,
                log_mode="off",
            )

        n = len(commands)
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(_worker, cmd): i for i, cmd in enumerate(commands)}
            results: list[CmdResult | None] = [None] * n
            for future in as_completed(futures):
                i = futures[future]
                results[i] = future.result()
                if stop_on_error and not results[i].success:
                    for f in futures:
                        f.cancel()
                    break

        if effective_log_mode in (self.LOG_OUTPUT, self.LOG_ALL):
            for i, r in enumerate(results):
                label = _format_command(commands[i]) if need_cmd_str else f"cmd[{i}]"
                _print_parallel_result(i, label, r)

        return results  # type: ignore[return-value]

    # def run_parallel2(
    #     self,
    #     commands: Sequence[str | Sequence[str]],
    #     *,
    #     max_workers: int | None = None,
    #     env: Mapping[str, str] | None = None,
    #     cwd: str | None = None,
    #     timeout: float | None = None,
    #     shell: bool | None = None,
    #     check: bool | None = None,
    #     log_mode: str | None = None,
    # ) -> list[CmdResult]:
    #     """
    #     并行执行多条命令，完成后按序分组输出结果，避免输出交错。

    #     Args:
    #         commands: 命令列表
    #         max_workers: 最大并行数，默认 CPU 核心数
    #         其余参数同 ``run()``

    #     Returns:
    #         ``[CmdResult, ...]`` 列表，顺序与输入一致
    #     """
    #     effective_log_mode = log_mode if log_mode is not None else self.log_mode
    #     need_cmd_str = effective_log_mode in (self.LOG_CMD, self.LOG_ALL)

    #     def _worker(cmd: str | Sequence[str]) -> CmdResult:
    #         return self.run(
    #             cmd,
    #             env=env,
    #             cwd=cwd,
    #             timeout=timeout,
    #             shell=shell,
    #             check=check,
    #             log_mode="off",
    #         )

    #     n = len(commands)
    #     with ThreadPoolExecutor(max_workers=max_workers) as pool:
    #         futures = {pool.submit(_worker, cmd): i for i, cmd in enumerate(commands)}
    #         results: list[CmdResult | None] = [None] * n
    #         for future in as_completed(futures):
    #             i = futures[future]
    #             results[i] = future.result()

    #     if effective_log_mode in (self.LOG_OUTPUT, self.LOG_ALL):
    #         for i, r in enumerate(results):
    #             label = _format_command(commands[i]) if need_cmd_str else f"cmd[{i}]"
    #             _print_parallel_result(i, label, r)

    #     return results  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # 上下文管理器
    # ------------------------------------------------------------------

    @contextmanager
    def with_env(self, **kwargs: str) -> Iterator[CmdExecutor]:
        """
        临时增加环境变量的上下文管理器，退出后自动恢复。

        用法:
            with exe.with_env(TMP_DIR="/tmp/work"):
                exe("echo %TMP_DIR%")
        """
        old = self.env
        merged = dict(old) if old is not None else {}
        merged.update(kwargs)
        self.env = merged
        try:
            yield self
        finally:
            self.env = old

    @contextmanager
    def with_PATH(
        self,
        *paths: str,
        prepend: bool = False,
    ) -> Iterator[CmdExecutor]:
        """
        临时追加 PATH 目录的上下文管理器，退出后 PATH 自动恢复。

        Args:
            *paths: 要临时添加的目录路径
            prepend: True 插入到 PATH 最前，False（默认）追加到末尾
        """
        old_env = dict(self.env) if self.env is not None else None
        old_path = (self.env or {}).get("PATH", "")
        self.add_path(*paths, prepend=prepend)
        try:
            yield self
        finally:
            if old_env is None:
                self.env = None
            else:
                self.env = old_env
                self.env["PATH"] = old_path

    @contextmanager
    def with_options(
        self,
        *,
        cwd: str | None = None,
        timeout: float | None = None,
        shell: bool | None = None,
        check: bool | None = None,
        log_mode: str | None = None,
    ) -> Iterator[CmdExecutor]:
        """
        临时覆盖多个选项的上下文管理器，退出后自动恢复。

        用法:
            with exe.with_options(cwd="/tmp", timeout=5.0):
                exe("make")
            with exe.with_options(log_mode="all"):
                exe("echo visible")
        """
        old = self.cwd, self.timeout, self.shell, self.check, self.log_mode
        if cwd is not None:
            self.cwd = cwd
        if timeout is not None:
            self.timeout = timeout
        if shell is not None:
            self.shell = shell
        if check is not None:
            self.check = check
        if log_mode is not None:
            self.log_mode = log_mode
        try:
            yield self
        finally:
            self.cwd, self.timeout, self.shell, self.check, self.log_mode = old

    def run_python_script(
        self,
        script_path: str,
        *,
        script_args: Sequence[str] | None = None,
        cwd: str | None = None,
        timeout: float | None = None,
        env: Mapping[str, str] | None = None,
        check: bool | None = None,
        line_callback: Optional = None,
    ) -> CmdResult:
        """
        执行 Python 脚本（使用 python -u 模式），支持实时捕获输出。

        使用 ``python -u`` （无缓冲模式）运行脚本，确保输出实时可见。
        通过 ``line_callback`` 可逐行接收 stdout/stderr 输出。

        Args:
            script_path: Python 脚本文件路径（.py 文件）
            script_args: 传递给脚本的命令行参数列表
            cwd: 脚本的工作目录（默认为脚本所在目录或实例配置）
            timeout: 超时秒数
            env: 环境变量（优先级高于实例配置）
            check: 失败时是否抛出异常。None 表示使用实例默认值
            line_callback: 可选的行回调函数，签名为 ``callback(line: str)``，
                每读到一行 stdout/stderr 时调用。设置后启用流式模式。

        Returns:
            CmdResult: 包含 returncode、stdout、stderr 等信息

        Raises:
            RuntimeError: 当 ``check=True`` 且脚本执行失败时
            FileNotFoundError: 脚本文件不存在时

        Example:
            >>> executor = CmdExecutor()
            >>> def on_output(line):
            ...     print(f"实时输出: {line}")
            >>> result = executor.run_python_script(
            ...     "myscript.py",
            ...     script_args=["--input", "data.txt"],
            ...     line_callback=on_output,
            ... )
            >>> if result.success:
            ...     print("脚本执行成功")
        """
        import os.path

        if not os.path.isfile(script_path):
            raise FileNotFoundError(f"Python script not found: {script_path}")

        # cmd: list[str] = [sys.executable, "-u", script_path]
        cmd: list[str] = [sys.executable, script_path]
        if script_args:
            cmd.extend(str(arg) for arg in script_args)
        # log.info(f"cmd: {cmd}")
        effective_cwd = None

        # 需要将 env里面的输出提取出来 或取最后一个输出
        return self.run(
            cmd,
            env=env,
            cwd=effective_cwd,
            timeout=timeout,
            shell=False,
            check=check,
            line_callback=line_callback,
        )

    def exec_commands(
        self,
        commands: str | Sequence[str],
        *,
        parallel: bool = False,
        max_workers: int | None = 2,
        stop_on_error: bool = False,
        fail_fast: bool = False,
        verbose: bool = False,  # verbose
        is_compile: bool = True,
    ) -> list[CmdResult]:
        """
        执行一条或多条命令，支持顺序/并行。
        并行模式下每条命令执行完毕立即回调，不等待全部完成。

        Args:
            commands: 单条命令字符串，或多条命令的列表
            parallel: True 并行执行，False 顺序执行
            max_workers: 并行时最大线程数，默认 CPU 核心数
            stop_on_error: 顺序执行时遇错停止后续
            fail_fast: 并行执行时任一条失败即取消剩余任务
            on_result: 回调 (cmd_str, CmdResult) -> None，每条完成时调用

        Returns:
            CmdResult 列表（fail_fast 时未执行项为 None）
        """
        if isinstance(commands, str):
            commands = [commands]

        if not commands:
            return []

        mode_ = "simple" if verbose else "silent"

        if parallel and len(commands) > 1:
            workers = max_workers or os.cpu_count() - 1
            return self.run_parallel(commands, max_workers=workers, log_mode=mode_)
        else:
            return self.run_batch(commands, stop_on_error=stop_on_error, log_mode=mode_)


class CmdExecutorCli(CmdExecutor):
    """
    command in another subprocess。
    current subprocess can suppress output of next subprocess.
    """

    # ------------------------------------------------------------------
    # 统一入口：顺序 / 并行 + 即完即报 + 遇错即停
    # ------------------------------------------------------------------

    def exec_commands(
        self,
        commands: str | Sequence[str],
        *,
        parallel: bool = False,
        max_workers: int | None = None,
        stop_on_error: bool = False,
        fail_fast: bool = False,
        on_result: callable | None = None,
        verbose: bool = False,  # verbose
        is_compile: bool = True,
    ) -> list[CmdResult]:
        """
        执行一条或多条命令，支持顺序/并行。
        并行模式下每条命令执行完毕立即回调，不等待全部完成。

        Args:
            commands: 单条命令字符串，或多条命令的列表
            parallel: True 并行执行，False 顺序执行
            max_workers: 并行时最大线程数，默认 CPU 核心数
            stop_on_error: 顺序执行时遇错停止后续
            fail_fast: 并行执行时任一条失败即取消剩余任务
            on_result: 回调 (cmd_str, CmdResult) -> None，每条完成时调用

        Returns:
            CmdResult 列表（fail_fast 时未执行项为 None）
        """
        if isinstance(commands, str):
            commands = [commands]

        if not commands:
            return []

        if parallel and len(commands) > 1:
            return self._exec_parallel(
                commands, max_workers, fail_fast, on_result, verbose, is_compile
            )
        else:
            return self._exec_sequential(commands, stop_on_error, on_result, verbose, is_compile)

    def _exec_sequential(
        self,
        commands: Sequence[str],
        stop_on_error: bool,
        on_result: callable | None,
        verbose: bool = False,  # verbose
        is_compile: bool = True,
    ) -> list[CmdResult]:
        """
        命令行过长解决
        compile simple mode, display only src
        command simple mode, display commad
        """
        results: list[CmdResult] = []
        n = len(commands)
        for i, cmd in enumerate(commands):
            r = self.run(cmd, log_mode="off")
            results.append(r)

            command = r.command
            simple_command = ""
            if verbose:
                simple_command = command
            else:
                simple_command = command.split(" ")[-1]
            if not is_compile:
                simple_command = command

            if verbose:
                print(f"[{i + 1}/{n}] - {simple_command}", flush=True)
                if r.stdout:
                    print(f"{r.stdout}", flush=True)
                if r.stderr:
                    print(f"{r.stderr}", flush=True)
            else:
                print(f"[{i + 1}/{n}] - {simple_command}", flush=True)

            if on_result:
                on_result(_format_command(cmd), r)
            if stop_on_error and not r.success:
                break
        return results

    def __output_parallel(
        self, completed: int, n: int, r: CmdResult, mode: str = "verbose"
    ) -> None:
        if mode == "silent":
            return
        command = r.command
        src = command.split(" ")[-1] if command else ""
        print(f"[{completed}/{n}] - {src}", flush=True)
        if mode == "verbose":
            print(f"{command}", flush=True)
            if r.stdout:
                print(f"{r.stdout}", flush=True)
        if r.stderr:
            print(f"{r.stderr}", flush=True)

    def _exec_parallel(
        self,
        commands: Sequence[str],
        max_workers: int | None,
        fail_fast: bool,
        on_result: callable | None,
        verbose: bool = False,  # verbose
        is_compile: bool = True,
    ) -> list[CmdResult]:
        import threading

        n = len(commands)
        limit = max_workers or os.cpu_count() - 1 or 4
        print(f"[0/{n}] parallel: {n} commands, max_threads={limit}", flush=True)
        # sys.stderr.write(f"\033[1A\033[2K[0/{n}] parallel: {n} commands, max_threads={limit}\n")
        # sys.stderr.flush()

        results: list[CmdResult | None] = [None] * n
        completed = 0
        lock = threading.Lock()
        stop = threading.Event()
        sem = threading.Semaphore(limit)

        def _run_one(idx: int, cmd: str) -> None:
            nonlocal completed
            with sem:
                if stop.is_set():
                    return
                try:
                    r = self.run(cmd, log_mode="off")
                except Exception as e:
                    r = CmdResult(
                        returncode=-1,
                        stdout="",
                        stderr=str(e),
                        command=_format_command(cmd),
                    )
            with lock:
                if r.returncode != 0:
                    results[idx] = r
                completed += 1
                command = r.command
                command.split(" ")[-1] if command else ""
                mode_ = "verbose" if verbose else "simple"
                self.__output_parallel(completed, n, r, mode_)
                # print(
                #     f"[{completed}/{n}] [{src}] parallel:  rc={r.returncode}  ",
                #     flush=True,
                # )
                # sys.stderr.write(
                #     f"\033[1A\033[2K[{completed}/{n}] _exec_parallel:  rc={r.returncode}\n"
                # )
                # sys.stderr.flush()
            if on_result:
                on_result(_format_command(cmd), r)
            if fail_fast and not r.success:
                stop.set()

        threads = []
        for i, cmd in enumerate(commands):
            t = threading.Thread(target=_run_one, args=(i, cmd), daemon=True)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        print(f"[{completed}/{n}]  parallel: done,  completed", flush=True)
        return results  # type: ignore[return-value]


# ===========================================================================
# 测试用例：CmdExecutor（同进程执行）
# ===========================================================================
def test_executor_run_simple():
    """单条命令执行"""
    exe = CmdExecutor(log_mode="all")
    r = exe.run("echo hello")
    assert r.success
    assert "hello" in r.stdout


def test_executor_run_list():
    """列表形式命令（shell=False，避免 shlex 拆分）"""
    exe = CmdExecutor(log_mode="all")
    r = exe.run(["python", "-c", "print('hello from list')"])
    assert r.success
    assert "hello from list" in r.stdout


def test_executor_run_with_env():
    """带环境变量执行"""
    exe = CmdExecutor(env={"MY_VAR": "XXXX_test_value"}, log_mode="all")
    if sys.platform == "win32":
        r = exe.run("echo %MY_VAR%")
    else:
        r = exe.run("echo $MY_VAR")
    assert r.success
    assert "test_value" in r.stdout


def test_executor_run_error():
    """命令执行失败"""
    exe = CmdExecutor(log_mode="off")
    r = exe.run("python -c 'import sys; sys.exit(3)'")
    assert not r.success
    assert r.returncode == 3


def test_executor_run_check():
    """check=True 时失败抛出异常"""
    import pytest

    exe = CmdExecutor(check=True, log_mode="off")
    with pytest.raises(RuntimeError):
        exe.run("python -c 'import sys; sys.exit(1)'")


def test_executor_run_timeout():
    """超时测试"""
    exe = CmdExecutor(timeout=1, log_mode="off")
    if sys.platform == "win32":
        r = exe.run('python -c "import time; time.sleep(10)"')
    else:
        r = exe.run("python -c 'import time; time.sleep(10)'")
    assert r.timed_out
    assert not r.success


# def test_executor_exec_parallel_fail_fast():
#     """并行执行遇错即停"""
#     exe = CmdExecutorCli(log_mode="off")
#     results = exe.exec_commands(
#         [
#             "python -c 'import sys; sys.exit(1)'",
#             "echo ok",
#             "echo also_ok",
#         ],
#         parallel=True,
#         max_workers=2,
#         fail_fast=True,
#         mode="silent",
#     )
#     print(f"test_executor_exec_parallel_fail_fast: {results}")
#     successes = [r for r in results if r is not None]
#     assert len(successes) <= 3


def test_executor_run_batch():
    """批量执行"""
    exe = CmdExecutor(log_mode="off")
    results = exe.run_batch(["echo x", "echo y"], stop_on_error=True)
    assert len(results) == 2
    assert all(r.success for r in results)


def test_executor_run_parallel():
    """并行执行多条命令（run_parallel），顺序与输入一致"""
    exe = CmdExecutor(log_mode="off")
    results = exe.run_parallel(
        ["echo a", "echo b", "echo c"],
        max_workers=2,
    )
    assert len(results) == 3
    assert all(r.success for r in results)
    assert "a" in results[0].stdout
    assert "b" in results[1].stdout
    assert "c" in results[2].stdout


def test_executor_with_options():
    """临时覆盖配置"""
    exe = CmdExecutor(cwd="C:/", log_mode="off")
    with exe.with_options(cwd="C:/Windows"):
        r = exe.run("cd" if sys.platform == "win32" else "pwd")
        assert r.success


# ===========================================================================
# 测试用例：CmdExecutorCli（运行在子进程中，行为与 CmdExecutor 一致）
# ===========================================================================
def test_cli_executor_run_simple():
    """CmdExecutorCli 单条命令（继承 CmdExecutor.run）"""
    exe = CmdExecutorCli(log_mode="off")
    r = exe.run("echo hello_from_cli")
    assert r.success
    assert "hello_from_cli" in r.stdout


def test_cli_executor_exec_sequential():
    """CmdExecutorCli 顺序执行"""
    exe = CmdExecutorCli(log_mode="off")
    results = exe.exec_commands(
        ["echo a", "echo b", "echo c"],
        parallel=False,
        mode="silent",
    )
    assert len(results) == 3
    assert all(r.success for r in results)


def test_cli_executor_exec_sequential_verbose():
    """CmdExecutorCli 顺序执行 + verbose 模式（验证日志输出）"""
    exe = CmdExecutorCli(log_mode="off")
    results = exe.exec_commands(
        ["echo step1", "echo step2"],
        parallel=False,
        mode="verbose",
    )
    assert len(results) == 2
    assert all(r.success for r in results)


def test_cli_executor_exec_parallel():
    """CmdExecutorCli 并行执行"""
    exe = CmdExecutorCli(log_mode="off")
    results = exe.exec_commands(
        ["echo x", "echo y", "echo z"],
        parallel=True,
        max_workers=2,
        mode="silent",
    )
    assert len(results) == 3


def test_cli_executor_exec_parallel_fail_fast():
    """CmdExecutorCli 并行执行遇错即停"""
    exe = CmdExecutorCli(log_mode="off")
    results = exe.exec_commands(
        [
            "python -c 'import sys; sys.exit(1)'",
            "echo ok",
            "echo also_ok",
        ],
        parallel=True,
        max_workers=2,
        fail_fast=True,
        mode="silent",
    )
    successes = [r for r in results if r is not None]
    assert len(successes) <= 3


def test_cli_subprocess():
    """
    CmdExecutorCli 运行在子进程中：
    父进程通过 subprocess 启动一个 Python 脚本，
    脚本内部使用 CmdExecutorCli 执行多条命令，
    父进程捕获 stdout/stderr 输出。
    """
    import os
    import subprocess
    import tempfile

    # 构建子进程脚本内容
    script = """
import sys
sys.path.insert(0, r"{pymakex_dir}")
from executor import CmdExecutorCli

# 模拟构建任务：编译 + 链接
cmds = [
    "echo [CC] compiling main.c",
    "echo [CC] compiling utils.c",
    "echo [LD] linking target.elf",
]

# 使用 CmdExecutorCli 顺序执行，verbose 模式输出完整日志
exe = CmdExecutorCli(log_mode="off")
results = exe.exec_commands(cmds, parallel=False, mode="verbose")

# 打印结果摘要
for i, r in enumerate(results):
    status = "OK" if r.success else "FAIL"
    print(f"[{{i+1}}/{{len(results)}}] {{status}} rc={{r.returncode}}")

sys.exit(0 if all(r.success for r in results) else 1)
"""

    # 获取 pymakex 父目录（executor 模块所在目录的上级）
    pymakex_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script = script.format(pymakex_dir=pymakex_dir)

    # 写入临时脚本
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(script)
        tmp_path = f.name

    try:
        # 子进程运行脚本
        proc = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=30,
        )

        print("=== subprocess stdout ===")
        print(proc.stdout)
        print("=== subprocess stderr ===")
        print(proc.stderr)
        print(f"=== exit code: {proc.returncode} ===")

        # 验证：子进程应该成功执行
        assert proc.returncode == 0, f"subprocess failed: {proc.stderr}"
        assert "compiling main.c" in proc.stdout
        assert "compiling utils.c" in proc.stdout
        assert "linking target.elf" in proc.stdout
        assert "[3/3]" in proc.stdout
    finally:
        os.unlink(tmp_path)


if __name__ == "__main__":
    # test_executor_run_simple()
    # test_executor_run_list()
    # test_executor_run_with_env()
    # test_executor_run_error()
    # test_executor_run_timeout()
    test_executor_run_parallel()

    # test_executor_run_batch()
    # test_executor_with_options()

    # # cmd cli class test

    # test_cli_executor_run_simple()
    # test_cli_executor_exec_sequential()
    # test_cli_executor_exec_sequential_verbose()
    # test_cli_executor_exec_parallel()
    # test_cli_executor_exec_parallel_fail_fast()

    # test_cli_subprocess()


# def _detect_encoding() -> str:
#     """自动检测当前系统编码，兼容Windows和Linux"""
#     if sys.platform == "win32":
#         import locale

#         try:
#             cp = locale.getpreferredencoding()
#             if cp and cp.lower() in ("utf-8", "utf8"):
#                 return "utf-8"
#             if cp and cp.lower() in ("gbk", "gb2312", "gb18030"):
#                 return "gbk"
#         except Exception:
#             pass
#         try:
#             import ctypes

#             kernel32 = ctypes.windll.kernel32
#             code_page = kernel32.GetACP()
#             if code_page == 65001:  # UTF-8代码页
#                 return "utf-8"
#             elif code_page in (936, 54936):  # GBK/GB18030代码页
#                 return "gbk"
#         except Exception:
#             pass
#         return "gbk"  # Windows默认GBK
#     return "utf-8"  # Linux默认UTF-8


# def _decode(data: bytes, encoding: str) -> str:
#     """安全解码字节，多编码 fallback，兼容Windows/Linux"""
#     if not data:
#         return ""

#     # 动态构建编码尝试列表（避免重复）
#     encodings_to_try = [encoding]
#     if encoding.lower() not in ("utf-8", "utf8"):
#         encodings_to_try.append("utf-8")
#     if encoding.lower() not in ("gbk", "gb2312", "gb18030"):
#         encodings_to_try.append("gbk")
#     if "latin-1" not in encodings_to_try:
#         encodings_to_try.append("latin-1")

#     # 尝试每种编码
#     for enc in encodings_to_try:
#         try:
#             return data.decode(enc)
#         except (UnicodeDecodeError, LookupError):
#             continue

#     # 最终fallback：使用replace模式
#     return data.decode(encoding, errors="replace")
