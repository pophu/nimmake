# 快捷导入：常用预设配置和快速构建函数
# from ...flags import presets as flashes
from .HALDrivers import HALDrivers
from .MyParties import MyParties
from .ThirdParty import CommonDir, DefaultParty, GenericParty, ThirdParty

# PARTIES_DCT: dict[str, str] = {
#     "GENERIC": "GenericParty",
#     "COMMON": "CommonDir",
# }


__all__ = [
    "CommonDir",
    "GenericParty",
    "ThirdParty",
    "HALDrivers",
    "DefaultParty",
]
