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

import hashlib
import inspect
import os
import queue
import threading
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any


def file_hash(file_path: str) -> str:
    if not os.path.exists(file_path):
        return ""
    h = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            h.update(chunk)
    return h.hexdigest()


def to_dict(obj: dataclass) -> dict:
    return asdict(obj)


def format_include_flags(include_dirs: list[str | Path], prefix: str = "-I") -> list[str]:
    """将目录列表格式化为编译器 -I 参数"""
    return [f"{prefix}{str(d)}" for d in include_dirs]


def format_macro_flags(macros: dict[str, str], prefix: str = "-D") -> list[str]:
    """
    return [f"{prefix}{k}" if not v else f"{prefix}{k}={v}" for k, v in macros.items()]

    """
    macro_lst = []
    macor_keys = sorted(macros.keys())
    for k in macor_keys:
        v = macros.get(k, "")
        if v.strip():
            v = f"={v.strip()}"
        macro_lst.append(f"{prefix}{k.strip()}{v}")
    return macro_lst


def format_libs_flags(libs: list[str], prefix: str = "-l") -> list[str]:
    return [f"{prefix}{lib.strip()}" for lib in libs]


def format_lib_pathes_flags(lib_pathes: list[str], prefix: str = "-L") -> list[str]:
    return [f"{prefix}{lib}" for lib in lib_pathes]


class Color:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"

    # YELLOW = "\033[33m"
    # BLUE2 = "\033[34m"


# def print_err(*args):
#     # 将所有参数用空格拼接成字符串
#     content = " ".join(str(arg) for arg in args)
#     print(f"{Color.RED}[ERROR] {content}{Color.END} ")


# def print_warn(*args):
#     content = " ".join(str(arg) for arg in args)
#     print(f"{Color.YELLOW}[WARN] {content}{Color.END}")


# def print_ok(*args):
#     content = " ".join(str(arg) for arg in args)
#     print(f"{Color.GREEN}[OK] {content}{Color.END}")


# def print_info(*args):
#     content = " ".join(str(arg) for arg in args)
#     print(f"{Color.BLUE}[INFO] {content}{Color.END} ")


# def print_info(*args):
#     # 获取调用者的帧信息
#     frame = inspect.stack()[1].frame

#     # 1. 提取纯文件名（不含目录）
#     full_path = frame.f_code.co_filename
#     filename = os.path.basename(full_path)

#     lineno = frame.f_lineno

#     # 2. 提取类名（兼容实例方法和类方法）
#     class_name = ""
#     if "self" in frame.f_locals:
#         class_name = type(frame.f_locals["self"]).__name__
#     elif "cls" in frame.f_locals:
#         class_name = frame.f_locals["cls"].__name__

#     # 3. 拼接位置信息
#     location_parts = [filename, str(lineno)]
#     if class_name:
#         location_parts.insert(1, class_name)
#     # location_parts.append(func_name)

#     location_str = ":".join(location_parts)

#     content = " ".join(str(arg) for arg in args)
#     print(f"{Color.BLUE}[INFO] {location_str} - {content}{Color.END}")


# def print_debug(*args):
#     content = " ".join(str(arg) for arg in args)
#     print(f"{Color.CYAN}[DEBUG] {content}{Color.END}  ")


def dict_equal(a, b):
    """递归判断两个嵌套字典/列表是否完全一致"""
    if type(a) != type(b):
        return False
    if isinstance(a, dict):
        if set(a.keys()) != set(b.keys()):
            return False
        return all(dict_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        if len(a) != len(b):
            return False
        return all(dict_equal(x, y) for x, y in zip(a, b, strict=False))
    return a == b


class ContainSafe:
    def __init__(self, maxsize: int = 0):
        self._seen = set()
        self._lock = threading.Lock()

    def put(self, item: Any, block: bool = True, timeout: float | None = None):
        """放入队列"""
        with self._lock:
            self._seen.add(item)

    def add(self, item: Any, block: bool = True, timeout: float | None = None):
        """放入队列"""
        with self._lock:
            self._seen.add(item)

    def append(self, item: Any, block: bool = True, timeout: float | None = None):
        """放入队列"""
        with self._lock:
            self._seen.add(item)

    def get(self, block: bool = True, timeout: float | None = None) -> Any:
        """取出队列"""
        pass

    def __contains__(self, item: Any) -> bool:
        # 支持 if item in q:
        with self._lock:
            return item in self._seen

    def empty(self) -> bool:
        with self._lock:
            self._seen.clear()

    def qsize(self) -> int:
        with self._lock:
            return len(self._seen)


class ContainsQueue:
    def __init__(self, maxsize: int = 0):
        self._q = queue.Queue(maxsize=maxsize)
        self._seen = set()
        self._lock = threading.Lock()

    def put(self, item: Any, block: bool = True, timeout: float | None = None):
        """放入队列"""
        with self._lock:
            self._q.put(item, block=block, timeout=timeout)
            self._seen.add(item)

    def get(self, block: bool = True, timeout: float | None = None) -> Any:
        """取出队列"""
        item = self._q.get(block=block, timeout=timeout)
        with self._lock:
            self._seen.discard(item)
        return item

    def task_done(self):
        self._q.task_done()

    def join(self):
        self._q.join()

    def __contains__(self, item: Any) -> bool:
        # 支持 if item in q:
        with self._lock:
            return item in self._seen

    def empty(self) -> bool:
        with self._lock:
            return self._q.empty()

    def qsize(self) -> int:
        with self._lock:
            return self._q.qsize()


class LogLevel(Enum):
    VERBOSE = 0
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4


class Logger:
    def __init__(self):
        # 记录当前 logger.py 的绝对路径，用于后续过滤
        self._logger_file = os.path.abspath(__file__)
        self.silent = False
        self.mode = 0  # 0: 测试模式， 1: 运行模式 不输出位置信息
        self.level = LogLevel.INFO.name
        self.level = LogLevel.DEBUG.name

    def _get_caller_info(self):
        """
        向上遍历调用栈，找到第一个不是 logger.py 本身的调用者
        """
        # 获取完整的调用栈
        stack = inspect.stack()

        # 从第1层开始找（第0层是 _get_caller_info 自己）
        for frame_info in stack[1:]:
            # 获取当前帧的文件绝对路径
            current_file = os.path.abspath(frame_info.filename)

            # 如果这个文件就是 logger.py 本身，跳过，继续往上找
            if current_file == self._logger_file:
                continue

            # 找到了外部的调用者！提取信息
            frame = frame_info.frame
            filename = os.path.basename(frame.f_code.co_filename)
            lineno = frame.f_lineno

            # 提取类名
            class_name = ""
            if "self" in frame.f_locals:
                class_name = type(frame.f_locals["self"]).__name__
            elif "cls" in frame.f_locals:
                class_name = frame.f_locals["cls"].__name__

            # 组装位置字符串
            parts = [filename, str(lineno)]
            if class_name:
                parts.insert(1, class_name)
            # parts.append(func_name)

            return ":".join(parts)

        # 如果找了一圈都没找到（极端情况），返回未知
        return "Unknown:0:unknown"

    def _log(self, level, color, *args, **kwargs):
        if LogLevel[level].value < LogLevel[self.level].value:
            return
        if self.silent:
            return

        if not self.mode:
            location = self._get_caller_info()
        content = " ".join(str(arg) for arg in args)

        extra = ""
        if kwargs:
            extra = f" | {kwargs}"

        print(f"{color}[{level}] {location} - {content}{extra}{Color.END}")

    def output(self, *args, **kwargs):
        if self.silent:
            return
        content = " ".join(str(arg) for arg in args)
        extra = ""
        if kwargs:
            extra = f" | {kwargs}"
        print(f"{content} {extra} ")

    def info(self, *args, **kwargs):
        self._log("INFO", Color.BLUE, *args, **kwargs)

    def warn(self, *args, **kwargs):
        self._log("WARN", Color.YELLOW, *args, **kwargs)

    def error(self, *args, **kwargs):
        self._log("ERROR", Color.RED, *args, **kwargs)

    def debug(self, *args, **kwargs):
        self._log("DEBUG", Color.CYAN, *args, **kwargs)

    def set_mode(self, mode: int):
        self.mode = mode
        return self

    def set_level(self, level: str):
        if level.upper() in LogLevel.__members__:
            self.level = level.upper()
        else:
            self.level = LogLevel.INFO.name
        return self

    def set_silent(self, silent: bool):
        self.silent = silent
        return self


# 全局单例
log = Logger()


# class ExecutableFile:
#     @staticmethod
#     def is_executable_in_path(executable: str) -> bool:
#         """
#         Check if an executable is available in PATH.

#         Args:
#             executable: Name of the executable to check

#         Returns:
#             True if executable is found in PATH, False otherwise
#         """
#         path_env = os.environ.get("PATH", "")
#         paths = path_env.split(os.pathsep)

#         for path in paths:
#             exe_path = Path(path) / executable
#             if exe_path.is_file() and os.access(exe_path, os.X_OK):
#                 return True

#             if os.name == "nt":
#                 for ext in [".exe", ".bat", ".cmd"]:
#                     exe_with_ext = Path(path) / f"{executable}{ext}"
#                     if exe_with_ext.is_file():
#                         return True

#         return False

#     @staticmethod
#     def find_executable(executable: str) -> str | None:
#         """
#         Find the full path of an executable in PATH.

#         Args:
#             executable: Name of the executable to find

#         Returns:
#             Full path to executable if found, None otherwise
#         """
#         path_env = os.environ.get("PATH", "")
#         paths = path_env.split(os.pathsep)

#         for path in paths:
#             exe_path = Path(path) / executable
#             if exe_path.is_file() and os.access(exe_path, os.X_OK):
#                 return str(exe_path)

#             if os.name == "nt":
#                 for ext in [".exe", ".bat", ".cmd"]:
#                     exe_with_ext = Path(path) / f"{executable}{ext}"
#                     if exe_with_ext.is_file():
#                         return str(exe_with_ext)

#         return None

#     @staticmethod
#     def is_executable_in_directory(directory: str, executable: str) -> bool:
#         """
#         Check if an executable exists in a specific directory.

#         Args:
#             directory: Directory path to check
#             executable: Name of the executable to check

#         Returns:
#             True if executable is found in directory, False otherwise
#         """
#         dir_path = Path(directory)
#         if not dir_path.is_dir():
#             return False

#         exe_path = dir_path / executable
#         if exe_path.is_file() and os.access(exe_path, os.X_OK):
#             return True

#         if os.name == "nt":
#             for ext in [".exe", ".bat", ".cmd"]:
#                 exe_with_ext = dir_path / f"{executable}{ext}"
#                 if exe_with_ext.is_file():
#                     return True

#         return False

#     @staticmethod
#     def can_run_executable(executable: str, directory: str | None = None) -> bool:
#         """
#         Check if an executable can be run via subprocess.

#         Args:
#             executable: Name or path of the executable
#             directory: Optional directory to check first before PATH

#         Returns:
#             True if executable can be run, False otherwise
#         """
#         if directory and ExecutableFile.is_executable_in_directory(directory, executable):
#             return True

#         if ExecutableFile.is_executable_in_path(executable):
#             return True

#         exe_path = Path(executable)
#         if exe_path.is_file() and os.access(exe_path, os.X_OK):
#             return True

#         return False

#     @staticmethod
#     def try_run_executable(
#         executable: str,
#         args: list[str] | None = None,
#         directory: str | None = None,
#     ) -> tuple[bool, str]:
#         """
#         Try to run an executable and return success status and output.

#         Args:
#             executable: Name or path of the executable
#             args: Optional list of arguments to pass
#             directory: Optional directory to prepend to PATH

#         Returns:
#             Tuple of (success, output/error_message)
#         """
#         if args is None:
#             args = []

#         env = os.environ.copy()

#         if directory:
#             dir_path = Path(directory).resolve()
#             if dir_path.is_dir():
#                 env["PATH"] = str(dir_path) + os.pathsep + env.get("PATH", "")

#         try:
#             result = subprocess.run(
#                 [executable] + args, env=env, capture_output=True, text=True, timeout=5
#             )
#             return True, result.stdout if result.returncode == 0 else result.stderr
#         except FileNotFoundError:
#             return False, f"Executable not found: {executable}"
#         except subprocess.TimeoutExpired:
#             return False, f"Execution timeout: {executable}"
#         except Exception as e:
#             return False, f"Error running {executable}: {str(e)}"

#     @staticmethod
#     def get_executable_version(
#         executable: str, version_arg: str = "--version", directory: str | None = None
#     ) -> str | None:
#         """
#         Get version information from an executable.

#         Args:
#             executable: Name or path of the executable
#             version_arg: Argument to get version (default: --version)
#             directory: Optional directory to prepend to PATH

#         Returns:
#             Version string if successful, None otherwise
#         """
#         success, output = ExecutableFile.try_run_executable(executable, [version_arg], directory)
#         if success:
#             return output.strip().split("\n")[0] if output else None
#         return None

#     @staticmethod
#     def find_toolchain_executables(toolchain_dir: str, executables: list[str]) -> dict[str, bool]:
#         """
#         Check which executables from a list are available in a toolchain directory.

#         Args:
#             toolchain_dir: Directory containing toolchain executables
#             executables: List of executable names to check

#         Returns:
#             Dictionary mapping executable names to availability status
#         """
#         result = {}
#         for exe in executables:
#             result[exe] = ExecutableFile.is_executable_in_directory(toolchain_dir, exe)
#         return result


# def main():
#     print("=== Windows Executable Utilities Examples ===\n")

#     print("Example 1: Check if common Windows executables are in PATH")
#     common_exes = ["python", "cmd", "powershell", "notepad", "git"]
#     for exe in common_exes:
#         found = ExecutableFile.is_executable_in_path(exe)
#         status = "✓ Found" if found else "✗ Not found"
#         print(f"  {exe:15} : {status}")
#     print()

#     print("Example 2: Find full paths of executables")
#     for exe in ["python", "git", "arm-none-eabi-gcc"]:
#         path = ExecutableFile.find_executable(exe)
#         if path:
#             print(f"  {exe:20} -> {path}")
#         else:
#             print(f"  {exe:20} -> Not found")
#     print()

#     print("Example 3: Check ARM GCC toolchain in specific directory")
#     toolchain_dirs = [
#         r"C:\Program Files (x86)\GNU Arm Embedded Toolchain\10 2021.10\bin",
#         r"C:\ARM\bin",
#         r"D:\ARM_GCC\bin",
#     ]

#     for toolchain_dir in toolchain_dirs:
#         if Path(toolchain_dir).exists():
#             print(f"  Checking: {toolchain_dir}")
#             gcc_found = ExecutableFile.is_executable_in_directory(
#                 toolchain_dir, "arm-none-eabi-gcc"
#             )
#             print(f" arm-none-eabi-gcc: {'Found' if gcc_found else 'Not found'}")
#             break
#     else:
#         print("  No ARM toolchain directory found")
#     print()

#     print("Example 4: Try to run Python and get version")
#     success, output = ExecutableFile.try_run_executable("python", ["--version"])
#     if success:
#         print(f"  Python version: {output.strip()}")
#     else:
#         print(f"  Error: {output}")
#     print()

#     print("Example 5: Get version from various toolchain compilers")
#     compilers = [
#         ("gcc", "--version"),
#         ("clang", "--version"),
#         ("cl", None),
#         ("armcc", "--version_number"),
#     ]

#     for compiler, version_arg in compilers:
#         if version_arg:
#             version = ExecutableFile.get_executable_version(compiler, version_arg)
#         else:
#             version = (
#                 ExecutableFile.get_executable_version(compiler)
#                 if ExecutableFile.is_executable_in_path(compiler)
#                 else None
#             )

#         if version:
#             print(f"  {compiler:10} : {version[:60]}...")
#         else:
#             print(f"  {compiler:10} : Not found")
#     print()

#     print("Example 6: Check Keil ARM toolchain executables")
#     keil_dir = r"C:\Keil_v5\ARM\ARMCLANG\bin"
#     keil_executables = ["armclang", "armlink", "armar", "fromelf"]

#     if Path(keil_dir).exists():
#         print(f"  Checking Keil directory: {keil_dir}")
#         result = ExecutableFile.find_toolchain_executables(keil_dir, keil_executables)
#         for exe, found in result.items():
#             status = "✓" if found else "✗"
#             print(f"    {status} {exe}")
#     else:
#         print(f"  Keil directory not found: {keil_dir}")
#     print()

#     print("Example 7: Check GNU ARM toolchain executables")
#     arm_gcc_dir = r"C:\Program Files (x86)\GNU Arm Embedded Toolchain\10 2021.10\bin"
#     arm_executables = [
#         "arm-none-eabi-gcc",
#         "arm-none-eabi-g++",
#         "arm-none-eabi-ld",
#         "arm-none-eabi-as",
#         "arm-none-eabi-ar",
#         "arm-none-eabi-objcopy",
#     ]

#     if Path(arm_gcc_dir).exists():
#         print(f"  Checking ARM GCC directory: {arm_gcc_dir}")
#         result = ExecutableFile.find_toolchain_executables(arm_gcc_dir, arm_executables)
#         for exe, found in result.items():
#             status = "✓" if found else "✗"
#             print(f"    {status} {exe}")
#     else:
#         print(f"  ARM GCC directory not found: {arm_gcc_dir}")
#     print()

#     print("Example 8: Test running compiler from custom directory")
#     custom_toolchain = r"C:\ARM_Toolchains\gcc-arm\bin"
#     if Path(custom_toolchain).exists():
#         print(f"  Testing compiler from: {custom_toolchain}")
#         success, output = ExecutableFile.try_run_executable(
#             "arm-none-eabi-gcc", ["--version"], custom_toolchain
#         )
#         if success:
#             print(f"  Success: {output.split()[0] if output else 'No output'}")
#         else:
#             print(f"  Failed: {output}")
#     else:
#         print(f"  Custom toolchain directory not found")
#     print()

#     print("Example 9: Check MSVC compiler (Visual Studio)")
#     msvc_executables = ["cl", "link", "lib", "nmake"]
#     print("  Checking MSVC tools in PATH:")
#     for exe in msvc_executables:
#         found = ExecutableFile.is_executable_in_path(exe)
#         status = "✓" if found else "✗"
#         path = ExecutableFile.find_executable(exe) if found else "Not in PATH"
#         print(f"    {status} {exe:10} : {path}")
#     print()

#     print("Example 10: Verify toolchain before build")
#     required_tools = ["arm-none-eabi-gcc", "arm-none-eabi-objcopy", "make"]
#     print("  Pre-build toolchain verification:")
#     all_found = True
#     for tool in required_tools:
#         found = ExecutableFile.can_run_executable(tool)
#         status = "✓" if found else "✗"
#         print(f"    {status} {tool}")
#         if not found:
#             all_found = False

#     if all_found:
#         print("\n  ✓ All required tools are available. Ready to build!")
#     else:
#         print("\n  ✗ Some tools are missing. Please install missing toolchain components.")


# if __name__ == "__main__":
#     # r = my_test()
#     # print(r)
#     # main()

#     dir = r"D:\00_test"
#     dir = "D://00_test"
#     exe_name = "test2.exe"
#     found = ExecutableFile.is_executable_in_directory(dir, exe_name)
#     print(f"  Found: {found}")

#     found = ExecutableFile.is_executable_in_path(exe_name)
#     print(f"  Found in PATH: {found}")
