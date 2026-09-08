# MIT License
#
# Copyright (c) 2026-2036 Pophu and contributors
# https://github.com/pophu/nimmake
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Compile DB"""

import json
from pathlib import Path

from nimmake.utils import log


class Compiledb:
    """
    compile_commands.json , any dir, can be searched recursively
    usual in the build dir
    [
    {
    "directory": "D:/ESP-IDF/Projects/09_webserver/build",
    "command": "C:\\Espressif\\tools\\xtensa-esp-elf\\esp-15.2.0_20251204\\xtensa-esp-elf\\bin\\xtensa-esp32s3-elf-gcc.exe -DESP_PLATFORM -DIDF_VER=\\\"v6.0.2-dirty\\\" -DSOC_MMU_PAGE_SIZE=CONFIG_MMU_PAGE_SIZE -DSOC_XTAL_FREQ_MHZ=CONFIG_XTAL_FREQ -D_GLIBCXX_HAVE_POSIX_SEMAPHORE -D_GLIBCXX_USE_POSIX_SEMAPHORE -D_GNU_SOURCE -D_POSIX_READER_WRITER_LOCKS -ID:/ESP-IDF/Projects/09_webserver/build/config -ID:/ESP-IDF/Projects/09_webserver/main -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_libc/platform_include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/freertos/config/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/freertos/config/include/freertos -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/freertos/config/xtensa/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/freertos/FreeRTOS-Kernel/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/freertos/FreeRTOS-Kernel/portable/xtensa/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/freertos/FreeRTOS-Kernel/portable/xtensa/include/freertos -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/freertos/esp_additions/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hw_support/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hw_support/include/soc -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hw_support/ldo/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hw_support/debug_probe/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hw_support/etm/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hw_support/mspi_timing_tuning/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hw_support/mspi_timing_tuning/tuning_scheme_impl/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hw_support/power_supply/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hw_support/modem/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hw_support/include/soc/esp32s3 -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hw_support/port/esp32s3/. -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hw_support/port/esp32s3/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hw_support/mspi_timing_tuning/port/esp32s3/. -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hw_support/mspi_timing_tuning/port/esp32s3/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/heap/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/heap/tlsf -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/log/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/soc/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/soc/esp32s3 -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/soc/esp32s3/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/soc/esp32s3/register -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/hal/platform_port/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/hal/esp32s3/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/hal/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_rom/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_rom/esp32s3/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_rom/esp32s3/include/esp32s3 -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_rom/esp32s3 -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_common/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_system/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_system/port/soc -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_system/port/include/private -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_stdio/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/xtensa/esp32s3/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/xtensa/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/xtensa/deprecated_include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hal_gpio/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hal_gpio/esp32s3/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hal_usb/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hal_usb/esp32s3/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hal_pmu/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hal_pmu/esp32s3/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hal_ana_conv/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hal_ana_conv/esp32s3/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hal_dma/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hal_dma/esp32s3/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/lwip/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/lwip/include/apps -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/lwip/lwip/src/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/lwip/port/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/lwip/port/freertos/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/lwip/port/esp32xx/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/lwip/port/esp32xx/include/arch -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/lwip/port/esp32xx/include/sys -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_wifi/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_wifi/include/local -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_wifi/wifi_apps/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_wifi/wifi_apps/nan_app/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_event/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_phy/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_phy/esp32s3/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_netif/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/nvs_flash/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_partition/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_blockdev/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_http_server/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/http_parser -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/vfs/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/fatfs/diskio -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/fatfs/src -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/fatfs/vfs -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/wear_levelling/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/sdmmc/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hal_sd/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hal_sd/esp32s3/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_driver_sdmmc/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_driver_sdmmc/legacy/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_driver_sd_intf/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_driver_sdspi/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_driver_spi/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_pm/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hal_gpspi/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_hal_gpspi/esp32s3/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_driver_dma/include -ID:/ESP-IDF/IDF6/v6.0.2/esp-idf/components/esp_driver_gpio/include -ID:/ESP-IDF/Projects/09_webserver/managed_components/joltwallet__littlefs/include @\"D:/ESP-IDF/Projects/09_webserver/build/toolchain/cflags\" -fdiagnostics-color=always -ffunction-sections -fdata-sections -Wall -Werror -Wno-error=unused-function -Wno-error=unused-variable -Wno-error=unused-but-set-variable -Wno-error=deprecated-declarations -Wextra -Wno-error=extra -Wno-unused-parameter -Wno-sign-compare -Wno-enum-conversion -gdwarf-4 -ggdb -Og -fno-shrink-wrap -fmacro-prefix-map=D:/ESP-IDF/Projects/09_webserver=. -fmacro-prefix-map=D:/ESP-IDF/IDF6/v6.0.2/esp-idf=/IDF -fstrict-volatile-bitfields -fno-jump-tables -fno-tree-switch-conversion -std=gnu23 -Wno-old-style-declaration -fzero-init-padding-bits=all -fno-malloc-dce -o esp-idf\\main\\CMakeFiles\\__idf_main.dir\\littlefs_app.c.obj -c D:\\ESP-IDF\\Projects\\09_webserver\\main\\littlefs_app.c",
    "file": "D:\\ESP-IDF\\Projects\\09_webserver\\main\\littlefs_app.c",
    "output": "esp-idf\\main\\CMakeFiles\\__idf_main.dir\\littlefs_app.c.obj"
    }
    ]
    """

    def __init__(
        self,
        helper: dict[str, str],
        targets_commands: dict[str, dict],
        flags: dict[str, list] = None,
    ):
        self.helper = helper
        self.targets_commands = targets_commands
        self.flags = flags

        print("Compiledb ........")
        self.gen()

    def gen(self):
        """
        BUILD/OBJ/DRIVER/stm32f4xx_hal_rcc_ex.o ['arm-none-eabi-gcc -c -mcpu=cortex-m4 -mfloat-abi=hard -mthumb -O2 -Wall -g -fdata-sections -ffunction-sections -std=c99 -DSTM32F407xx -DUSE_HAL_DRIVER  -Isrc_stm/Drivers/STM32F4xx_HAL_Driver/Inc/Legacy -Isrc_stm/Drivers/STM32F4xx_HAL_Driver/Inc -Isrc_stm/Core/Inc ', 'src_stm/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_rcc_ex.c', 1777520757.3615153]
        """

        gen_lst = []
        # print(f"self.targets_commands {list(self.targets_commands.keys())}")
        objs = self.targets_commands.get("OBJECTS", [])
        log.info(f"self.targets_commands {list(objs.keys())}")
        build_dir = Path(self.helper.get("BUILDDIR", "."))
        for obj, item in objs.items():
            log.info(obj, item)
            # build_dir = Path(obj).parts[0]
            fil = item[1]
            out = obj
            command = item[0] + " " + fil
            _entry = {
                "directory": build_dir.resolve().as_posix(),  # 构建工作目录
                "command": command,  # 完整的编译命令
                "file": Path(fil).parent.resolve().as_posix(),  # 源文件路径
                "output": Path(out).resolve().as_posix(),  # 输出文件路径
            }
            gen_lst.append(_entry)
        with open("compile_commands.json", "w", encoding="utf-8") as f:
            json.dump(gen_lst, f, indent=2)

    def __gen_compile_commands_json(self) -> list[dict[str, object]]:
        """
        生成 compile_commands.json 格式的编译数据库

        Returns:
            list[dict]: 包含 directory, command, file, output 的字典列表
        """
        _result = []

        # 获取构建目录（使用 BUILDDIR 或当前工作目录）
        _build_dir = str(Path.cwd())
        if self.helper.get("BUILDDIR"):
            _build_dir = str(Path(self.helper["BUILDDIR"]).resolve())

        # 遍历所有编译命令并转换为 compile_commands.json 格式
        objs = self.targets_commands.get("OBJECTS", [])

        for obj in objs:
            # 将所有部分拼接成完整命令字符串
            # _command_str = " ".join(str(p) for p in _parts)
            _command_str = obj.get("command", "")
            _file = obj.get("src", "")
            _output = obj.get("obj", "")

            # # 提取源文件和输出文件路径
            # _file = _cmd["src"][0] if _cmd.get("src") else ""
            # _output = _cmd["obj"][0] if _cmd.get("obj") else ""

            # 构建符合 compile_commands.json 标准格式的条目
            _entry = {
                "directory": _build_dir,  # 构建工作目录
                "command": _command_str,  # 完整的编译命令
                "file": _file,  # 源文件路径
                "output": _output,  # 输出文件路径
            }
            _result.append(_entry)

        return _result

        # for _cmd in objs:
        #     # 拼接完整的编译命令
        #     _parts = []
        #     _parts += _cmd.get("tool", [])  # 工具链: ["gcc", "-c"]
        #     _parts += _cmd.get("toolflag", [])  # 编译标志: ["-O2", "-Wall"]
        #     _parts += _cmd.get("define", [])  # 宏定义: ["-DDEBUG"]
        #     _parts += _cmd.get("include_macro", [])  # 包含宏
        #     _parts += _cmd.get("inc_flag", [])  # 包含路径: ["-I/path"]
        #     _parts += _cmd.get("_o", [])  # 输出选项: ["-o"]
        #     _parts += _cmd.get("obj", [])  # 目标文件: ["build/main.o"]
        #     _parts += _cmd.get("src", [])  # 源文件: ["src/main.c"]

        #     # 将所有部分拼接成完整命令字符串
        #     _command_str = " ".join(str(p) for p in _parts)

        #     # 提取源文件和输出文件路径
        #     _file = _cmd["src"][0] if _cmd.get("src") else ""
        #     _output = _cmd["obj"][0] if _cmd.get("obj") else ""

        #     # 构建符合 compile_commands.json 标准格式的条目
        #     _entry = {
        #         "directory": _build_dir,  # 构建工作目录
        #         "command": _command_str,  # 完整的编译命令
        #         "file": _file,  # 源文件路径
        #         "output": _output,  # 输出文件路径
        #     }
        #     _result.append(_entry)

        # return _result
        pass
