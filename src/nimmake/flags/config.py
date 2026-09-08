"""
FlagsConfig — 编译标志配置数据类

支持:
  - 与普通关键字参数互转（to_dict / from_dict）
  - JSON / YAML 序列化后可直接重建
  - 直接传入 FlagsFactory
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class FlagsConfig:
    """FlagsFactory 的全部配置参数"""

    # ---- 工具 ----
    toolchain: str = ""

    # ---- 目标 ----
    cpu: str = ""
    arch: str = ""
    fpu: str = ""  # none, fpv4-sp-d16, fpv5-d16 ,neon-vfpv4 ..
    abi: str = ""  # hard, softfp soft
    thumb: str = ""
    model: list[str] | str = ""
    vendor: list[str] | str = ""

    # ---- 编译 ----
    opt: str = "O0"
    dbg: bool = False
    warn: str = ""
    std_c: str = ""
    std_cxx: str = ""
    data_sections: str = ""
    func_sections: str = ""
    freestanding: bool = False
    no_builtin: bool = (False,)

    # ---- 宏 ----
    defines: dict[str, str] = field(default_factory=dict)

    # cxx flag
    no_rtti: bool = False
    no_exceptions: bool = False

    # ---- 链接 ----
    ld_path: str = ""
    linkscript: str = ""
    mmap: str = ""
    gc_sections: bool = False
    nostartfiles: bool = False
    nostdlib: bool = False
    shared: bool = False
    library_path: str = ""
    specs: str = ""
    lto: str = ""
    semihost: bool = False
    sysroot: str = ""

    def to_dict(self) -> dict[str, object]:
        """转为普通字典（可用于 JSON / YAML 序列化）"""
        d = asdict(self)
        # 清理空值方便可视化
        return d

    def to_json(self) -> str:
        """转为 JSON 字符串"""
        import json

        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def to_kwargs(self, toolchain: str = "") -> dict[str, object]:
        """转为 FlagsFactory 的关键字参数（不含 toolchain）"""
        d = self.to_dict()
        d.pop("model", None)
        return d

    @staticmethod
    def from_dict(d: dict[str, object]) -> FlagsConfig:
        """从字典重建（可用 JSON.load 后传入）"""
        valid_keys = {f.name for f in __import__("dataclasses").fields(FlagsConfig)}
        filtered = {k: v for k, v in d.items() if k in valid_keys}
        return FlagsConfig(**filtered)

    @staticmethod
    def from_json(s: str) -> FlagsConfig:
        """从 JSON 字符串重建"""
        import json

        return FlagsConfig.from_dict(json.loads(s))

    def clone(self) -> FlagsConfig:
        """深拷贝"""
        return FlagsConfig.from_dict(self.to_dict())

    def __repr__(self) -> str:
        items = []
        for k, v in asdict(self).items():
            if v is not None and v != "" and v != [] and v != {} and v is not False:
                items.append(f"{k}={v!r}")
        return f"FlagsConfig({', '.join(items)})"

    def set(self, field_name: str, value: object) -> FlagsConfig:
        """
        设置指定字段的值

        Args:
            field_name: 字段名称，如 'cpu', 'opt', 'dbg' 等
            value: 要设置的值

        Returns:
            self (支持链式调用)

        Raises:
            AttributeError: 字段不存在时抛出
            TypeError: 值类型不匹配时抛出
        """
        if not hasattr(self, field_name):
            raise AttributeError(f"FlagsConfig 无此字段: {field_name}")

        current_value = getattr(self, field_name)
        expected_type = type(current_value) if current_value is not None else type(value)

        if value is not None and current_value is not None:
            if not isinstance(value, expected_type):
                try:
                    value = expected_type(value)
                except (ValueError, TypeError):
                    pass

        setattr(self, field_name, value)
        return self
