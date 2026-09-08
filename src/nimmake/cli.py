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

"""Command-line interface for nimmake."""

import argparse
import json
import os
import sys
from pathlib import Path

from nimmake import Helper, __software__, __version__

# from nimmake.builders.builder import Builder
from nimmake.builders.parseParties import ParseParties
from nimmake.configs import CFG_PY_FNAME, TASK_GRPAPH_HEADER
from nimmake.executor import CmdExecutor
from nimmake.utils import log

TASK_GRAPH_HEADER = {
    "PARTIES": {},
    "COMMANDS": {},
    "PHONIES": {},
    "TARGETS": {},
    "STATIC": {},
    "SHARED": {},
    "ALIASES": {},
    "DEPENDS": {},
    "HELPER": {},
    "DEFAULTTARGET": {},
}

TASK_PARAMS = {
    "verbose": False,
    "silent": False,
    "dry_run": False,
    "clean": False,
    "mode": "build",
    "custom_args": None,
}


def hello_command(args: argparse.Namespace) -> None:
    """Say hello to NAME."""
    print(f"Hello, {args.name}!")


def _on_output(output: str):
    if output:
        print(output, file=sys.stdout)
    else:
        print(" ")
    pass


RUN_PYSCRIPT_OUTPUT_WITH_PYMAKE_DETECTED = False  # script output with pymake prefix


def build_task_graph(task_graph: str):
    # print("*********", task_graph)
    task = json.loads(task_graph)
    if "typ" not in task:
        return
    if task["typ"] not in TASK_GRAPH_HEADER:
        return
    if "name" not in task:
        return
    key = task["typ"]
    if key == "STATIC":
        key = "TARGETS"
    elif key == "SHARED":
        key = "TARGETS"
    elif key == "HELPER":
        key = "HELPER"
    TASK_GRAPH_HEADER[key].update({task["name"]: task})


def _run_pyscript_output(output: str, return_code: int = 0, is_stdout: bool = True):
    if not output:
        return
    if return_code == 0 and output.startswith(TASK_GRPAPH_HEADER):
        build_task_graph(output[len(TASK_GRPAPH_HEADER) :])
        # print("*********", output)
        return
    print(output, file=sys.stdout)
    pass


def execute_file_subprocess(
    filepath: str,
    verbose: bool = False,
    silent: bool = False,
    dry_run: bool = False,
    clean: bool = False,
    mode: str = "build",
    custom_args: dict = None,
    **kw,
):
    """
    subproces python file, params can be passed to all class of makefile.py
    you should recevie the params by sys.argv --pymake-args
    memory is not shared with the child process.
    It looks like safer than exec code.
    """
    cmd_executor = CmdExecutor()
    # script_args = []
    # params = {}

    # params.update({"verbose": verbose})
    # params.update({"silent": silent})
    # params.update({"dry_run": dry_run})
    # params.update({"clean": clean})
    # params.update({"mode": mode})

    # if custom_args:
    #     params.update(**custom_args)
    # TASK_PARAMS.update(**params)

    # script_args.append("--pymake-args")
    # script_args.append(json.dumps(params))
    r = cmd_executor.run_python_script(
        filepath,
        line_callback=_run_pyscript_output,
        # script_args=script_args,
    )
    return r.returncode, r.stderr


def execute_file_exec_global_vara(
    filepath: str,
    verbose: bool = False,
    silent: bool = False,
    dry_run: bool = False,
    clean: bool = False,
    mode: str = "build",
    custom_args: dict = None,
):
    """
    exec code, manually manage the global variables
    you should recevie the global variables in runned code
    memory is shared with the child process
    """
    if not os.path.exists(filepath):
        if not silent:
            print(f"Error: File {filepath} not found")
        sys.exit(1)

    if verbose and not silent:
        print(f"Executing file: {filepath}")

    if dry_run and not silent:
        print(f"Dry run mode - would execute: {filepath}")
        return

    global_vars = {
        "__name__": "__main__",
        "__file__": filepath,
        "VERBOSE": verbose,
        "SILENT": silent,
        "DRY_RUN": dry_run,
        "CLEAN": clean,
        "MODE": mode,
        "ARGS": custom_args or {},
    }

    # print(f" open : {filepath}")
    Path(str(filepath))

    with open(filepath, encoding="utf-8") as f:
        code = f.read()

    try:
        exec(code, global_vars)
    except Exception as e:
        # if not silent:
        print(f"Error executing {filepath}: {e}")
        sys.exit(1)


def _build_parallel(hlp: Helper):
    builder = Builder(hlp)
    print(builder.helper._env["PARTIES"])
    # builder.Build()
    # demo_stream_parallel()


def _build(hlp: Helper):
    Builder(hlp)
    log("------ ENDING -------")
    # r = builder.is_tool_exsited()
    # r = builder.gcc_triple()
    # r = builder.clang_triple()
    # print(r)
    # print(f"_build ---- {builder.helper._env['PARTIES']}")
    # builder.Build()


def __after_exec_file(r_code, r_err, **params):
    print("cli:", r_err)
    if int(r_code) != 0:
        print("== No Target, No Command ==\n")
        print(r_err)
        print("== No Target, No Command ==\n")
        return

    # print(r_err, "00000000000")
    dct = {} if not r_err else json.loads(r_err)
    # log.debug("AFTER ===", dct)

    if "toolpath" in dct.keys():
        dct["toolpath"]

    hlp = Helper(register=False)
    hlp.Update(dct)
    Builder(helper=dct, toolpath=dct["toolpath"], **params)


def show_build_graph():
    for ks, vs in TASK_GRAPH_HEADER.items():
        print(ks)
        for k, v in vs.items():
            # print("\t", k, v)
            print("\t", k)
            print()

    for k, v in TASK_PARAMS.items():
        print(k, v)


def run():
    # log.debug(f"TASK_GRAPH_HEADER: {TASK_GRAPH_HEADER['TARGETS']}")
    # log.debug(f"PHONIES: {TASK_GRAPH_HEADER['PHONIES']}")
    # log.debug(f"COMMANDS: {TASK_GRAPH_HEADER['COMMANDS']}")
    # log.debug(f"TASK_PARAMS: {TASK_PARAMS}")
    pp = ParseParties(TASK_GRAPH_HEADER, TASK_PARAMS)
    pp.idle()


def __parse_params(args: argparse.Namespace, unknown: list[str]) -> dict:
    # log.error(f"args, unknown: {args}, {unknown} ")
    custom_args = {}
    for arg in unknown:
        if arg.startswith("--"):
            if "=" in arg:
                key, value = arg[2:].split("=", 1)
                custom_args[key] = value
            else:
                custom_args[arg[2:]] = True
        elif arg.startswith("-"):
            custom_args[arg[1:]] = True
        else:
            if "positional" not in custom_args:
                custom_args["positional"] = []
            custom_args["positional"].append(arg)
    if "positional" in custom_args:
        custom_args["positional"][0]
    # log.info(f"args, unknown: {args}, {unknown} ")

    args.file = args.file if args.file.endswith(".py") else f"{args.file}.py"

    params = {
        "verbose": args.verbose,
        "silent": args.silent,
        "dry_run": args.dry_run,
        "mode": args.mode,
        "clean": args.clean,
        "jobs": args.jobs,
        "toml": args.toml,
        "party": args.party,
        "cache": args.cache,
        "compiledb": args.compiledb,
        "logger": args.logger,
        "ninja": args.ninja,
        **custom_args,
    }
    params.update(**custom_args)
    TASK_PARAMS.update(**params)
    # log.info(f"params: {params}")

    # core = MyParties("CORE", "src_stm/Core")
    # a = core.Dump()
    # print(a, type(a))

    r_code, r_err = execute_file_subprocess(
        args.file,
        **params,
        # verbose=args.verbose,
        # silent=args.silent,
        # dry_run=args.dry_run,
        # mode=args.mode,
        # clean=args.clean,
        # custom_args=custom_args,
    )
    if int(r_code) != 0:
        log.output("==================== ")
        log.output(r_err)
        log.output("====================\n")
        exit(1)
        return

    # show_build_graph()
    # print("*********", TASK_GRAPH_HEADER)

    log.output()
    log.output("*" * 40)
    log.output("******* begin to process task *******")
    log.output("*" * 40)
    log.output()

    run()


def main():
    """
    pymakex --t=ninja  -> "t":"ninja"
    pymakex --dry-run  -> "dry_run":True
    pymakex --mode=ninja  -> "mode":"ninja"
    pymakex =m ninja  -> "mode":"ninja"
    """
    _parser = argparse.ArgumentParser(
        prog="pycmd",
        description="A Python compiler for building MCU firmware",
        epilog="Example: pymake -f Makefile.py --target=release --config=debug",
        allow_abbrev=False,
    )

    _parser.add_argument(
        "-f",
        "--file",
        default=CFG_PY_FNAME,
        help=f"Specify the command file to execute (default: {CFG_PY_FNAME})",
    )

    _parser.add_argument(
        "-s",
        "--silent",
        action="store_true",
        help="Silent mode - suppress all output except errors",
    )

    _parser.add_argument(
        "-l",
        "--logger",
        dest="logger",
        type=int,
        default=0,
        help="Log mode - 0: quiet, 1: verbose, 2: debug",
    )

    _parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose mode - show detailed execution information",
    )

    _parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode - show what would be executed without actually running",
    )

    _parser.add_argument(
        "-m",
        "--mode",
        type=str,
        default="build",
        choices=["ninja", "build", "compiledb", "cache", "dryrun"],
        help="构建模式",
    )

    _parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        help="Clean all build files",
    )

    _parser.add_argument(
        "--compiledb",
        action="store_true",
        help="generate compile_commands.json file",
    )

    _parser.add_argument(
        "--picolib",
        action="store_true",
        help="compile picolib file",
    )

    _parser.add_argument(
        "-n",
        "--ninja",
        dest="ninja",
        type=str,
        nargs="?",
        const="update",  # default value
        default="",  # no value passed
        help="Use ninja build mode - build or update",
    )

    _parser.add_argument(
        "-cch",
        "--cache",
        dest="cache",
        type=str,
        nargs="?",
        const="update",  # default value
        default="",  # no value passed
        help="Use cache mode - build or update",
    )

    # _parser.add_argument(
    #     "-cch",
    #     "--cache",
    #     dest="cache",
    #     type=str,
    #     default="",
    #     help="Use cache mode - buildcache or build from cache",
    # )

    _parser.add_argument(
        "-j",
        "--jobs",
        dest="jobs",
        type=int,
        default=1,
        help="Specify number of concurrent jobs",
    )

    _parser.add_argument(
        "-t",
        "--toml",
        dest="toml",
        type=str,
        help="Specify TOML file path",
    )

    _parser.add_argument(
        "-p",
        "--party",
        dest="party",
        type=str,
        help="Specify party file path",
    )

    _parser.add_argument(
        "-v", "-V", "--version", action="version", version=f"{__software__} {__version__}"
    )

    args, unknown = _parser.parse_known_args()
    # args = _parser.parse_args()
    __parse_params(args, unknown)


if __name__ == "__main__":
    main()
