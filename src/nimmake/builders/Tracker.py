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

"""Tracker —  Track the build of a project
especially src update
"""

import json
import os
import pickle
from pathlib import Path
from typing import Any

from nimmake.builders.buildCache import BuildCache
from nimmake.configs import ASM_EXTS, HEADER_EXTS
from nimmake.executor import CmdExecutor
from nimmake.utils import ContainSafe, log


class Tracker:
    def __init__(
        self,
        commands: list[dict[str:Any]],
        fpath: str | Path,
        fmt: str = "pickle",
        executor: CmdExecutor = None,
        headers_exts: list[str] = HEADER_EXTS,
        rebuild_objs: ContainSafe | None = None,
        # updated_hdrs: ContainSafe | None = None,
    ) -> None:
        self.commands: list[dict[str:Any]] = commands
        self.track_fpath: str | Path = Path(fpath)
        self.cache: dict = {}
        self.fmt: str = fmt
        self.executor: CmdExecutor = executor
        self.headers_exts: list[str] = headers_exts
        self.build_cache: BuildCache = BuildCache()
        if self.fmt == "pickle":
            self.track_fpath = self.track_fpath.with_suffix(".pkl")
        else:
            self.track_fpath = self.track_fpath.with_suffix(".json")

        if not self.track_fpath.exists():
            if self.fmt == "pickle":
                with open(self.track_fpath, "wb") as f:
                    pickle.dump({}, f)
            else:
                with open(self.track_fpath, "w", encoding="utf-8") as f:
                    json.dump({}, f)
        if self.fmt == "pickle":
            self.cache = self._load_pickle(self.track_fpath)
        else:
            self.cache = self._load_json(self.track_fpath)

        if "OBJECTS" not in self.commands:
            self.commands["OBJECTS"] = {}
        if "TARGETS" not in self.commands:
            self.commands["TARGETS"] = {}
        if "LIBS" not in self.commands:
            self.commands["LIBS"] = {}

        if not self.cache:
            self.cache.update({"OBJECTS": {}})
            self.cache.update({"TARGETS": {}})
            self.cache.update({"COMMANDS": {}})
            self.cache.update({"HEADERS": {}})
            self.cache.update({"DEPENDENCIES": {}})
            self.cache.update({"LIBS": {}})

        self.new_cache = {}
        self.new_cache.update({"OBJECTS": {}})
        self.new_cache.update({"TARGETS": {}})
        self.new_cache.update({"COMMANDS": {}})

        self.should_rebuild_objs: ContainSafe = rebuild_objs or ContainSafe()
        # self.updated_hdrs: ContainSafe = updated_hdrs or ContainSafe()
        # log.debug(f"Tracker init, cache ")
        # log.info(f"{self.cache}")
        # log.debug(f"Tracker init, commands ")
        # log.info(f"{self.commands}")

    def _load_pickle(self, fpath: str | Path) -> dict:
        if os.path.exists(fpath):
            with open(fpath, "rb") as f:
                return pickle.load(f)
        return {}

    def _save_pickle(self, fpath: str | Path):
        cache_to_save = {}
        for key, value in self.cache.items():
            if isinstance(value, dict):
                cache_to_save[key] = {}
                for k, v in value.items():
                    if isinstance(v, set):
                        cache_to_save[key][k] = list(v)
                    else:
                        cache_to_save[key][k] = v
            else:
                cache_to_save[key] = value
        with open(fpath, "wb") as f:
            pickle.dump(cache_to_save, f)

    def _load_json(self, fpath: str | Path) -> dict:
        if os.path.exists(fpath):
            try:
                with open(fpath, encoding="utf-8") as f:
                    content = f.read().strip()
                    if not content:
                        return {}
                    cache = json.loads(content)
                    for toolchain in cache:
                        if isinstance(cache[toolchain], dict):
                            for src_file in cache[toolchain]:
                                if isinstance(cache[toolchain][src_file], list):
                                    cache[toolchain][src_file] = set(cache[toolchain][src_file])
                    return cache
            except (json.JSONDecodeError, Exception) as e:
                log.error(f"Failed to load JSON tracker file {fpath}: {e}")
                return {}
        return {}

    def _save_json(self, fpath: str | Path) -> None:
        cache_to_save = {}
        for key, value in self.cache.items():
            if isinstance(value, dict):
                cache_to_save[key] = {}
                for k, v in value.items():
                    if isinstance(v, set):
                        cache_to_save[key][k] = list(v)
                    else:
                        cache_to_save[key][k] = v
            else:
                cache_to_save[key] = value

        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(cache_to_save, f, indent=2, ensure_ascii=False)

    def _load(self, fpath: str | Path):
        if self.fmt == "pickle":
            self._load_pickle(fpath)
        else:
            self._load_json(fpath)

    def _save(self, fpath: str | Path = None):
        if fpath is None:
            fpath = self.track_fpath
        if self.fmt == "pickle":
            self._save_pickle(fpath)
        else:
            self._save_json(fpath)

    def Invalid(self):
        """
        set all valid to 0
        """
        for key, value in self.cache.items():
            if key not in ["OBJECTS", "TARGETS", "LIBS"]:
                continue
            if not isinstance(value, dict):
                continue
            for _k, v in value.items():
                if not isinstance(v, dict):
                    continue
                v.update({"valid": 0})

    def Track(self, out, cmd_lst=None):
        """
        track objects libs targets
        OBJECTS  LIBS  TARGETS
        """
        if cmd_lst is None:
            return None
        if len(cmd_lst) != 3:
            return None
        typ = cmd_lst[2]
        if typ == "OBJECTS":
            return self.__track_obj(out, cmd_lst)
        elif typ == "TARGETS":
            return self.__track_tgt(out, cmd_lst)
        elif typ == "LIBS":
            return self.__track_lib(out, cmd_lst)
        elif typ == "STATIC":
            # log.warn(f"Track {out} {cmd_lst}")
            return self.__track_lib(out, cmd_lst)
        elif typ == "SHARED":
            return self.__track_lib(out, cmd_lst)
        pass

    def __in_should_rebuild_objs(self, objs):
        for obj in objs:
            if obj in self.should_rebuild_objs:
                return True
        return False

    def __track_obj(self, out, cmd_lst=None):
        """
        track objects
        return : None or full cmd
        """
        cmd_item = self.commands["OBJECTS"].get(out, None)
        deps = self.commands.get("DEPENDENCIES", {})
        if cmd_item is None:
            log.warn(f"out {out} not found in commands[OBJECTS]")
            return
        cmd = cmd_item[0]
        src = cmd_item[1]
        # asm file
        if Path(src).suffix.lower() not in ASM_EXTS:
            hdrs_ = list(self.__dependencies(cmd, src, out))
        else:
            hdrs_ = []
        # add deps
        deps.update({out: hdrs_})

        ret = self.build_cache.should_rebuild(out, cmd, hdrs_)

        # .s no dependencies, so get src time to compare with out time
        if ".s" in src.lower() or ".asm" in src.lower():
            cache_tm = self.cache.get("OBJECTS", {}).get(out, {}).get("mtime", 0.0)
            src_tm = os.path.getmtime(src)
            if cache_tm < src_tm:
                ret = 6
                log.warn(f" {cache_tm} {src_tm}")

        # log.info(f"Track {out} {cmd_lst} {ret}")
        # log.info(f"Track {out} {cmd_lst} {ret}")
        # if ret == 0:
        #     return None
        if ret != 0:
            self.should_rebuild_objs.add(out)
            self.build_cache.record_build(out, cmd, hdrs_, src)
        full_cmd = f"{cmd} {src} -o {out}"
        is_valid = ret != 0
        return full_cmd, is_valid

    def __track_lib(self, out, cmd_item=None):
        """
        track libs
        """
        # typ = cmd_item[2]

        # cmd_item = self.commands["LIBS"].get(out, None)
        # log.warn(f"cmd_item= {cmd_item}")
        _cache_libs = self.cache.get("LIBS", {})
        _cache_deps = self.cache.get("DEPENDENCIES", {})
        if cmd_item is None:
            log.warn(f"out {out} not found in commands[LIBS]")
            return None

        cmd = cmd_item[0]
        objs_str = cmd_item[1]
        cmd += " " + out
        cmd += " " + objs_str

        # log.info(f" cmd= {cmd}")
        hash_ = self.build_cache._compute_command_hash(cmd)
        # _k exsit , hash not change , deps not change , skip.
        rebuild = False
        if not rebuild and not Path(out).exists():
            rebuild = True
        old_hash = _cache_libs.get(out, {}).get("hash", "")
        if not rebuild and hash_ != old_hash:
            rebuild = True
        # log.info(f"{rebuild}  ")
        # log.error(f"{rebuild}  hash= {(hash_ == old_hash)}   ")
        # # log.error(f"{rebuild}  hash= {cmd}   ")
        # # log.error(f"{rebuild}  {self.should_rebuild_objs}")
        objs = objs_str.split(" ")
        objs = [obj.strip() for obj in objs if obj.strip()]
        if not rebuild:
            rebuild = self.__in_should_rebuild_objs(objs)
            # for obj in objs:
            #     if obj in self.should_rebuild_objs:
            #         log.info(f"obj {obj} in rebuild objs")
            #         rebuild = True
            #         break
        # if not rebuild:
        #     return None

        # # TODO hash
        if rebuild:
            cnt = {"hash": hash_, "command": cmd, "src": objs_str, "valid": 1}
            cnt_dep = objs
            _cache_libs.update({out: cnt})
            _cache_deps.update({out: cnt_dep})
        full_cmd = f"{cmd}"
        # log.info(f"full_cmd= {full_cmd}")
        is_valid = rebuild
        return full_cmd, is_valid
        pass

    def __track_tgt(self, out, cmd_lst=None):
        """
        track targets
        """
        cmd_item = self.commands["TARGETS"].get(out, None)
        _cache_targets = self.cache.get("TARGETS", {})
        _cache_deps = self.cache.get("DEPENDENCIES", {})
        cmd = cmd_item[0]
        objs_str = cmd_item[1]
        # _k exsit , hash not change , deps not change , skip.
        rebuild = False
        # _k not exsit, add to cache.
        hash_ = self.build_cache._compute_command_hash(cmd)
        if not rebuild and not Path(out).exists():
            rebuild = True
        # hash changed, rebuild.
        old_hash = _cache_targets.get(out, {}).get("hash", "")
        if not rebuild and hash_ != old_hash:
            rebuild = True
        # depend objs changed, rebuild.
        objs = objs_str.split(" ")
        objs = [obj.strip() for obj in objs if obj.strip()]
        # log.error(f"{rebuild}  hash= {hash_}   ")
        # log.error(f"{rebuild}  hash= {old_hash}   ")
        # log.error(f"{rebuild}  hash= {cmd}   ")
        # log.error(f"{rebuild}  {self.should_rebuild_objs}")
        if not rebuild:
            rebuild = self.__in_should_rebuild_objs(objs)

        # if not rebuild:
        #     return None
        if rebuild:
            cnt = {"hash": hash_, "command": cmd, "src": objs, "valid": 1}
            cnt_dep = objs
            _cache_targets.update({out: cnt})
            _cache_deps.update({out: cnt_dep})
        full_cmd = f"{cmd} -o {out} "
        is_valid = rebuild
        return full_cmd, is_valid
        # log.warn(f"__refresh_target: end ")

    def build_cache_reset(self):
        self.Invalid()
        _cache_objects = self.cache.get("OBJECTS", {})
        _cache_deps = self.cache.get("DEPENDENCIES", {})
        self.build_cache.set_log_cache(_cache_objects)
        self.build_cache.set_deps_cache(_cache_deps)

        self.should_rebuild_objs = ContainSafe()

    # def Refresh(self):
    #     """
    #     deal keys, objects , libs , targets , commands
    #     add stamp to cache?
    #     self.commands , no timestamp
    #     objects:
    #         if obj not exsit, add to cache. add src timestamp or now to cache.
    #         if hash changed, update cache timestamp to now.
    #         find deps timestamp, if depend timestap > obj timestamp, update cache timestamp to now.
    #         when compiling, if cache timestamp <= obj timestamp, skip.
    #     libs: depends objs hash
    #     libs: depends objs libs hash
    #     commands:
    #     {'BUILD\\OBJ\\SRC\\main.o': ['arm-none-eabi-gcc -c -mcpu=cortex-m4 -mfpu=fpv4-sp-d16 -mfloat-abi=softfp -mthumb -O2 --Wall -g -fdata-sections -ffunction-sections -ffreestanding -std=c99 -DXXXX=123 -DYYYY=123 -Isrc\\cmsis\\core -Isrc\\hal\\inc -o ', 'src\\app\\src\\main.c' ]
    #     caches:
    #     {'BUILD\\OBJ\\SRC\\main.o': [flags ,hash, timestamp]

    #     ASM des have dependencies.
    #     """
    #     # objects = self.commands.get("OBJECTS", {})
    #     # targets = self.commands.get("TARGETS", {})
    #     # libs = self.commands.get("LIBS", {})
    #     # deps = self.commands.get("DEPENDENCIES", {})
    #     # self.commands.get("HEADERS", {})
    #     # log.info(f"objects: {objects}")
    #     # log.info(f"targets: {targets}")
    #     # log.info(f"libs: {libs}")

    #     _cache_objects = self.cache.get("OBJECTS", {})
    #     _cache_deps = self.cache.get("DEPENDENCIES", {})
    #     _cache_libs = self.cache.get("LIBS", {})
    #     _cache_targets = self.cache.get("TARGETS", {})
    #     self.build_cache.set_log_cache(_cache_objects)
    #     self.build_cache.set_deps_cache(_cache_deps)

    #     shoulds = self.__check_objs()
    #     for sh in shoulds:
    #         self.should_rebuild_objs.add(sh)
    #     # self.should_rebuild_objs = self.__check_objs()
    #     # log.info(f"objects: {self.should_rebuild_objs}")
    #     # objects 添加 deps to commands, 同时合并header stamp

    #     # log.info(f"libs: {libs}")
    #     # how to rebuild, hash
    #     self.__refresh_party_libs()

    #     self.__refresh_target()

    #     # log.info(f"objects: {objects}")
    #     self._save(self.track_fpath)

    def __check_objs(self) -> None:
        log.debug("__check_objs ... ")
        objects = self.commands.get("OBJECTS", {})
        # deps = self.commands.get("DEPENDENCIES", {})
        should_rebuild_objs = []
        # objects 添加 deps to commands, 同时合并header stamp
        for _k, v in objects.items():
            self.__track_obj(_k, v)
            # if r:
            #     should_rebuild_objs.append(_k)
        return should_rebuild_objs

    # def __refresh_party_libs2(self) -> None:
    #     # log.debug(f"__refresh_party_libs ... ")
    #     libs = self.commands.get("LIBS", {})
    #     _cache_libs = self.cache.get("LIBS", {})
    #     _cache_deps = self.cache.get("DEPENDENCIES", {})
    #     for _k, v in libs.items():
    #         # out = self.__track_lib(_k, v)
    #         # out_ = _k
    #         cmd = v[0]
    #         objs_str = v[1]
    #         cmd += " " + _k
    #         cmd += " " + objs_str

    #         # log.info(f" cmd= {cmd}")
    #         hash = self.build_cache._compute_command_hash(cmd)
    #         # log.info(f" hash= {hash}")
    #         # _k exsit , hash not change , deps not change , skip.
    #         rebuild = False
    #         # log.info(f" hash= {rebuild} {Path(_k)} {Path(_k).exists()}")
    #         if not rebuild and not Path(_k).exists():
    #             rebuild = True
    #         # log.info(f"{rebuild} hash= {hash} {_cache_libs.get(_k, {}).get('hash', '')}")
    #         if not rebuild and hash != _cache_libs.get(_k, {}).get("hash", ""):
    #             rebuild = True
    #         objs = objs_str.split(" ")
    #         objs = [obj.strip() for obj in objs if obj.strip()]
    #         if not rebuild:
    #             for obj in objs:
    #                 if obj in self.should_rebuild_objs:
    #                     rebuild = True
    #                     break
    #         # log.info(f"{rebuild} ")
    #         if not rebuild:
    #             continue

    #         # out = self.__track_lib(_k, v)
    #         # log.error(out)

    #         # if not out:
    #         #     continue

    #         # TODO hash
    #         cnt = {"hash": hash, "command": cmd, "src": objs_str, "valid": 1}
    #         cnt_dep = objs
    #         _cache_libs.update({_k: cnt})
    #         _cache_deps.update({_k: cnt_dep})

    # def __refresh_party_libs(self) -> None:
    #     # log.debug(f"__refresh_party_libs ... ")
    #     libs = self.commands.get("LIBS", {})
    #     _cache_libs = self.cache.get("LIBS", {})
    #     _cache_deps = self.cache.get("DEPENDENCIES", {})
    #     for _k, v in libs.items():
    #         hash_ = self.__track_lib(_k, v)
    #         log.error(f"__refresh_party_libs: {_k} {hash_}")

    # def __refresh_target(self) -> None:
    #     """
    #     if target is lib, check need rebuild.
    #     """
    #     targets = self.commands.get("TARGETS", {})
    #     _cache_targets = self.cache.get("TARGETS", {})
    #     _cache_deps = self.cache.get("DEPENDENCIES", {})
    #     # log.warn(f"__refresh_target ... {_cache_targets} ")
    #     for _k, v in targets.items():
    #         self.__track_tgt(_k, v)
    #         # # log.warn(_k, v)
    #         # cmd = v[0]
    #         # objs_str = v[1]
    #         # hash = self.build_cache._compute_command_hash(cmd)
    #         # # log.debug(f" cmd= {cmd}")
    #         # # log.debug(f" hash= {hash}")
    #         # # log.debug(f" hash 2= {_cache_targets.get(_k, {}).get('hash', '')}")
    #         # # _k exsit , hash not change , deps not change , skip.
    #         # rebuild = False
    #         # # _k not exsit, add to cache.
    #         # if not rebuild and not Path(_k).exists():
    #         #     rebuild = True
    #         # # hash changed, rebuild.
    #         # if not rebuild and hash != _cache_targets.get(_k, {}).get("hash", ""):
    #         #     rebuild = True
    #         # # depend objs changed, rebuild.
    #         # objs = objs_str.split(" ")
    #         # objs = [obj.strip() for obj in objs if obj.strip()]
    #         # if not rebuild:
    #         #     for obj in objs:
    #         #         if obj in self.should_rebuild_objs:
    #         #             # log.warn(obj)
    #         #             rebuild = True
    #         #             break
    #         # if not rebuild:
    #         #     continue
    #         # cnt = {
    #         #     "hash": hash,
    #         #     "command": v[0],
    #         #     "src": objs,
    #         #     "valid": 1,
    #         # }
    #         # cnt_dep = objs
    #         # # _cache_targets = {}  # 清空其他target ，target唯一？
    #         # _cache_targets.update({_k: cnt})
    #         # _cache_deps.update({_k: cnt_dep})
    #         # log.warn(f"__refresh_target: end ")

    # # def _compare_cmd_cache_by_src(self, cmd: dict, src: str) -> bool:
    # #     for k, _v in cmd.items():
    # #         if k not in ["TOOL", "FLAGS", "DEFINES", "TARGET"]:
    # #             if sorted(cmd.get(k)) != sorted(self.cache[src].get(k)):
    # #                 return False
    # #     # self.cache.update(dct)

    # # def _deal_cmd_item_obj(self, cmd: dict[str:any]) -> None:
    # #     src = cmd["SRC"][1]
    # #     new_tm_stamp = self._get_timestamp(src)
    # #     if new_tm_stamp == 0:
    # #         log.error(f"src file {src} not found")
    # #         return

    # #     if src not in self.cache:
    # #         self._item_from_cmd_to_cache(cmd, src, new_tm_stamp)
    # #         return

    # #     # compare timestamp  flags, if  equal, then modify cmd["VALID"] = 0
    # #     if new_tm_stamp == self.cache[src]["TIMESTAMP"]:
    # #         cmd["VALID"] = 0
    # #         return
    # #     if not self._compare_cmd_cache_by_src(cmd, src):
    # #         cmd["VALID"] = 0
    # #         return
    # #     self._item_from_cmd_to_cache(cmd, src, new_tm_stamp)

    # def _deal_cmd_item_target(self, cmd_dct: dict[str:Any]) -> int:
    #     log.error(f"cmd_dct  2 {cmd_dct}")
    #     target = cmd_dct["TARGET"]
    #     # lib target
    #     if target not in self.cache:
    #         self._item_from_cmd_to_cache(cmd_dct, target, 0)
    #         return

    def _get_timestamp(self, src: str) -> int:
        if not os.path.exists(src):
            return 0
        return os.path.getmtime(src)

    def _get_valid_commands(self) -> dict[str, Any]:
        cmd = {}
        cmd.update({"OBJECTS": {}})
        cmd.update({"LIBS": {}})
        cmd.update({"TARGETS": {}})
        objs = self.cache.get("OBJECTS", {})

        # log.debug(f"objs: {list(self.cache.keys())}")
        # log.debug(f"objs: {self.cache['TARGETS']}")

        for _k, _v in objs.items():
            if _v.get("valid", "0") == 1:
                v = f"{_v.get('command', '')} -o {_k}  {_v.get('src', '')}"
                cmd["OBJECTS"].update({_k: v})
        # ar  no  -o  _k
        libs = self.cache.get("LIBS", {})
        for _k, _v in libs.items():
            # log.info(f"{_k} : {_v}")
            if _v.get("valid", "0") == 1:
                v = f"{_v.get('command', '')}   "
                cmd["LIBS"].update({_k: v})
        targets = self.cache.get("TARGETS", {})
        for _k, _v in targets.items():
            # log.info(f"{_k} : {_v}")
            if _v.get("valid", "0") == 1:
                v = f"{_v.get('command', '')} -o {_k}"
                cmd["TARGETS"].update({_k: v})
        return cmd

    def track_flags(self) -> set[str]:
        pass

    def dep_callback(self, obj: str, lines: str) -> set[str]:
        headers = set()
        try:
            for line in lines:
                line = line.strip()
                if line.endswith("\\"):
                    line = line[:-1].strip()
                parts = line.split()
                for part in parts:
                    if part.endswith(":"):
                        continue
                    headers.add(Path(part).as_posix())
                    # print(self.header_exts)
                    # if any(part.endswith(ext) for ext in self.header_exts):
                    #     print(part, ext)
                    #     headers.add(part)
        except Exception:
            pass
        if obj not in self.cache["Dependencies"]:
            self.cache["Dependencies"].update({obj: []})
        self.cache["Dependencies"][obj].update({"deps": list(headers)})

    def __dependencies(self, cmd: str, src: str, obj: str = " ") -> set[str]:
        """
        get dependencies from toolchain command
        example:
        gcc -MM src/main.c -Iincs
        """
        headers = set()
        if not os.path.exists(src):
            return headers
        # # tool = self._get_tool(cmd_item["tool"] )
        # # if not tool:
        # #     return headers
        # # cmd_lst = [cmd_item["tool"]] + ["-MM", cmd_item["src"]] + [cmd_item["inc_flag"]]
        # cmd_lst = cmd.split(" ")
        # # log.debug(f"cmd_lst {cmd_lst}")
        # # cmd_lst = filter(lambda x: not x.strip(), cmd_lst)
        # cmd_lst = [x for x in cmd_lst if x.strip()]
        # # log.info(f"cmd_lst {cmd_lst[0]}")
        # log.debug(f"cmd_lst {cmd_lst}")
        # cmd_lst.append("-MM")
        # cmd_lst.append(src)
        # cmd_lst.append(obj)

        cmd = f"{cmd} -MM {src}"

        # cmd = "riscv-none-elf-gcc --version"
        # r = self.executor.run([cmd_lst[0], "-MM", src])
        # r = self.executor.run(cmd_lst)
        # r = self.executor.run(" ".join(cmd_lst))
        r = self.executor.run(cmd)
        # log.error(f"========cmd_lst {r} ")
        # return

        # log.debug(f"headers {r}")
        try:
            lines = r.stdout.strip().split("\n")
            for line in lines:
                line = line.strip()
                if line.endswith("\\"):
                    line = line[:-1].strip()

                parts = line.split()
                for part in parts:
                    if part.endswith(":"):
                        continue
                    headers.add(Path(part).as_posix())
                    # print(self.header_exts)
                    # if any(part.endswith(ext) for ext in self.header_exts):
                    #     print(part, ext)
                    #     headers.add(part)
        except Exception:
            pass
        # log.debug(f"headers {headers}")

        return headers

    def track(self) -> set[str]:
        """
        return :
            objetcs   targets  commands
        """
        # log.error("track obj src stamp, track dep ..compiling")
        pass
        # # objects ={}
        # # targets ={}
        # # comands ={}
        # if "DEPENDENCIES" not in self.cache:
        #     self.cache.update({"DEPENDENCIES": {}})
        # if "HEADERS" not in self.cache:
        #     self.cache.update({"HEADERS": []})

        # # 所有header VALID 为 0
        # for hdr in self.cache["HEADERS"]:
        #     self.cache["HEADERS"][hdr].update({"VALID": 0})

        # objects = self.cache.get("OBJECTS", {})
        # hdr_changed = []
        # for _, _v in objects.items():
        #     obj = _v.get("obj", "")
        #     lst = [_v.get("src", "")]
        #     cmd = _v
        #     deps = self._get_dependencies(cmd)
        #     lst.extend(deps)
        #     self.cache["DEPENDENCIES"].update({obj: lst})
        #     for _dep in deps:
        #         header_f = _dep
        #         tm_stamp = self._get_timestamp(header_f)
        #         if header_f not in self.cache["HEADERS"]:
        #             dct = {"TIMESTAMP": tm_stamp, "VALID": 1}
        #             dct.update({"TIMESTAMP", self._get_timestamp(header_f)})
        #             hdr_changed.append(header_f)
        #             continue
        #         if tm_stamp != self.cache["HEADERS"][header_f].get("TIMESTAMP", 0):
        #             dct = {"TIMESTAMP": tm_stamp, "VALID": 1}
        #             dct.update({"TIMESTAMP", self._get_timestamp(header_f)})
        #             hdr_changed.append(header_f)
        #             continue
        #         # self.cache["HEADERS"][header_f].update({"VALID": 0})

        # src_by_hdr_changed = []
        # for hdr in hdr_changed:
        #     for dep in self.cache["DEPENDENCIES"].items():
        #         if hdr in dep:
        #             src_by_hdr_changed.append(dep[0])

        # for src in src_by_hdr_changed:
        #     for item in self.cache["OBJECTS"].items():
        #         if src == item.get("src", ""):
        #             self.item.update({"VALID": 1})

    # def track2(self) -> set[str]:
    #     """
    #     return :
    #         objetcs   targets  commands
    #     """
    #     # objects ={}
    #     # targets ={}
    #     # comands ={}
    #     if "DEPENDENCIES" not in self.cache:
    #         self.cache.update({"DEPENDENCIES": {}})
    #     if "HEADERS" not in self.cache:
    #         self.cache.update({"HEADERS": []})

    #     # 所有header VALID 为 0
    #     for hdr in self.cache["HEADERS"]:
    #         self.cache["HEADERS"][hdr].update({"VALID": 0})

    #     objects = self.cache.get("OBJECTS", {})
    #     hdr_changed = []
    #     for _, _v in objects.items():
    #         obj = _v.get("obj", "")
    #         lst = [_v.get("src", "")]
    #         cmd = _v
    #         # TODO asm donot have dependencies
    #         deps = self._get_dependencies(cmd)
    #         lst.extend(deps)
    #         self.cache["DEPENDENCIES"].update({obj: lst})
    #         for _dep in deps:
    #             header_f = _dep
    #             tm_stamp = self._get_timestamp(header_f)
    #             if header_f not in self.cache["HEADERS"]:
    #                 dct = {"TIMESTAMP": tm_stamp, "VALID": 1}
    #                 dct.update({"TIMESTAMP", self._get_timestamp(header_f)})
    #                 hdr_changed.append(header_f)
    #                 continue
    #             if tm_stamp != self.cache["HEADERS"][header_f].get("TIMESTAMP", 0):
    #                 dct = {"TIMESTAMP": tm_stamp, "VALID": 1}
    #                 dct.update({"TIMESTAMP", self._get_timestamp(header_f)})
    #                 hdr_changed.append(header_f)
    #                 continue
    #             # self.cache["HEADERS"][header_f].update({"VALID": 0})

    #     src_by_hdr_changed = []
    #     for hdr in hdr_changed:
    #         for dep in self.cache["DEPENDENCIES"].items():
    #             if hdr in dep:
    #                 src_by_hdr_changed.append(dep[0])

    #     for src in src_by_hdr_changed:
    #         for item in self.cache["OBJECTS"].items():
    #             if src == item.get("src", ""):
    #                 self.item.update({"VALID": 1})

    # def _get_dependencies(self, cmd_item: dict[str:any]) -> set[str]:
    #     """
    #     get dependencies from toolchain command
    #     example:
    #     gcc -MM src/main.c -Iincs
    #     """
    #     headers = set()
    #     if not os.path.exists(cmd_item["src"]):
    #         return headers
    #     # tool = self._get_tool(cmd_item["tool"] )
    #     # if not tool:
    #     #     return headers
    #     # cmd_lst = [cmd_item["tool"]] + ["-MM", cmd_item["src"]] + [cmd_item["inc_flag"]]
    #     cmd_lst = cmd_item["tool"] + " -MM " + cmd_item["src"] + " " + cmd_item["inc_flag"]
    #     # log.error(f"========cmd_lst {cmd_lst}")
    #     r = self.executor.run(cmd_lst)

    #     try:
    #         lines = r.stdout.strip().split("\n")
    #         for line in lines:
    #             line = line.strip()
    #             if line.endswith("\\"):
    #                 line = line[:-1].strip()

    #             parts = line.split()
    #             for part in parts:
    #                 if part.endswith(":"):
    #                     continue
    #                 if any(part.endswith(ext) for ext in self.header_exts):
    #                     headers.add(part)
    #     except Exception:
    #         pass
    #     return headers

    # def cache_refresh_obj_valid(self):
    #     """all header valid =0"""
    #     cache_objs = self.cache.get("OBJECTS", {})
    #     if cache_objs:
    #         for _, v in cache_objs.items():
    #             v.update({"VALID": 0})

    # def cache_refresh_hdr_valid(self):
    #     """all header valid =0"""
    #     cache_hdrs = self.cache.get("HEADERS", {})
    #     if cache_hdrs:
    #         for _, v in cache_hdrs.items():
    #             v.update({"VALID": 0})

    # def __compare_obj(self):
    #     """compare cache  new cache"""
    #     # log.error(f"__compare :  ")
    #     cache_objs = self.cache.get("OBJECTS", {})
    #     new_cache_objs = self.new_cache.get("OBJECTS", {})

    #     # all cache src valid =0

    #     # compare
    #     for k, v in new_cache_objs.items():
    #         # log.info(f"k: {k}  v: {v}")
    #         if k not in cache_objs:
    #             cache_objs.update({k: v})
    #             continue
    #         if v.get("TIMESTAMP") != cache_objs[k].get("TIMESTAMP"):
    #             cache_objs[k].update({"VALID": 1})
    #             continue
    #         if v.get("tool") != cache_objs[k].get("tool"):
    #             cache_objs[k].update({"VALID": 1})
    #             continue
    #         if v.get("toolflag") != cache_objs[k].get("toolflag"):
    #             cache_objs[k].update({"VALID": 1})
    #             continue
    #         if v.get("define") != cache_objs[k].get("define"):
    #             cache_objs[k].update({"VALID": 1})
    #             continue
    #         if v.get("include_macro") != cache_objs[k].get("include_macro"):
    #             cache_objs[k].update({"VALID": 1})
    #             continue
    #     pass

    # def _deal_obejcts_by_src_cmd(self, cmd: dict[str:Any]) -> None:
    #     # log.error(f"cmd {cmd}")
    #     src = cmd["src"][0]
    #     new_tm_stamp = self._get_timestamp(src)
    #     if new_tm_stamp == 0:
    #         log.error(f"src file {src} not found")
    #         return

    #     if src not in self.cache:
    #         self._object_from_cmd_to_cache(cmd, src, new_tm_stamp)
    #         return

    #     # compare timestamp  flags, if  equal, then modify cmd["VALID"] = 0
    #     if new_tm_stamp == self.cache[src]["TIMESTAMP"]:
    #         cmd["VALID"] = 0
    #         return
    #     if not self._compare_cmd_cache_by_src(cmd, src):
    #         cmd["VALID"] = 0
    #         return
    #     self._object_from_cmd_to_cache(cmd, src, new_tm_stamp)

    # def _deal_targets_by_obj_cmd(self, cmd_dct: dict[str:Any]) -> None:
    #     # log.error(f"cmd_dct  2 {cmd_dct}")
    #     target = cmd_dct["obj"][0]
    #     # lib target
    #     if target not in self.cache:
    #         self._target_from_cmd_to_cache(cmd_dct, target, 0)
    #         return

    # def _deal_actions_by_cmd(self, cmd_dct: dict[str:Any]) -> None:
    #     # 替代
    #     log.error(f"_deal_actions_by_cmd  2 {cmd_dct}")
    #     # cmd_dct["obj"][0]
    #     # # lib target
    #     # if target not in self.cache:
    #     #     self._target_from_cmd_to_cache(cmd_dct, target, 0)
    #     #     return

    # def run(self):
    #     """
    #     {'TOOL': 'gcc',
    #     'FLAGS': ['-mcpu=cortex-m4', '-mfpu=fpv4-sp-d16', '-mfloat-abi=softfp', '-mthumb', '-O0'],
    #     'DEFINES': ['-DXXXX=123'],
    #     'INCS': ['-Isrc\\cmsis\\core', '-Isrc\\hal\\inc'],
    #     'SRC': ['-c', 'src\\app\\src\\main.c'],
    #     'TARGET': 'BUILD\\OBJ\\SRC\\main.o',
    #     'SUFF': '.c',
    #     'VALID': 1}
    #     lib  suff
    #     link
    #     """
    #     for cmd in self.commands:
    #         if not cmd.get("SUFF", []):
    #             log.error(f"cmd {cmd} suff is empty")
    #             continue
    #         if cmd.get("SUFF", []) in SOURCE_EXTS:
    #             self._deal_cmd_item_obj(cmd)
    #             continue
    #         self._deal_cmd_item_target(cmd)
    #         self._save(self.track_fpath)

    # def __format_lst_2_str(self, lst: list[str]) -> str:
    #     if not lst:
    #         return ""
    #     return " ".join(lst)

    # def _object_from_cmd_to_cache(self, cmd: dict, key: str, tm_stamp: int) -> None:
    #     ret = {key: {}}
    #     if "OBJECTS" not in self.cache:
    #         self.new_cache["OBJECTS"] = {}
    #     ret[key].update({"tool": self.__format_lst_2_str(cmd.get("tool"))})
    #     ret[key].update({"toolflag": self.__format_lst_2_str(cmd.get("toolflag"))})
    #     if cmd.get("define", []):
    #         ret[key].update({"define": self.__format_lst_2_str(cmd.get("define", []))})
    #     if cmd.get("include_macro", []):
    #         ret[key].update(
    #             {"include_macro": self.__format_lst_2_str(cmd.get("include_macro", []))}
    #         )
    #     if cmd.get("inc_flag", []):
    #         ret[key].update({"inc_flag": self.__format_lst_2_str(cmd.get("inc_flag", []))})
    #     if cmd.get("obj"):
    #         ret[key].update({"obj": self.__format_lst_2_str(cmd.get("obj"))})
    #     if cmd.get("_o"):
    #         ret[key].update({"_o": self.__format_lst_2_str(cmd.get("_o"))})
    #     if cmd.get("src"):
    #         ret[key].update({"src": self.__format_lst_2_str(cmd.get("src"))})

    #     ret[key].update({"TIMESTAMP": tm_stamp})
    #     self.new_cache["OBJECTS"].update(ret)

    # def _target_from_cmd_to_cache(self, cmd: dict, key: str, tm_stamp: int) -> None:
    #     ret = {key: {}}
    #     if "TARGETS" not in self.cache:
    #         self.new_cache["TARGETS"] = {}
    #     ret[key].update({"tool": self.__format_lst_2_str(cmd.get("tool"))})
    #     ret[key].update({"toolflag": self.__format_lst_2_str(cmd.get("toolflag"))})

    #     if cmd.get("obj"):
    #         ret[key].update({"obj": self.__format_lst_2_str(cmd.get("obj"))})
    #     if cmd.get("_o"):
    #         ret[key].update({"_o": self.__format_lst_2_str(cmd.get("_o"))})
    #     if cmd.get("src"):
    #         ret[key].update({"src": self.__format_lst_2_str(cmd.get("src"))})
    #     if cmd.get("LIB"):
    #         ret[key].update({"LIB": self.__format_lst_2_str(cmd.get("LIB"))})
    #     if cmd.get("LIBPATH"):
    #         ret[key].update({"LIBPATH": self.__format_lst_2_str(cmd.get("LIBPATH"))})
    #     if cmd.get("SUFF"):
    #         ret[key].update({"SUFF": self.__format_lst_2_str(cmd.get("SUFF"))})

    #     ret[key].update({"TIMESTAMP": tm_stamp})
    #     self.new_cache["TARGETS"].update(ret)

    # def _action_from_cmd_to_cache(self, cmd: dict, key: str, tm_stamp: int) -> None:
    #     ret = {key: {}}
    #     if "ACTIONS" not in self.cache:
    #         self.new_cache["ACTIONS"] = {}

    #     self.new_cache["ACTIONS"].update(ret)

    # def _item_from_cmd_to_cache(self, cmd: dict, key: str, tm_stamp: int) -> None:
    #     ret = {key: {}}
    #     ret[key].update({"tool": cmd.get("tool")})
    #     ret[key].update({"toolflag": cmd.get("toolflag")})
    #     if cmd.get("define_macro", []):
    #         ret[key].update({"define_macro": cmd.get("define_macro", [])})
    #     if cmd.get("include_macro", []):
    #         ret[key].update({"include_macro": cmd.get("include_macro", [])})
    #     if cmd.get("inc_flag", []):
    #         ret[key].update({"inc_flag": cmd.get("inc_flag", [])})
    #     if cmd.get("obj"):
    #         ret[key].update({"obj": cmd.get("obj")})
    #     if cmd.get("_o"):
    #         ret[key].update({"_o": cmd.get("_o")})
    #     if cmd.get("src"):
    #         ret[key].update({"src": cmd.get("src")})
    #     if cmd.get("LIB"):
    #         ret[key].update({"LIB": cmd.get("LIB")})
    #     if cmd.get("LIBPATH"):
    #         ret[key].update({"LIBPATH": cmd.get("LIBPATH")})
    #     if cmd.get("SUFF"):
    #         ret[key].update({"SUFF": cmd.get("SUFF")})

    #     ret[key].update({"TIMESTAMP": tm_stamp})
    #     self.cache.update(ret)
