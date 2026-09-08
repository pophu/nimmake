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

from enum import Enum


class BuildType(Enum):
    """
    build_type:
        "target"  — executable
        "object"  — 编译为 .o 目标文件（默认）
        "static"  — static library
        "shared"  — shared library,dynamic library
        "header"  — only include header file
    """

    TARGET = 0
    OBJECT = 1
    STATIC = 2
    SHARED = 3
    HEADER = 4


class RunMode(Enum):
    TEST = 0
    RUN = 1


TASK_GRPAPH_HEADER = "##PYMAKEX_G_HDR##"

CACHE_FILENAME = "CACHE_NIMMAKE"

TOML_PYMAKEX = "NIMMAKE.toml"
TOML_PYMAKEX_CFG = "NIMMAKE_CFG.toml"

CFG_PY_FNAME = "Nimmake.py"

PARTY_LIB_PREFIX = "party__"

MAKEMODE = RunMode.TEST.value

C_EXTS: set[str] = {".c"}
CXX_EXTS: set[str] = {".cpp", ".cxx", ".cc", ".c++"}
ASM_EXTS: set[str] = {".asm", ".s", ".S"}
SOURCE_EXTS: set[str] = {".c", ".cpp", ".cxx", ".cc", ".c++", ".s", ".S", ".asm"}

HEADER_EXTS: set[str] = {".h", ".hpp", ".hxx", ".hh"}

EXCLUDE_DIRS: set[str] = {"doc", "docs", "examples"}
EXCLUDE_PREFIXES: set[str] = {}
EXCLUDE_SUFFIXES: set[str] = {"copy", "template"}

BARE_TARGET_OS_LST: set[str] = {"elf", "none"}

COMMAND_LST = "$TOOL$ $FLAGS$ $_CPPDEFFLAGS $_CPPINCFLAGS$ $PARTY_DEFFLAGS$ \
      $PARTY_INCS$ -c -o TARGET$ $SOURCE$ "

AR_LST = "$TOOL$ $arFLAGS$ $DEFINES$    $lib_NAME$ "
