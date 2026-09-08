from .ThirdParty import ThirdParty


class LVGL(ThirdParty):
    """LVGL"""

    def setup(self) -> None:
        child_dirs = self.__child_dirs()

        self.incs = [
            self.dir,
            self.dir / "demos",
            self.dir / "examples",
        ]

        self.srcs = self.sources(
            child_dirs=child_dirs,
            exclude_dirs=self.exclude_dirs,
            exclude_prefixes=self.exclude_prefixes,
            exclude_suffixes=self.exclude_suffixes,
            recursive=True,
        )
        # print("LVGL srcs:", self.incs)
        # print("LVGL srcs:", self.incs)
        self.__after_setup()
        pass

    def __child_dirs(self, cpu: str = None) -> list[str]:
        """
        add filter scr dir to src file
        """
        child_dirs = []
        child_dirs.append("src")
        child_dirs.append("demos")
        child_dirs.append("examples")
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

    # class LVGL_3rd(Thirparty):
    #     def __init__(
    #         self,
    #         env: Environment = None,
    #         name: str = None,
    #         workspace_dir: Path = Path("."),
    #         party_pth: str = None,
    #         compile_mode: DIR_COMPILE_MODE = DIR_COMPILE_MODE.NONE.value,
    #         suffixes: List[str] = [".c"],
    #         **kwargv,
    #     ) -> None:
    #         super().__init__(env, name, workspace_dir, party_pth, compile_mode, suffixes, **kwargv)
    #         # print("LVGL_3rd __init ...........", self.pth)
    #         self.build_resources.macros.append("-DLV_CONF_INCLUDE_SIMPLE")
    #         # self.demo = None
    #         # self.example = None

    #     def set_srcs(self) -> List[File]:
    #         ## TODO  add  macro lib libdirs
    #         # self.build_resources.macros.append("-DUSE_HAL_DRIVER")

    #         srcs = []
    #         dir = self.pth.joinpath("lvgl", "src")
    #         srcs.extend(self.env_get_files_suffix(dir, [".c"], 1))
    #         # for src in srcs:
    #         #     print(str(src))

    #         if self.demo is not None:
    #             dir = self.pth.joinpath("lvgl", "demos")
    #             srcs.extend(self.env_get_files_suffix(dir, [".c"], 1))

    #         if self.example is not None:
    #             dir = self.pth.joinpath("lvgl", "examples")
    #             srcs.extend(self.env_get_files_suffix(dir, [".c"], 1))

    #         for src in srcs:
    #             if src in self.build_resources.srcs:
    #                 continue
    #             self.build_resources.srcs.append(src)
    #         pass

    #     def set_incs(self) -> List[File]:
    #         dir = self.pth.joinpath("lvgl")
    #         incs = [
    #             dir,
    #         ]
    #         if self.demo is not None:
    #             inc_dir = self.pth.joinpath("lvgl", "demos")
    #             incs.append(inc_dir)

    #         if self.example is not None:
    #             inc_dir = self.pth.joinpath("lvgl", "examples")
    #             incs.append(inc_dir)

    #         for inc in incs:
    #             if inc not in self.build_resources.incs:
    #                 self.build_resources.incs.append(inc)

    #         # print("========", self.build_resources.incs)

    #         return incs
    #         pass

    def set_attrs(self, **kwargv):
        self.demo = None
        self.example = None
        if len(kwargv) <= 0:
            return
        if kwargv.get("lvgldemo"):
            self.demo = 1

        if kwargv.get("lvglexample"):
            self.example = 1

    def build(self):
        ##  静态库模式 自己判断是否编译
        objs = []
        if (self.compile_mode & DIR_COMPILE_MODE.BUILD.value) and (self.build_resources.srcs != []):
            objs = self.build_resources.env.Object(source=self.build_resources.srcs)
        return objs
        pass


# class FreeModbus_3rd(Thirparty):
#     def __init__(
#         self,
#         workspace_dir: Path,
#         party_pth: str = None,
#         suffixes: List[str] = None,
#         src_enable: int = 1,
#     ) -> None:
#         super().__init__(workspace_dir, party_pth, suffixes, src_enable)

#     def add_srcs_incs(self, env: Environment, all_srcs: List[File], **kwargv) -> None:
#         newdir = self.pth.joinpath("freemodbus", "modbus")
#         self.srcs += self._get_srcs_without_childdir(env, newdir)
#         self.srcs += self._get_srcs_without_childdir(env, newdir.joinpath("rtu"))
#         self.srcs += self._get_srcs_without_childdir(env, newdir.joinpath("ascii"))
#         self.srcs += self._get_srcs_without_childdir(env, newdir.joinpath("functions"))

#         # tcp  ascii
#         self.incs = [
#             newdir / "include",
#             newdir / "rtu",
#             newdir / "ascii",
#             newdir / "tcp",
#             # newdir / "include",
#         ]
#         self.set_target(env, all_srcs)
#         # print("=======================================")
#         pass


# class USB_3rd(Thirparty):
#     def __init__(
#         self,
#         workspace_dir: Path,
#         party_pth: str = None,
#         suffixes: List[str] = None,
#         src_enable: int = 1,
#     ) -> None:
#         super().__init__(workspace_dir, party_pth, suffixes, src_enable)

#     def add_srcs_incs(self, env: Environment, all_srcs: List[File], **kwargv) -> None:
#         newdir = self.pth.joinpath("Library_USB")
#         self.srcs += self._get_srcs_without_childdir(
#             env, newdir.joinpath("class", "MSC")
#         )
#         self.srcs += self._get_srcs_without_childdir(env, newdir.joinpath("Core"))

#         self.incs = [
#             newdir / "class/MSC/Inc",
#             newdir / "Core/Inc",
#         ]

#         self.set_target(env, all_srcs)


# class CherryUSB_3rd(Thirparty):
#     def __init__(
#         self,
#         workspace_dir: Path,
#         party_pth: str = None,
#         suffixes: List[str] = None,
#         src_enable: int = 1,
#     ) -> None:
#         super().__init__(workspace_dir, party_pth, suffixes, src_enable)

#     def add_srcs_incs(self, env: Environment, all_srcs: List[File], **kwargv) -> None:
#         # newdir = self.pth.joinpath("CherryUSB")
#         # self.srcs += self._get_srcs_without_childdir(env, newdir.joinpath("common"))
#         # self.srcs += [
#         #     env.File(newdir / "osal/usb_osal_freertos.c"),
#         # ]

#         # # tcp  ascii
#         # self.incs = [
#         #     newdir / "common",
#         # ]
#         # self.set_target(env, all_srcs)
#         pass


# class TinyUSB_3rd(Thirparty):
#     def __init__(
#         self,
#         workspace_dir: Path,
#         party_pth: str = None,
#         suffixes: List[str] = None,
#         src_enable: int = 1,
#     ) -> None:
#         super().__init__(workspace_dir, party_pth, suffixes, src_enable)

#     def add_srcs_incs(self, env: Environment, srcs: List[File], **kwargv) -> None:

#         pass


# class LWIP_3rd(Thirparty):
#     def __init__(
#         self,
#         workspace_dir: Path,
#         party_pth: str = None,
#         suffixes: List[str] = None,
#         src_enable: int = 1,
#     ) -> None:
#         super().__init__(workspace_dir, party_pth, suffixes, src_enable)

#     def add_srcs_incs(self, env: Environment, srcs: List[File], **kwargv) -> None:
#         """pth 第三方源文件 头文件目录"""
#         pass
