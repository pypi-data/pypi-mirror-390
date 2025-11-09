from __future__ import annotations

import logging
import platform
from functools import wraps
from typing import Callable
from typing import TypeVar

from rich.logging import RichHandler
from typing_extensions import ParamSpec

from fspacker.settings import get_settings

P = ParamSpec("P")
R = TypeVar("R")


class Logger:
    """日志记录器."""

    SEP_CHAR = "="
    __instance: logging.Logger | None = None

    @classmethod
    def get_instance(cls, name: str, *, debug: bool = False) -> logging.Logger:
        """获取日志记录器实例.

        Args:
            name (str): 模块名称.
            debug (bool, optional): 是否开启调试模式. Defaults to False.

        Returns:
            logging.Logger: 日志记录器实例.
        """
        if cls.__instance is None:
            level = (
                logging.DEBUG
                if (debug or get_settings().mode.debug)
                else logging.INFO
            )

            logging.basicConfig(
                level=level,
                format="[%(asctime)s] %(message)s",
                datefmt="%X",
                handlers=[RichHandler(markup=True)],
            )

            cls.__instance = logging.getLogger(name)
        return cls.__instance

    @classmethod
    def show_build_info(cls, func: Callable[P, R]) -> Callable[P, R]:
        """显示构建信息.

        Returns:
            Callable[P, R]: 包装后的函数.
        """

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            from fspacker import __build_date__  # noqa: PLC0415
            from fspacker import __version__  # noqa: PLC0415

            logger = cls.get_instance(__name__)
            Logger.show_symbol("FSPACKER")
            logger.info(f"版本: {__version__}, 构建日期: {__build_date__}")
            logger.info(f"Python 版本: {platform.python_version()}")
            logger.info(f"操作系统: {platform.system()} {platform.release()}")
            Logger.show_symbol("FSPACKER")

            return func(*args, **kwargs)

        return wrapper

    @classmethod
    def show_settings_mode(cls) -> None:
        """显示设置模式."""
        logger = cls.get_instance(__name__)
        logger.info(f"模式: {get_settings().mode}")
        logger.info(f"链接: {get_settings().urls}")
        logger.info(f"目录: {get_settings().dirs}")

    @classmethod
    def show_symbol(cls, symbol: str) -> None:
        """显示分隔符信息.

        Args:
            symbol (str): 分隔符内容.
        """
        logger = cls.get_instance(__name__)
        logger.info(cls.SEP_CHAR * 40 + symbol + cls.SEP_CHAR * 40)
