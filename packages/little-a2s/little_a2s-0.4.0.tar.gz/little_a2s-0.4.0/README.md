# little-a2s

[![](https://img.shields.io/pypi/v/little-a2s?style=flat-square&logo=pypi)](https://pypi.org/project/little-a2s/)
[![](https://readthedocs.org/projects/little-a2s/badge/?style=flat-square)](http://little-a2s.readthedocs.io/)
[![](https://img.shields.io/github/actions/workflow/status/thegamecracks/little-a2s/publish.yml?style=flat-square&logo=uv&label=build)](https://docs.astral.sh/uv/)
[![](https://img.shields.io/github/actions/workflow/status/thegamecracks/little-a2s/pytest.yml?style=flat-square&logo=pytest&label=tests)](https://docs.pytest.org/)
[![](https://img.shields.io/github/actions/workflow/status/thegamecracks/little-a2s/pyright-lint.yml?style=flat-square&label=pyright)](https://microsoft.github.io/pyright/#/)
[![](https://img.shields.io/github/actions/workflow/status/thegamecracks/little-a2s/ruff-check.yml?style=flat-square&logo=ruff&label=lints)](https://docs.astral.sh/ruff/)
[![](https://img.shields.io/github/actions/workflow/status/thegamecracks/little-a2s/ruff-format.yml?style=flat-square&logo=ruff&label=style)](https://docs.astral.sh/ruff/)

A synchronous and sans-I/O library implementing the A2S Valve Source Query protocol.

```py
from little_a2s import A2S

with A2S.from_addr("example.com", 27015, timeout=1) as a2s:
    print(a2s.info())
    print(a2s.players())
    print(a2s.rules())
```

Read the [documentation] or see the [examples] directory to get started!

[documentation]: https://little-a2s.rtfd.io/
[examples]: https://github.com/thegamecracks/little-a2s/tree/main/examples

## Installation

The minimum Python version required is **3.11**. No other dependencies are required.

This package can be installed from PyPI using one of the following commands:

```sh
# Linux/MacOS
python3 -m pip install little-a2s

# Windows
py -m pip install little-a2s
```

To install the development version of the library (requires Git), you can download
it from GitHub directly:

```sh
pip install git+https://github.com/thegamecracks/little-a2s
```

## License

This project is written under the [MIT License].

[MIT License]: /LICENSE
