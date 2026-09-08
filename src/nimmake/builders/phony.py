# import json


# class Phonies:
#     """代表一个真实的文件构建任务"""

#     def __init__(self, name: str, phonies: str | list | list[str] = None):
#         self.name = name
#         self.phonies = phonies

#     def Dump(self) -> None:
#         dct = {
#             "name": self.name,
#             "phonies": self.phonies,
#             "typ": "PHONIES",
#         }
#         return json.dumps(dct)

#     def __repr__(self):
#         return f"<Phony: {self.name}>"


# class Aliases:
#     """代表一个真实的文件构建任务"""

#     def __init__(self, name: str, aliases: str | list | list[str] = None):
#         self.name = name
#         self.aliases = aliases

#     def Dump(self) -> None:
#         dct = {
#             "name": self.name,
#             "aliases": self.aliases,
#             "typ": "ALIASES",
#         }
#         return json.dumps(dct)

#     def __repr__(self):
#         return f"<Alias: {self.name}>"
