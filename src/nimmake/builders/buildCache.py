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

"""BuildCache
buildCache — Build cache for incremental builds.

Supports loading historical data to check if a build is necessary.
"""

import hashlib
import os
import shlex
import time
from pathlib import Path

from nimmake.utils import ContainSafe, log


class BuildCache:
    """
    referto   .ninja_log adn .ninja_deps 。
    支持加载历史数据，实现跨次构建的增量判断。
    """

    def __init__(
        self,
        log_dict: dict[str, dict] = None,
        deps_dict: dict[str, dict] = None,
        hdr_check: bool = True,
        updated_hdrs: ContainSafe | None = None,
    ):
        # 内存字典，用于承载历史构建状态
        self.log_dict: dict[str, dict] = log_dict or {}
        self.deps_dict: dict[str, dict] = deps_dict or {}
        self.headers_tm: dict[str, float] = {}
        self.headers_unchanged: set[str] = set()
        self.hdrs_unchanged: ContainSafe = updated_hdrs or ContainSafe()
        self.hdr_check = hdr_check  # check hdr time change

    def set_log_cache(self, log_dict: dict[str, dict]):
        self.log_dict = log_dict

    def set_deps_cache(self, deps_dict: dict[str, dict]):
        self.deps_dict = deps_dict

    def _compute_command_hash(self, command: str) -> str:
        """计算构建命令的确定性哈希"""
        # log.debug(f"  >> Computing hash for command: {command}")
        tokens = sorted(shlex.split(command))
        hash_input = " ".join(tokens)
        return hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

    def should_rebuild(self, output: str, command: str, deps: list[str]) -> int:
        """
        params:
        output: obj *.o
        command: flags
        deps: list[str] [src gdr]
        RETURN:
            0: 无需重建
            1: 未构建过
            2: 命令变更
            3: 依赖变更
            4: 输出文件不存在
            5: 依赖文件变更
            6: 依赖文件不存在
        """
        # log.error(f"should_rebuild  tracke  {output} ")
        current_hash = self._compute_command_hash(command)
        old_log = self.log_dict.get(output, {})
        old_deps = self.deps_dict.get(output)
        old_tm = old_log.get("mtime", 0.0)
        # log.debug(f"should_rebuild  tracke  {output}   ")
        # log.warn(f" {command}  ")
        # log.warn(f"newhash {current_hash}  ")
        # log.warn(f"oldhash {old_log.get('hash', '')}  ")
        # log.warn(
        #     f" should_rebuild >> {output} {command} {deps} old_log: {old_log} old_deps: {old_deps}"
        # )

        if old_log is None:
            # log.debug(f"  [MISSING] {output} 从未构建过")
            return 1

        if old_log.get("hash", "") != current_hash:
            # log.debug(f"  [CMD_CHANGED] {output} 命令已变更 ")
            # log.debug(f"   {old_log.get('hash', '')}")
            # log.debug(f"   {current_hash}")
            return 2

        if old_deps is None or old_deps.get("hash", "") != current_hash:
            # log.debug(f"  [DEPS_MISSING] {output} 依赖记录缺失")
            return 3

        stored_deps = old_deps.get("deps", [])
        # log.warn(f" {output} T={os.path.getmtime(output)} ,tm from cache= {old_tm}")
        try:
            output_mtime = os.path.getmtime(output)
        except OSError:
            log.debug(f"  [MISSING] {output} 文件不存在")
            return 4

        # dep include the source file
        # # log.debug(f" {output_mtime - old_tm}")
        # if output_mtime < old_tm:
        #     log.debug("mtime updated")
        #     return 5

        log.debug(f"hdr_check -> T={self.hdr_check}")
        # log.warn(f"stored_deps -> T={stored_deps}")

        if not self.hdr_check:
            return 0

        for dep in stored_deps:
            # log.debug(f" output_mtime={output_mtime}, dep {dep}  {os.path.getmtime(dep)}")
            if dep in self.hdrs_unchanged:
                continue
            try:
                if os.path.getmtime(dep) >= output_mtime:  # hdr time > obj time
                    # log.debug(f"  [DEP_UPDATED] {dep} 比 {output} 新")
                    return 6
            except OSError:
                # log.debug(f"  [DEP_MISSING] {dep} 依赖文件不存在")
                return 7
            self.hdrs_unchanged.add(dep)

        # log.debug(f"  [UP_TO_DATE] {output} 已是最新，跳过")
        return 0

    def record_build(self, output: str, command: str, deps: list[str], src: str = None):
        """构建成功后，更新内存字典"""
        current_hash = self._compute_command_hash(command)
        # log.debug(f"  >> Recording build: {current_hash} {command}  ")
        self.log_dict[output] = {
            "command": command,
            "src": src,
            "hash": current_hash,
            "mtime": time.time(),  # need to update , so mtime is now
            "valid": 1,
        }
        self.deps_dict[output] = {
            "hash": current_hash,
            "deps": sorted(deps),
        }

    def clean(self):
        """清空历史数据"""
        self.log_dict.clear()
        self.deps_dict.clear()


if __name__ == "__main__":
    # 1. 准备测试文件
    test_dir = Path(".ninja_demo")
    test_dir.mkdir(exist_ok=True)
    src = str(test_dir / "main.c")
    hdr = str(test_dir / "utils.h")
    obj = str(test_dir / "main.o")

    Path(src).write_text("int main() { return 0; }")
    Path(hdr).write_text("#define VERSION 1")
    Path(obj).write_text("fake binary")
    time.sleep(0.05)  # 确保 mtime 有区分度

    print("=" * 60)
    print("【第1次构建】首次运行，缓存为空")
    print("=" * 60)
    cache = BuildCache()
    # 此时 log_dict 和 deps_dict 都是空字典 {}
    print(f"  构建前 log_dict: {cache.log_dict}")
    print(f"  构建前 deps_dict: {cache.deps_dict}")

    need = cache.should_rebuild(obj, "gcc -O2 -o main.o main.c", [src, hdr])
    assert need is True, "首次构建必须重建"
    cache.record_build(obj, "gcc -O2 -o main.o main.c", [src, hdr])

    print(f"  构建后 log_dict: {cache.log_dict}")
    print(f"  构建后 deps_dict: {cache.deps_dict}")
    print("  ✅ 历史数据已写入内存字典\n")

"""
pickle 

object:  参考 ninjialog
15	547	8065814410929564	hal/src/uart.o	1de45c58174ed9e3
29	548	8065814411065446	app/src/main.o	81e10db807c3cfdf
1	548	8065814410729960	hal/src/spi.o	1e0a7df724271780
549	1122	8065814416273905	firmware.elf	d3f743f452aa1515
1 目标ID 整数,构建目标在构建图中的唯一标识符,快速索引和管理构建依赖关系
2 依赖文件数量整数,目标文件所依赖的文件总数,评估构建复杂度和资源需求
3 文件修改时间戳,纳 秒 级 时间戳,目标文件的最后修改时间
4 目标文件路径字符串 构建生成的最终文件路径
5 命令哈希值哈 希 字 符串,构 建 命 令 的 哈 希 值 （ 如SHA-1）检测构建命令参数变化
{
    "OBJECTS": { *.o :[src , stamp(last) hash] },
    "LIBS": { *.a :[[.o] , stamp(last) hash] },  libs 也可以合并到 OBJECTS 中， 触发命令后安装库比较麻烦了
    "CMD": "gcc -O2 -o main.o main.c",
    "DEPS":{ *.0: [src, hdr]},
}

以上存入缓存， 如果以上.o 时间戳 与对应源文件时间戳比较， 源时间戳大，存源时间戳

正式编译， .o 本身时间戳  与对应列表中源时间戳比较，判断是否需要重建
"""
