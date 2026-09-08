from .ThirdParty import ThirdParty


class FreeRTOS(ThirdParty):
    """FreeRTOS"""

    def setup(self) -> None:
        child_dirs = self.__child_dirs()

        # self.incs = self.include_dirs(
        #     child_dirs=child_dirs,
        #     exclude_dirs=self.exclude_dirs,
        #     exclude_prefixes=self.exclude_prefixes,
        #     recursive=False,
        # )

        self.incs += [
            self.dir / "include",
        ]
        self.srcs = self.sources(
            child_dirs=child_dirs,
            exclude_dirs=self.exclude_dirs,
            exclude_prefixes=self.exclude_prefixes,
            exclude_suffixes=self.exclude_suffixes,
            recursive=False,
        )
        # print(f"FreeRTOS(ThirdParty) srcs: {self.srcs}")
        self.__after_setup()
        # print(f"FreeRTOS(ThirdParty) srcs: {self.srcs}")
        # print(f"FreeRTOS(ThirdParty) defines: {self.include_macros}")
        pass

    def __child_dirs(self, cpu: str = None) -> list[str]:
        """
        add filter scr dir to src file
        """
        child_dirs = []
        # child_dirs.append("Source")

        return child_dirs

    def __after_setup(self, cpu: str = None, fpu: str = None, abi: str = None) -> None:
        portable_tolchain = "GCC"
        if "toolchain" in self.include_macros:
            portable_tolchain = self.include_macros.get("toolchain")
        # if self.params and "tool" in self.params:
        #     if self.params["tool"] == "gcc":
        #         portable_tolchain = "GCC"
        #     elif self.params["tool"] == "armclang":
        #         portable_tolchain = "GCC"
        #     elif self.params["tool"] == "clang":
        #         portable_tolchain = "GCC"

        portable_chip = "ARM_CM4F"
        if "chip" in self.include_macros:
            portable_chip = self.include_macros.get("chip")
        # if self.params and "tool" in self.params:
        # if self.params and "CHIP" in self.params:
        #     if self.params["CHIP"] == "cortex-m3":
        #         portable_chip = "ARM_CM3"
        #     if self.params["CHIP"] == "cortex-m4":
        #         portable_chip = "ARM_CM4F"
        #     if self.params["CHIP"] == "cortex-m33":
        #         portable_chip = "ARM_CM33"

        heap = 4
        if "heap" in self.include_macros:
            heap = self.include_macros.get("heap")
        # if self.params and "HEAP" in self.params:
        #     heap = int(self.params["HEAP_SIZE"])

        incs = [
            # self.dir / "include",
            # self.dir / "CMSIS_RTOS_V2",
            self.dir / f"portable/{portable_tolchain}/{portable_chip}",
        ]

        srcs = [
            self.dir / f"portable/{portable_tolchain}/{portable_chip}/port.c",
            self.dir / f"portable/MemMang/heap_{heap}.c",
            # self.dir / "CMSIS_RTOS_V2/cmsis_os2.c",
        ]

        self.incs.extend(incs)
        self.srcs.extend(srcs)

    def build(self) -> None:
        pass
