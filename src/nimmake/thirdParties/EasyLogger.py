from .ThirdParty import ThirdParty


class EasyLogger(ThirdParty):
    """EasyLogger"""

    def setup(self) -> None:
        child_dirs = self.__child_dirs()

        self.incs = [
            self.dir / "easylogger" / "inc",
        ]
        self.srcs = self.sources(
            child_dirs=child_dirs,
            exclude_dirs=self.exclude_dirs,
            exclude_prefixes=self.exclude_prefixes,
            exclude_suffixes=self.exclude_suffixes,
            recursive=False,
        )
        self.__after_setup()
        pass

    def __child_dirs(self, cpu: str = None) -> list[str]:
        """
        add filter scr dir to src file
        """
        child_dirs = []
        child_dirs.append("easylogger/src")

        return child_dirs

    def __after_setup(self, cpu: str = None, fpu: str = None, abi: str = None) -> None:
        # incs = [
        #     self.dir / "inc",
        # ]

        # # srcs = [
        # #     self.dir / f"portable/{portable_tolchain}/{portable_chip}/port.c",
        # #     self.dir / f"portable/MemMang/heap_{heap}.c",
        # #     # self.dir / "CMSIS_RTOS_V2/cmsis_os2.c",
        # # ]

        # self.incs.extend(incs)
        # # self.srcs.extend(srcs)
        pass

    def build(self) -> None:
        pass
