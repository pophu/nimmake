"""
flags — 编译工具链标志工厂

快速按工具链 / 芯片架构 / 厂商型号生成:
  cflags / cxxflags / asflags / arflags / ldflags / defines

用法:
    from flags import FlagsFactory, FlagsConfig

    # 方式一：直接传参
    f = FlagsFactory("armgcc", cpu="cortex-m4", opt="O2")
    f.cflags   # ["-mcpu=cortex-m4", "-mthumb", "-O2", ...]

    # 方式二：通过配置对象
    cfg = FlagsConfig(cpu="cortex-m4", opt="O2", linkscript="stm32f4.ld")
    f = FlagsFactory.from_config("armgcc", cfg)

    # 配置对象 ↔ 字典互转（可用于 JSON/YAML）
    d = cfg.to_dict()
    cfg2 = FlagsConfig.from_dict(d)
"""

# 快捷导入：常用预设配置和快速构建函数
# from ...flags import presets as flashes
# from .chips import chip_by_model, chips_by_vendor, cpu_arch, vendor_of_model
from .config import FlagsConfig

# from .factory import FlagsFactory, new_flags
from .flags import Flags

__all__ = [
    # "FlagsFactory",
    # "new_flags",
    "Flags",
    "FlagsConfig",
    # "chip_by_model",
    # "cpu_arch",
    # "chips_by_vendor",
    # "vendor_of_model",
    # "flashes",
]
