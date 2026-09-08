"""
Flags — 编译标志数据类
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


def fmt_define(key: str, value: str = "") -> str:
    """将宏定义转为命令行参数"""
    return f"-D{key}={value}" if value else f"-D{key}"


@dataclass
class Flags:
    """一组完整的编译标志"""

    cflags: List[str] = field(default_factory=list)
    cxxflags: List[str] = field(default_factory=list)
    asflags: List[str] = field(default_factory=list)
    arflags: List[str] = field(default_factory=list)
    defines: Dict[str, str] = field(default_factory=dict)
    ldflags: List[str] = field(default_factory=list)

    @property
    def all(self) -> Dict[str, object]:
        return {
            "cflags": self.cflags,
            "cxxflags": self.cxxflags,
            "asflags": self.asflags,
            "arflags": self.arflags,
            "defines": self.defines,
            "ldflags": self.ldflags,
        }

    def __str__(self) -> str:
        lines = []
        for k, v in self.all.items():
            if isinstance(v, dict):
                parts = " ".join(
                    fmt_define(kk, vv) for kk, vv in v.items()
                )
            else:
                parts = " ".join(v)
            lines.append(f"  {k:10s}: {parts}")
        return "\n".join(lines)
