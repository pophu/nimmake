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
gather — srcs / headers / include_dirs gatherer
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from nimmake.configs import HEADER_EXTS, SOURCE_EXTS

# ---------------------------------------------------------------------------
# 默认扩展名集合
# ---------------------------------------------------------------------------

# SOURCE_EXTS: set[str] = {".c", ".cpp", ".cxx", ".cc", ".c++", ".s", ".S", ".asm"}
# HEADER_EXTS: set[str] = {".h", ".hpp", ".hxx", ".hh", ".inc"}


# ---------------------------------------------------------------------------
# 结果数据类
# ---------------------------------------------------------------------------


@dataclass
class GatherResult:
    """收集结果"""

    sources: list[Path] = field(default_factory=list)
    headers: list[Path] = field(default_factory=list)
    include_dirs: list[Path] = field(default_factory=list)

    @property
    def source_count(self) -> int:
        return len(self.sources)

    @property
    def header_count(self) -> int:
        return len(self.headers)

    def __str__(self) -> str:
        return (
            f"GatherResult(sources={self.source_count}, "
            f"headers={self.header_count}, "
            f"include_dirs={len(self.include_dirs)})"
        )


# ---------------------------------------------------------------------------
# 核心类
# ---------------------------------------------------------------------------


class FileGatherer:
    """源文件 / 头文件收集器。

    将扫描配置固化在实例中，避免每次调用重复传参。

    Args:
        source_exts: 源文件扩展名集合
        header_exts: 头文件扩展名集合
        exclude_dirs: 默认排除的子目录（相对根目录）
        exclude_prefixes: 默认排除的文件名前缀
        exclude_suffixes: 默认排除的文件名后缀 如 copy means exclude *copy.c ,*copy ,*copy.cpp
        recursive: 是否递归子目录
        relative: 是否返回相对路径（默认 False 返回绝对路径）
    """

    def __init__(
        self,
        *,
        source_exts: set[str] | None = None,
        header_exts: set[str] | None = None,
        exclude_dirs: list[str | Path] | None = None,
        exclude_prefixes: list[str] | None = None,
        exclude_suffixes: list[str] | None = None,
        recursive: bool = True,
        relative: bool = False,
    ):
        self.source_exts = source_exts or SOURCE_EXTS
        self.header_exts = header_exts or HEADER_EXTS
        self.exclude_dirs = exclude_dirs or []
        self.exclude_prefixes = exclude_prefixes or []
        self.exclude_suffixes = exclude_suffixes or []
        self.recursive = recursive
        self.relative = relative

    # ------------------------------------------------------------------
    # 链式设置接口
    # ------------------------------------------------------------------

    def set_source_exts(self, exts: set[str]) -> FileGatherer:
        """设置源文件扩展名"""
        self.source_exts = set(exts)
        return self

    def set_header_exts(self, exts: set[str]) -> FileGatherer:
        """设置头文件扩展名"""
        self.header_exts = set(exts)
        return self

    def set_exclude_dirs(self, *dirs: str | Path) -> FileGatherer:
        """设置排除目录（覆盖）"""
        self.exclude_dirs = list(dirs)
        return self

    def add_exclude_dirs(self, *dirs: str | Path) -> FileGatherer:
        """追加排除目录"""
        for d in dirs:
            if d not in self.exclude_dirs:
                self.exclude_dirs.append(d)
        return self

    def set_exclude_prefixes(self, *prefixes: str) -> FileGatherer:
        """设置排除文件名前缀（覆盖）"""
        self.exclude_prefixes = list(prefixes)
        return self

    def add_exclude_prefixes(self, *prefixes: str) -> FileGatherer:
        """追加排除文件名前缀"""
        for p in prefixes:
            if p not in self.exclude_prefixes:
                self.exclude_prefixes.append(p)
        return self

    def set_exclude_suffixes(self, *suffixes: str) -> FileGatherer:
        """设置排除文件名后缀（覆盖）"""
        self.exclude_suffixes = list(suffixes)
        return self

    def add_exclude_suffixes(self, *suffixes: str) -> FileGatherer:
        """追加排除文件名后缀"""
        for s in suffixes:
            if s not in self.exclude_suffixes:
                self.exclude_suffixes.append(s)
        return self

    def set_recursive(self, recursive: bool) -> FileGatherer:
        """设置是否递归子目录"""
        self.recursive = recursive
        return self

    def set_relative(self, relative: bool) -> FileGatherer:
        """设置是否返回相对路径"""
        self.relative = relative
        return self

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------

    @staticmethod
    def _norm(p: str | Path) -> Path:
        return Path(p).resolve()

    def _is_excluded(self, path: Path, root: Path) -> bool:
        """检查路径是否在排除目录中"""
        if not self.exclude_dirs:
            return False
        try:
            rel = path.relative_to(root)
        except ValueError:
            return False
        for ed in self.exclude_dirs:
            ed_path = Path(ed)
            if rel == ed_path or rel.parts[: len(ed_path.parts)] == ed_path.parts:
                return True
        return False

    def _scan(
        self,
        root: Path,
        exts: set[str],
        include_dirs: list[str | Path] | None = None,
    ) -> list[Path]:
        """扫描目录，返回匹配扩展名的文件列表"""
        origin_root = root
        root = self._norm(root)
        scan_roots: list[Path] = []
        if include_dirs:
            for d in include_dirs:
                full = root / d
                if full.is_dir():
                    scan_roots.append(full)
        else:
            scan_roots.append(root)

        result: list[Path] = []
        pattern = "**/*" if self.recursive else "*"

        hide = set(self.exclude_prefixes)
        # hide_suff = set(self.exclude_suffixes)

        for sr in scan_roots:
            for fp in sr.glob(pattern):
                # log.error(f"    ====fp: {fp.name}  [{fp.stem}]  ")
                # if fp.name.endswith(".c"):
                #     log.error(f"    ====fp: {fp}   [{fp.stem}]  ")
                if not fp.is_file():
                    continue
                if fp.suffix.lower() not in exts:
                    continue
                if hide and any(fp.name.startswith(p) for p in hide):
                    continue
                # fp.name or fp.stem
                if self.exclude_suffixes:
                    name = fp.stem
                    if any(
                        name.endswith(s) or name.endswith("." + s) for s in self.exclude_suffixes
                    ):
                        continue
                if self._is_excluded(fp, root):
                    continue
                result.append(fp)

        sorted_result = sorted(result)

        if self.relative:
            return [origin_root / fp.relative_to(root) for fp in sorted_result]
        # ADD ROOT TO RESULT
        return sorted_result

    # ------------------------------------------------------------------
    # 公开方法
    # ------------------------------------------------------------------

    def sources(
        self,
        root: str | Path,
        *,
        include_dirs: list[str | Path] | None = None,
        exclude_dirs: list[str | Path] | None = None,
        exclude_prefixes: list[str] | None = None,
        exclude_suffixes: list[str] | None = None,
        exts: set[str] | None = None,
        recursive: bool | None = None,
    ) -> list[Path]:
        """收集源文件。

        Args:
            root: 项目根目录
            include_dirs: 限定子目录（相对 root）
            exclude_dirs: 临时排除子目录（与实例配置合并）
            exclude_prefixes: 临时排除文件名前缀
            exts: 临时覆盖源文件扩展名
            recursive: 临时覆盖是否递归

        Returns:
            源文件 Path 列表
        """
        # log.error(f"GATHER sources: {exclude_dirs}")
        merged_exts = exts or self.source_exts
        merged_exclude = _merge_lists(self.exclude_dirs, exclude_dirs)
        merged_prefix = _merge_lists(self.exclude_prefixes, exclude_prefixes)
        merged_suffix = _merge_lists(self.exclude_suffixes, exclude_suffixes)
        is_rec = recursive if recursive is not None else self.recursive

        return self._scan_ext(
            Path(root),
            merged_exts,
            merged_exclude,
            merged_prefix,
            merged_suffix,
            include_dirs,
            is_rec,
        )

    def headers(
        self,
        root: str | Path,
        *,
        include_dirs: list[str | Path] | None = None,
        exclude_dirs: list[str | Path] | None = None,
        exclude_prefixes: list[str] | None = None,
        exclude_suffixes: list[str] | None = None,
        exts: set[str] | None = None,
        recursive: bool | None = None,
    ) -> list[Path]:
        """收集头文件。"""
        merged_exts = exts or self.header_exts
        merged_exclude = _merge_lists(self.exclude_dirs, exclude_dirs)
        merged_prefix = _merge_lists(self.exclude_prefixes, exclude_prefixes)
        merged_suffix = _merge_lists(self.exclude_suffixes, exclude_suffixes)
        is_rec = recursive if recursive is not None else self.recursive

        return self._scan_ext(
            Path(root),
            merged_exts,
            merged_exclude,
            merged_prefix,
            merged_suffix,
            include_dirs,
            is_rec,
        )

    def _scan_ext(
        self,
        root: Path,
        exts: set[str],
        exclude_dirs: list[str | Path],
        exclude_prefixes: list[str],
        exclude_suffixes: list[str],
        include_dirs: list[str | Path] | None,
        recursive: bool,
    ) -> list[Path]:
        """带临时参数的单次扫描"""
        # 用临时配置创建子扫描器
        sub = FileGatherer(
            source_exts=exts,
            header_exts=exts,
            exclude_dirs=exclude_dirs,
            exclude_prefixes=exclude_prefixes,
            exclude_suffixes=exclude_suffixes,
            recursive=recursive,
            relative=self.relative,
        )
        return sub._scan(root, exts, include_dirs)

    def include_dirs(
        self,
        root: str | Path,
        *,
        include_dirs: list[str | Path] | None = None,
        exclude_dirs: list[str | Path] | None = None,
        exclude_prefixes: list[str] | None = None,
        exts: set[str] | None = None,
        recursive: bool | None = None,
    ) -> list[Path]:
        """收集头文件所在目录（即 -I 参数列表）。"""
        hdrs = self.headers(
            Path(root),
            include_dirs=include_dirs,
            exclude_dirs=exclude_dirs,
            exclude_prefixes=exclude_prefixes,
            exts=exts,
            recursive=recursive,
        )
        return sorted({h.parent for h in hdrs})

    def all(
        self,
        root: str | Path,
        *,
        include_dirs: list[str | Path] | None = None,
        exclude_dirs: list[str | Path] | None = None,
        exclude_prefixes: list[str] | None = None,
        source_exts: set[str] | None = None,
        header_exts: set[str] | None = None,
        recursive: bool | None = None,
    ) -> GatherResult:
        """一次调用同时收集源文件、头文件、头文件目录。

        Returns:
            GatherResult
        """
        srcs = self.sources(
            Path(root),
            include_dirs=include_dirs,
            exclude_dirs=exclude_dirs,
            exclude_prefixes=exclude_prefixes,
            exts=source_exts,
            recursive=recursive,
        )
        hdrs = self.headers(
            Path(root),
            include_dirs=include_dirs,
            exclude_dirs=exclude_dirs,
            exclude_prefixes=exclude_prefixes,
            exts=header_exts,
            recursive=recursive,
        )
        incs = sorted({h.parent for h in hdrs})
        return GatherResult(sources=srcs, headers=hdrs, include_dirs=incs)


# ---------------------------------------------------------------------------
# 工具
# ---------------------------------------------------------------------------


def _merge_lists(base: list, override: list | None) -> list:
    """合并实例配置和 per-call 参数"""
    if override is None:
        return list(base)
    seen = set(base)
    result = list(base)
    for item in override:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def format_include_flags(include_dirs: list[str | Path], prefix: str = "-I") -> list[str]:
    """将目录列表格式化为编译器 -I 参数"""
    return [f"{prefix}{str(d)}" for d in include_dirs]
