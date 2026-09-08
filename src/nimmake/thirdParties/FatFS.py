from .ThirdParty import ThirdParty


class FatFS(ThirdParty):
    """FatFS"""

    def setup(self) -> None:
        child_dirs = self.__child_dirs()

        # self.incs = self.include_dirs(
        #     child_dirs=child_dirs,
        #     exclude_dirs=self.exclude_dirs,
        #     exclude_prefixes=self.exclude_prefixes,
        #     recursive=False,
        # )
        self.incs = [
            self.dir / "source",
        ]

        self.srcs = self.sources(
            child_dirs=child_dirs,
            exclude_dirs=self.exclude_dirs,
            exclude_prefixes=self.exclude_prefixes,
            exclude_suffixes=self.exclude_suffixes,
            recursive=False,
        )
        # self.__after_setup()
        pass

    def __child_dirs(self, cpu: str = None) -> list[str]:
        """
        add filter scr dir to src file
        """
        child_dirs = []
        child_dirs.append("source")

        return child_dirs

    def __after_setup(self, cpu: str = None, fpu: str = None, abi: str = None) -> None:
        incs = [
            self.dir / "source",
        ]

        # srcs = [
        #     self.dir / f"portable/{portable_tolchain}/{portable_chip}/port.c",
        #     self.dir / f"portable/MemMang/heap_{heap}.c",
        #     # self.dir / "CMSIS_RTOS_V2/cmsis_os2.c",
        # ]

        self.incs.extend(incs)
        # self.srcs.extend(srcs)

    def build(self) -> None:
        pass


# class FATFS_3rd(Thirparty):
#     def __init__(
#         self,
#         workspace_dir: Path,
#         party_pth: str = None,
#         suffixes: List[str] = None,
#         src_enable: int = 1,
#     ) -> None:
#         super().__init__(workspace_dir, party_pth, suffixes, src_enable)

#     def add_srcs_incs(self, env: Environment, all_srcs: List[File], **kwargv) -> None:
#         newdir = self.pth.joinpath("FatFS")
#         self.srcs += self._get_srcs_without_childdir(env, newdir.joinpath("source"))
#         # self.srcs += env.Glob(newdir.joinpath("source", "*.c").as_posix())
#         self.incs = [
#             newdir / "source",
#         ]
#         self.set_target(env, all_srcs)
