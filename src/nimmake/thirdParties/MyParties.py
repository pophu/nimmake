import copy
import json
import sys
from pathlib import Path
from typing import Any

from ..configs import (
    EXCLUDE_DIRS,
    EXCLUDE_PREFIXES,
    EXCLUDE_SUFFIXES,
    HEADER_EXTS,
    SOURCE_EXTS,
    TASK_GRPAPH_HEADER,
    BuildType,
)
from .FatFS import FatFS
from .FreeRTOS import FreeRTOS
from .HALDrivers import HALDrivers
from .LVGL import LVGL
from .ThirdParty import CommonDir, DefaultParty, GenericParty

PARTIES_DCT: dict[str, str] = {
    "GENERIC": GenericParty,
    "_DEFAULT": DefaultParty,
    "COMMON": CommonDir,
    "HAL": HALDrivers,
    "FATFS": FatFS,
    "FREERTOS": FreeRTOS,
    "LVGL": LVGL,
}


class MyParties:
    pass


class MyParties:
    """params"""

    def __init__(
        self,
        name: str,
        root: str | Path,
        source_exts: set[str] = None,
        header_exts: set[str] = None,
        exclude_dirs: list[str] = None,
        exclude_prefixes: list[str] = None,
        exclude_suffixes: list[str] = None,
        recursive: bool = True,
        defines: dict[str, str] = None,
        # macros: list[str] = None,
        # global_macros: list[str] = None,
        include_macros: dict[str, str] = None,
        depends: list[str] = None,
        build_type: str = BuildType.OBJECT.name,
        relative: bool = True,
        params: dict[str, Any] = None,
        third_party: str = "",
        **kwargs,
    ):
        dict(kwargs.items())
        self.typ = "PARTIES"
        self.name = name
        # self.root = Path(root)
        self.root = root
        self._build_type = build_type
        self.source_exts = copy.deepcopy(source_exts) if source_exts else copy.deepcopy(SOURCE_EXTS)
        self.header_exts = copy.deepcopy(header_exts) if header_exts else copy.deepcopy(HEADER_EXTS)
        self.exclude_dirs = (
            copy.deepcopy(exclude_dirs) if exclude_dirs else copy.deepcopy(EXCLUDE_DIRS)
        )
        self.exclude_prefixes = (
            copy.deepcopy(exclude_prefixes) if exclude_prefixes else copy.deepcopy(EXCLUDE_PREFIXES)
        )
        self.exclude_suffixes = (
            copy.deepcopy(exclude_suffixes) if exclude_suffixes else copy.deepcopy(EXCLUDE_SUFFIXES)
        )
        self.depends = copy.deepcopy(depends) if depends else []
        self.recursive = recursive
        self.third_party = third_party

        self.defines = copy.deepcopy(defines or {})
        # log.debug(f"myparty self.defines: {defines}")
        # self.macros = copy.deepcopy(macros or {})
        # self.defines_g = copy.deepcopy(global_macros or {})
        self.include_macros = copy.deepcopy(include_macros or {})
        self.params = copy.deepcopy(params or {})
        self.recursive = recursive
        self.relative = relative

        # if not third_party:
        #     third_party = "GENERIC"
        # if third_party not in PARTIES_DCT.keys():
        #     log.error(f"third_party [{third_party}] not in PARTIES_DCT")
        # party_cls = PARTIES_DCT.get(third_party, GenericParty)
        # self.handler = party_cls(
        #     name=self.name,
        #     root=self.root,
        #     source_exts=self.source_exts,
        #     header_exts=self.header_exts,
        #     exclude_dirs=self.exclude_dirs,
        #     exclude_prefixes=self.exclude_prefixes,
        #     exclude_suffixes=self.exclude_suffixes,
        #     defines=self.defines,
        #     # macros=self.macros,
        #     # defines_g=self.defines_g,
        #     include_macros=self.include_macros,
        #     depends=self.depends,
        #     build_type=self._build_type,
        #     recursive=self.recursive,
        #     relative=self.relative,
        #     params=self.params,
        # )
        # return self.party_handler

    def Dictionary(self) -> dict[str, Any]:
        dct = {}
        dct.update(
            {
                "name": self.name,
                "root": str(self.root),
                "source_exts": list(self.source_exts),
                "header_exts": list(self.header_exts),
                "exclude_dirs": list(self.exclude_dirs),
                "exclude_prefixes": list(self.exclude_prefixes),
                "exclude_suffixes": list(self.exclude_suffixes),
                "defines": self.defines,
                # "macros": self.macros,
                # "defines_g": self.defines_g,
                "include_macros": self.include_macros,
                "depends": self.depends,
                "build_type": self._build_type,
                "recursive": self.recursive,
                "relative": self.relative,
                "params": self.params,
                "third_party": self.third_party,
                "typ": self.typ,
            }
        )
        return dct

    def Dump(self) -> None:
        return json.dumps(self.Dictionary())

    def DependOn(self, party: str | MyParties | list[str] | list[MyParties] = None) -> list[str]:
        if party is None:
            return self
        if isinstance(party, MyParties):
            self.depends.append(party.name)
        if isinstance(party, list):
            # self.depends.append(party.name)
            for _p in party:
                if isinstance(_p, str):
                    self.depends.append(_p)
                if isinstance(_p, MyParties):
                    self.depends.append(_p.name)
        dct = {
            "name": self.name,
            "depends": self.depends,
            "typ": "DEPENDS",
        }
        dump_ = json.dumps(dct)
        tgt_str = TASK_GRPAPH_HEADER + dump_ + "\n"
        sys.stdout.write(tgt_str)
        sys.stdout.flush()

        return self.depends

    def Sources(self) -> list[str]:
        return self.handler.Sources()

    def IncludeDir(self) -> list[str]:
        return self.handler.IncludeDir()
