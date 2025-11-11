from __future__ import annotations

from collections import OrderedDict
from typing import ClassVar

__all__ = ["SimplifyRule", "get_simplify_rules"]


class SimplifyRule:
    """库简化打包配置."""

    # 白名单匹配规则
    patterns: set[str] | None = None

    # 黑名单匹配规则
    excludes: set[str] | None = None


class MatplotlibRule(SimplifyRule):
    """Matplotlib simplify option."""

    excludes: ClassVar[set[str]] = {"matplotlib-.*.pth"}
    patterns: ClassVar[set[str]] = {
        "matplotlib/*",
        "matplotlib.libs/*",
        "mpl_toolkits/*",
        "pylab.py",
    }


class NumbaRule(SimplifyRule):
    """Numba simplify option."""

    patterns: ClassVar[set[str]] = {
        "numba/*",
        "numba*data/*",
    }


class NumpyRule(SimplifyRule):
    """Numpy simplify option."""

    excludes: ClassVar[set[str]] = {
        "numpy/_pyinstaller/*",
        "numpy/tests/*",
    }


class PygameRule(SimplifyRule):
    """Pygame simplify option."""

    excludes: ClassVar[set[str]] = {
        "pygame/docs/*",
        "pygame/examples/*",
        "pygame/tests/*",
        "pygame/__pyinstaller/*",
        "pygame*data/*",
    }


class PyQt5Rule(SimplifyRule):
    """PyQt5 simplify option."""

    patterns: ClassVar[set[str]] = {
        "PyQt5/__init__.py",
        "PyQt5/QtCore.pyd",
        "PyQt5/QtGui.pyd",
        "PyQt5/QtWidgets.pyd",
        "PyQt5/QtNetwork.pyd",
        "PyQt5/QtQml.pyd",
        # compatible for qt5
        "PyQt5/Qt*/bin/Qt5Core.dll",
        "PyQt5/Qt*/bin/Qt5Gui.dll",
        "PyQt5/Qt*/bin/Qt5Widgets.dll",
        "PyQt5/Qt*/bin/Qt5Network.dll",
        "PyQt5/Qt*/bin/Qt5Qml.dll",
        # other files
        "*plugins/iconengines/qsvgicon.dll",
        "*plugins/imageformats/*.dll",
        "*plugins/platforms/*.dll",
        # linux
        "PyQt5/QtCore.abi3.so",
        "PyQt5/QtGui.abi3.so",
        "PyQt5/QtWidgets.abi3.so",
        "PyQt5/QtNetwork.abi3.so",
        "PyQt5/QtQml.abi3.so",
        "*plugins/iconengines/libqsvgicon.so",
        "*plugins/imageformats/*.so",
        "*plugins/platforms/*.so",
    }


class PySide2Rule(SimplifyRule):
    """PySide2 Simplify Option."""

    patterns: ClassVar[set[str]] = {
        "PySide2/__init__.py",
        "PySide2/QtCore.pyd",
        "PySide2/QtGui.pyd",
        "PySide2/QtWidgets.pyd",
        "PySide2/QtNetwork.pyd",
        "PySide2/QtQml.pyd",
        "*plugins/iconengines/qsvgicon.dll",
        "*plugins/imageformats/*.dll",
        "*plugins/platforms/*.dll",
        # windows dlls
        "PySide2/pyside2.abi3.dll",
        "PySide2/Qt5Core.dll",
        "PySide2/Qt5Gui.dll",
        "PySide2/Qt5Widgets.dll",
        "PySide2/Qt5Network.dll",
        "PySide2/Qt5Qml.dll",
        # linux
        "PySide2/libpyside2.abi3.so",
        "PySide2/QtCore.abi3.so",
        "PySide2/QtGui.abi3.so",
        "PySide2/QtWidgets.abi3.so",
        "PySide2/QtNetwork.abi3.so",
        "PySide2/QtQml.abi3.so",
        "*plugins/iconengines/libqsvgicon.so",
        "*plugins/imageformats/*.so",
        "*plugins/platforms/*.so",
    }


class PySide6Rule(SimplifyRule):
    """PySide6 Simplify Option."""

    patterns: ClassVar[set[str]] = {
        "PySide6/__init__.py",
        "PySide6/QtCore.pyd",
        "PySide6/QtGui.pyd",
        "PySide6/QtWidgets.pyd",
        "PySide6/QtNetwork.pyd",
        "PySide6/QtQml.pyd",
        # windows dlls
        "PySide6/pyside6.abi3.dll",
        "PySide6/Qt6Core.dll",
        "PySide6/Qt6Gui.dll",
        "PySide6/Qt6Widgets.dll",
        "PySide6/Qt6Network.dll",
        "PySide6/Qt6Qml.dll",
        "*plugins/iconengines/qsvgicon.dll",
        "*plugins/imageformats/*.dll",
        "*plugins/platforms/*.dll",
        # linux
        "PySide6/libPySide6.abi3.so",
        "PySide6/QtCore.abi3.so",
        "PySide6/QtGui.abi3.so",
        "PySide6/QtWidgets.abi3.so",
        "PySide6/QtNetwork.abi3.so",
        "PySide6/QtQml.abi3.so",
        "*plugins/iconengines/libqsvgicon.so",
        "*plugins/imageformats/*.so",
        "*plugins/platforms/*.so",
    }


class TorchRule(SimplifyRule):
    """PyQt5 simplify option."""

    excludes: ClassVar[set[str]] = {
        # for debug
        "torch/utils/bottleneck/*",
        "torch/utils/checkpoint/*",
        "torch/utils/tensorboard/*",
        # for test
        "torch/utils/data/dataset/*",
        "torch/utils/data/dataloader/*",
    }


_OPTIONS: OrderedDict[str, SimplifyRule] = OrderedDict(
    {
        "matplotlib": MatplotlibRule(),
        "numba": NumbaRule(),
        "numpy": NumpyRule(),
        "pygame": PygameRule(),
        "pyqt5": PyQt5Rule(),
        "pyside2": PySide2Rule(),
        "pyside6": PySide6Rule(),
        "pyside6-essentials": PySide6Rule(),
        "torch": TorchRule(),
    },
)


def get_simplify_rules(name: str) -> SimplifyRule | None:
    """获取库打包精简配置规则.

    Args:
        name (str): 库名称

    Returns:
        SimplifyRule: 库打包精简配置
    """
    return _OPTIONS.get(name.lower())
