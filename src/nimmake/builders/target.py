# from . import Action


# class Target:
#     def __init__(self, name):
#         self.name = name
#         self.parties = []  # 依赖的三方组件
#         self.sources = []  # 依赖的源文件/目标
#         self.actions = []  # 构建此目标的 Action
#         self.macros = []  # 定义的宏
#         self.incs = []  # 包含的头文件
#         self.is_phony = False  # 是否是伪目标
#         self.built = False  # 是否已经构建过

#     def add_source(self, source):
#         if source not in self.sources:
#             self.sources.append(source)


# class Command(Target):
#     """
#     代表一个真实的文件构建任务
#     直接添加actions
#     """

#     def __init__(self, name, action: str | list[str]):
#         super().__init__(name)
#         # self.sources = sources if isinstance(sources, list) else [sources]
#         self.action = action if isinstance(action, Action) else Action(action)

#     def __repr__(self):
#         return f"<Command: {self.name}>"


# class PhonyTarget(Target):
#     """
#     不对应真实文件，总是会被执行
#     包含以上两种情况
#     """

#     def __init__(self, name, action=None):
#         super().__init__(name)
#         self.is_phony = True
#         if action:
#             self.action = action if isinstance(action, Action) else Action(action)

#     def __repr__(self):
#         return f"<Phony: {self.name}>"
