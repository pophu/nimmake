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

"""Base
base — Base class for all build tasks.
"""

import json


class Targets:
    """代表一个真实的文件构建任务"""

    def __init__(
        self,
        name: str,
        targets: str | list | list[str] = None,
        sources: str | list | list[str] = None,
        typ: str = "TARGETS",
    ):
        self.name = name
        self.targets = targets
        self.sources = sources
        self.typ = typ

    def Dump(self) -> None:
        dct = {
            "name": self.name,
            "targets": self.targets,
            "sources": self.sources,
            "typ": self.typ,
        }
        return json.dumps(dct)

    def __repr__(self):
        return f"<{__class__.__name__}>: {self.name}>"


class Commands:
    """代表一个真实的文件构建任务"""

    def __init__(self, name: str, commands: str | list | list[str] = None):
        self.name = name
        self.commands = commands

    def Dump(self) -> None:
        dct = {
            "name": self.name,
            "commands": self.commands,
            "typ": "COMMANDS",
        }
        return json.dumps(dct)

    def __repr__(self):
        return f"<Command: {self.name}>"


class Phonies:
    """代表一个真实的文件构建任务"""

    def __init__(self, name: str, phonies: str | list | list[str] = None):
        self.name = name
        self.phonies = []
        if isinstance(phonies, str):
            self.phonies.append(phonies)
        elif isinstance(phonies, list):
            for p in phonies:
                if isinstance(p, str):
                    self.phonies.append(p)
                elif isinstance(p, Commands):
                    self.phonies.append(p.name)
                elif isinstance(p, Targets):
                    self.phonies.append(p.name)
                else:
                    print(f"Phony {name} {p} error")
                    return
        elif isinstance(phonies, Commands):
            self.phonies.append(phonies.name)
        elif isinstance(phonies, Targets):
            self.phonies.append(phonies.name)
        else:
            print(f"Phony {name} {phonies} error")
            return

    def Dump(self) -> None:
        dct = {
            "name": self.name,
            "phonies": self.phonies,
            "typ": "PHONIES",
        }
        return json.dumps(dct)

    def __repr__(self):
        return f"<Phony: {self.name}>"


class Aliases:
    """代表一个真实的文件构建任务"""

    def __init__(self, name: str, aliases: str | list | list[str] = None):
        self.name = name
        self.aliases = []
        if isinstance(aliases, str):
            self.aliases.append(aliases)
        elif isinstance(aliases, list):
            for p in aliases:
                if isinstance(p, str):
                    self.aliases.append(p)
                elif isinstance(p, Commands):
                    self.aliases.append(p.name)
                elif isinstance(p, Targets):
                    self.aliases.append(p.name)
                else:
                    print(f"Alias {name} {p} error")
                    return
        elif isinstance(aliases, Commands):
            self.aliases.append(aliases.name)
        elif isinstance(aliases, Targets):
            self.aliases.append(aliases.name)
        else:
            print(f"Alias {name} {aliases} error")
            return

    def Dump(self) -> None:
        dct = {
            "name": self.name,
            "aliases": self.aliases,
            "typ": "ALIASES",
        }
        return json.dumps(dct)

    def __repr__(self):
        return f"<Alias: {self.name}>"


# import os
# from collections import OrderedDict

# """
# 嵌套关系太复杂， 先实现 基础功能， 编译一个项目
# """


# class Tasks:
#     """
#     # targets: list[str]
#     # [ ["target", name, " "] , ["phony", name, " "], ["alias", name, " "] ]
#     # [ ["target", "main", " "] , ["command", name, "main", "pre/post"] ]
#     # parties: dict {"target": "main", name  ---}  ]
#     #
#     # commands:  list[list[str] | str]  like target
#     #            cannot execute directly,depend on alias targets
#     # phonies:  list[list[str] | str]  like target
#     #            cannot execute directly,depend on alias targets
#     # aliases:  list[str]  execute directly, manage target phonies command
#     """

#     def __init__(self, name):
#         self.target = ""  # 1 default target
#         self.parties = []
#         self.commands = []
#         self.actions = []
#         self.phonies = []
#         self.aliases = []
#         self.name = name
#         self.built = False  # 是否已经构建过
#         self.tasks = []

#         # result
#         self._target_tasks = []
#         self._phony_tasks = []
#         self._alias_tasks = []

#     def target_tasks(self):
#         preactions = []
#         for action in self.actions:
#             if action[2] == "pre":
#                 preactions.append(action[1])
#         self._target_tasks.append(["preactions", preactions])

#         # parties
#         self._target_tasks.append(["parties", ""])

#         postactions = []
#         for action in self.actions:
#             if action[2] == "post":
#                 postactions.append(action[1])
#         self._target_tasks.update({"postactions": postactions})

#     def alias_tasks(self):
#         for alias in self.aliases:
#             if alias == self.target:
#                 self.target_tasks(self)
#                 self._alias_tasks += self._target_tasks
#                 continue
#             self._alias_tasks + alias

#     def phony_tasks(self):
#         for phony in self.phonies:
#             if phony == self.target:
#                 self.target_tasks(self)
#                 self._phony_tasks += self._target_tasks
#                 continue
#             self._phony_tasks + phony

#     def check(self):
#         self._tasks.update({"target": {}})
#         self._tasks.update({"command": {}})
#         self._tasks.update({"phony": {}})
#         for target in self.targets:
#             if target[0] == "target":
#                 self._tasks.get("target").update({target[1]: []})
#                 tgt_party_lst = self._tasks.get("target").get(target[1])
#                 for _parties in self.helper["PARTIES"].keys():
#                     tgt_party_lst.append(_parties)
#             if target[0] == "phony":
#                 self._tasks.get("phony").update({target[1]: []})
#                 phony_party_lst = self._tasks.get("phony").get(target[1])
#                 for dep in self.helper["PHONIES"].keys():
#                     phony_party_lst.append(dep)
#             if target[0] == "command":
#                 self._tasks.get("command").update({target[1]: []})
#                 cmd_party_lst = self._tasks.get("command").get(target[1])
#                 for cmd in self.helper["COMMANDS"].keys():
#                     cmd_party_lst.append(cmd)


# # ==========================================
# # 1. Action 类：定义“做什么”
# # ==========================================
# class Action:
#     """封装一个具体的构建动作（可以是命令或函数）"""

#     def __init__(self, func_or_cmd):
#         self.func_or_cmd = func_or_cmd

#     def execute(self, target, source, env):
#         print(f"  >> Executing Action for: {target}")
#         if callable(self.func_or_cmd):
#             # 如果是 Python 函数
#             return self.func_or_cmd(target, source, env)
#         else:
#             # 如果是字符串命令（这里仅做模拟打印）
#             print(f"  >> [Shell] {self.func_or_cmd}")
#             return 0  # 0 表示成功


# # ==========================================
# # 2. Target 基类：定义“产出物”
# # ==========================================
# class Target:
#     def __init__(self, name):
#         self.name = name
#         self.parties = []  # 依赖的三方组件
#         self.sources = []  # 依赖的源文件/目标
#         self.action = None  # 构建此目标的 Action
#         self.is_phony = False  # 是否是伪目标
#         self.built = False  # 是否已经构建过

#     def add_source(self, source):
#         if source not in self.sources:
#             self.sources.append(source)


# # ==========================================
# # 3. Command 类：普通的文件构建目标
# # ==========================================
# class Command(Target):
#     """代表一个真实的文件构建任务"""

#     def __init__(self, target_name, sources, action):
#         super().__init__(target_name)
#         self.sources = sources if isinstance(sources, list) else [sources]
#         self.action = action if isinstance(action, Action) else Action(action)

#     def __repr__(self):
#         return f"<Command: {self.name}>"


# # ==========================================
# # 4. PhonyTarget 类：伪目标（如 clean, install）
# # ==========================================
# class PhonyTarget(Target):
#     """不对应真实文件，总是会被执行"""

#     def __init__(self, name, action=None):
#         super().__init__(name)
#         self.is_phony = True
#         if action:
#             self.action = action if isinstance(action, Action) else Action(action)

#     def __repr__(self):
#         return f"<Phony: {self.name}>"


# # ==========================================
# # 5. BuildSystem 类：核心管理器（模拟 SCons 引擎）
# # ==========================================
# class BuildSystem:
#     def __init__(self):
#         self.targets = OrderedDict()  # 存储所有目标 {name: Target}
#         self.default_target = None

#     def Command(self, target_name, sources, action):
#         """类似 env.Command()"""
#         target = Command(target_name, sources, action)
#         self.targets[target_name] = target
#         if self.default_target is None:
#             self.default_target = target_name
#         return target

#     def Phony(self, name, action=None):
#         """创建伪目标"""
#         target = PhonyTarget(name, action)
#         self.targets[name] = target
#         return target

#     def Alias(self, alias_name, target_names):
#         """创建别名（依赖一组目标）"""
#         # 伪代码简化：Alias 本质上是一个没有 Action 的 PhonyTarget
#         phony = self.Phony(alias_name)
#         for t_name in target_names:
#             if t_name in self.targets:
#                 phony.add_source(self.targets[t_name])
#         return phony

#     def _build_node(self, target, visited=None):
#         """
#         核心递归构建逻辑（拓扑排序 + 执行）
#         """
#         if visited is None:
#             visited = set()

#         # 防止循环依赖
#         if target.name in visited:
#             raise Exception(f"循环依赖检测到: {target.name}")
#         visited.add(target.name)

#         # 1. 先递归构建所有依赖（自底向上）
#         for source in target.sources:
#             if isinstance(source, Target):
#                 self._build_node(source, visited)
#             # 如果是普通字符串（源文件），检查是否存在（这里省略文件存在性检查）

#         # 2. 决定是否需要构建
#         # 真实 SCons 会检查 MD5 签名或时间戳
#         # 这里简化为：Phony 总是执行，Command 如果没构建过就执行
#         need_build = target.is_phony or not target.built

#         if need_build and target.action:
#             print(f"[BUILD] {target.name}")
#             result = target.action.execute(target, target.sources, {})
#             if result != 0:
#                 raise Exception(f"构建失败: {target.name}")
#             target.built = True
#         else:
#             print(f"[SKIP]  {target.name} (已经是最新)")

#     def build(self, target_name=None):
#         """启动构建"""
#         name = target_name or self.default_target
#         if name not in self.targets:
#             print(f"错误: 未知目标 '{name}'")
#             return

#         print(f"=== 开始构建: {name} ===")
#         try:
#             self._build_node(self.targets[name])
#             print("=== 构建成功 ===\n")
#         except Exception as e:
#             print(f"=== 构建失败: {e} ===\n")


# # ==========================================
# # 6. 模拟使用场景 (类似 SConstruct 文件)
# # ==========================================
# if __name__ == "__main__":
#     env = BuildSystem()

#     # 定义一个 Python 函数作为 Action
#     def compile_code(target, source, env):
#         print(f"    [Python] 正在编译 {source} -> {target}")
#         # 模拟编译耗时
#         return 0

#     # 1. 定义普通构建命令
#     env.Command("app.o", "app.c", compile_code)
#     env.Command("utils.o", "utils.c", "gcc -c utils.c -o utils.o")

#     # 2. 定义链接命令（依赖前面的 .o 文件）
#     env.Command("my_app", ["app.o", "utils.o"], "gcc app.o utils.o -o my_app")

#     # 3. 定义伪目标
#     env.Phony("clean", lambda t, s, e: print("    [Clean] 删除所有构建文件...") or 0)

#     # 4. 定义别名
#     env.Alias("all", ["my_app"])

#     # --- 测试构建 ---
#     env.build("my_app")  # 完整构建
#     env.build("my_app")  # 再次构建（应该被跳过）
#     env.build("clean")  # 执行 clean
