from ..utils import log
from .ThirdParty import ThirdParty


class HALDrivers(ThirdParty):
    """STM32 HAL Drivers"""

    def setup(self) -> None:
        # child_dirs = []

        # print(f"HALDrivers incs: {self.incs}")
        # log.debug(f"HALDrivers incs: {self.defines}")
        if "USE_HAL_DRIVER" not in self.defines:
            self.defines.update({"USE_HAL_DRIVER": ""})
        cpu = "STM32F407xx"
        for k, v in self.defines.items():
            if k.startswith("STM") and v == "":
                cpu = k
        if not cpu:
            log.error("HALDrivers: cpu defines not found")
            return

        # log.debug(f"HALDrivers defines: {self.defines}  {self.dir}")

        driver_dir = self.dir / f"{cpu[:-4]}xx_HAL_Driver"
        # child_dirs = self.__child_dirs(cpu)
        self.incs += [
            driver_dir / "Inc",
            driver_dir / "Legacy" / "Inc",
        ]

        self.srcs = self.sources(
            child_dirs=[f"{cpu[:-4]}xx_HAL_Driver"],
            exclude_dirs=self.exclude_dirs,
            exclude_prefixes=self.exclude_prefixes,
            exclude_suffixes=self.exclude_suffixes,
            recursive=self.recursive,
        )

        # print(f"HALDrivers srcs: {self.srcs}")
        self.__add_cmsis(cpu)
        pass

    def __add_cmsis(self, cpu: str) -> None:
        # cmsis_dir_exsited = False
        cmsis_dir = self.dir / "CMSIS"
        # for child_dir in self.dir.iterdir():
        #     if not child_dir.is_dir():
        #         continue
        #     if child_dir.name == "CMSIS":
        #         cmsis_dir_exsited = True
        #         continue
        # print(f"HALDrivers cmsis_dir: {cmsis_dir}  -{self.dir.exists()}")
        if not cmsis_dir.exists():
            log.error("HALDrivers: CMSIS dir not found")
            return

        asm_type = "gcc"
        if self.params and "tool" in self.params:
            if self.params["tool"] == "armclang":
                asm_type = "arm"
        # cmsis_dir = self.dir / "CMSIS"
        cmsis_stm32_dir = cmsis_dir / "Device" / "ST" / f"{cpu[:-4]}xx"

        asm_fname = f"startup_{cpu.lower()}.s"
        asm_path = cmsis_stm32_dir / "Source" / "Templates" / asm_type / asm_fname
        if not asm_path.is_file():
            log.warn(f"HALDrivers: {asm_path} not found")
            asm_path = None
            # return
        if asm_path:
            self.srcs.append(asm_path)

        incs = [
            cmsis_dir / "Include",
            cmsis_stm32_dir / "Include",
        ]
        self.incs.extend(incs)

    def build(self) -> None:
        pass

    def __driver_dir(self, cpu: str) -> list[str]:
        pass

    def __child_dirs(self, cpu: str) -> list[str]:
        """
        add filter scr dir to src file
        """
        child_dirs = []
        # 遍历文件夹
        # log.debug(f"HALDrivers root dir: {self.dir} {cpu}")
        # log.debug(f"HALDrivers exclude_dirs: {self.exclude_dirs}")
        # log.debug(f"HALDrivers exclude_prefixes: {self.exclude_prefixes}")
        # log.debug(f"HALDrivers exclude_suffixes: {self.exclude_suffixes}")

        for child_dir in self.driver_dir.iterdir():
            if not child_dir.is_dir():
                continue
            if "_HAL_" not in child_dir.name.upper():
                continue
            # if child_dir.name == "CMSIS":
            #     cmsis_exsited = True
            #     continue
            if child_dir.name.startswith(f"{cpu[:-4]}xx"):
                child_dirs.append(child_dir.name)
        # if not cmsis_exsited:
        #     log.error("HALDrivers: CMSIS dir not found")
        #     return []
        # child_dirs.append("CMSIS")
        return child_dirs

        """
        .S  GCC  ARM 
        self.src_dirs.append(self.root / "CMSIS" / "Device" / "ST" / "STM32F4xx" / "Source" / "Templates")
 
        #include
        self.src_dirs.append(self.root / "CMSIS" / "Include")
        self.src_dirs / ("CMSIS/Device/ST/" + self.mcu_dir_prefix + "/Include"),

        """
