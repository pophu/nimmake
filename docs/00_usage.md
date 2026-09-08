## usage

先用env 进行编译 ， pkl 管理编译-基于文件时间戳
过渡到google 基于数据驱动 ，GN Generate Ninja
参考bazel 申明式语法。bazel 已经支持极简构建了，为什么不能用？ 对于外部库扩展不够灵活？
自己做的可以将环境变量带进去， bazel GN 暂且做不到这一点。
GN 能不断依赖子目录的 build.gn
gn 换一个工具链 ，就得重新适配 ?? 当前项目价值所在？？
现在ai 时代， 让ai 重新写个配置就可以了
假如添加 一个外部FreeRTOS, gn 有大量手动工作，而pymakex 可以有内置的FreeRTOS 配置，直接添加即可。
这个也是IDF 价值所在

### 不安装运行

chang dir to src ,run "python -m nimmake.cli"

```shell
cd src
python -m nimmake.cli

python -m nimmake.cli -f Makefile.py --verbose

python nimmake/cli.py -f Makefile.py --target=release

python -m nimmake.cli  -f examples/01.py

python -m nimmake.cli  -f examples/01.py
```

### 安装运行

```shell
cd d:\MyCodeNew\nimmake
uv build
python -m build
python -m build --wheel
pip install dist/nimmake-0.5.0-py3-none-any.whl
```

### 开发模式安装调试

不需要build 安装

```shell

pip install -e ".[dev]"  ，install dev mode

rm -rf dist/ build/ PyMakeX.egg-info/
```

### pytest 测试

after "pip install -e .[dev]"
you can run pytest to do unit test

```shell
cd d:\MyCodeNew\nimmake
pytest

pytest tests/
pytest tests/test_scan_sources_basic.py

```

### modify version

pyproject.toml 中 version 为 0.2.0
cli 中 version 为 0.2.0
You shoud remove old version. Then install new version.
pip unistall pymake
pip install dist/PyMakeX-0.2.0-py3-none-any.whl
you can install temporary version
pip install -e .

### bazel 语法

### 新思路

[distutils]
index-servers =
pypi
nimmake

[pypi]
username = **token**
password = pypi-AgEIcHlwaS5vcmcCJDVkY2JhYTdlLTUzYjMtNGIwMi1hNzlkLTFjMDE1M2QwNTEwNwACD1sxLFsicHltYWtleCJdXQACLFsyLFsiNjQ4YzRmNWYtNGRmZi00YjhhLWIzYmEtOTcyZTUwMjIzYWNhIl1dAAAGIBoNsKN7EYf0wBugbVnWu7r43gX9iNdzg2FmrMmHNQvM
[nimmake]
repository = https://upload.pypi.org/legacy/
username = **token**
password = pypi-AgEIcHlwaS5vcmcCJDVkY2JhYTdlLTUzYjMtNGIwMi1hNzlkLTFjMDE1M2QwNTEwNwACD1sxLFsicHltYWtleCJdXQACLFsyLFsiNjQ4YzRmNWYtNGRmZi00YjhhLWIzYmEtOTcyZTUwMjIzYWNhIl1dAAAGIBoNsKN7EYf0wBugbVnWu7r43gX9iNdzg2FmrMmHNQvM
