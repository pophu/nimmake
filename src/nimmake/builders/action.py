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

"""Action
action — Base class for all build actions.
"""


class Action:
    """封装一个具体的构建动作（可以是命令或函数）"""

    def __init__(self, func_or_cmd, pre_post="", relative_to=""):
        self.type = "function" if callable(func_or_cmd) else "command"
        self.pre_post = pre_post
        self.func_or_cmd = func_or_cmd
        self.action_str = func_or_cmd if self.type == "function" else None
        self.relative_to = relative_to

    # def execute(self, target, source, env):
    #     if self.pre_post == "pre":
    #         # 执行预处理
    #         self.func_or_cmd(target, source, env)
    #     self.func_or_cmd = func_or_cmd

    def execute(self, target, source, env):
        print(f"  >> Executing Action for: {target}")
        if callable(self.func_or_cmd):
            # 如果是 Python 函数
            return self.func_or_cmd(target, source, env)
        else:
            # 如果是字符串命令（这里仅做模拟打印）
            self.action_str = f"  >> [Shell] {self.action_str}"
            return self.action_str  # 0 表示成功

    @property
    def action(self, target, source, macro, incs, env):
        if callable(self.func_or_cmd):
            # 如果是 Python 函数
            return self.func_or_cmd(target, source, env)
        else:
            # 如果是字符串命令（这里仅做模拟打印）
            self.action_str = f"{self.action_str}"
            return self.action_str

    def __repr__(self):
        return f"<Action: {self.action_str}>"
