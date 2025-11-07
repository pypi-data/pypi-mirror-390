# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-05T06:10:28.809Z
# 文件描述：autowin 模块的统一日志系统。
# 文件路径：src/autowin/logger.py

import logging
from .config import settings

class Logger:
    """
    autowin 模块的统一日志记录器。
    """
    _logger: logging.Logger = None

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """
        获取配置好的日志记录器实例。
        """
        if cls._logger is None:
            cls._logger = logging.getLogger("autowin")
            cls._logger.setLevel(settings.LOG_LEVEL)
            cls._logger.propagate = False  # 阻止日志消息向上级记录器传递

            # 检查是否已经添加了处理器，避免重复添加
            if not cls._logger.handlers:
                # 控制台处理器
                console_handler = logging.StreamHandler()
                console_handler.setLevel(settings.LOG_LEVEL)
                formatter = logging.Formatter(settings.LOG_FORMAT, datefmt=settings.LOG_DATE_FORMAT)
                console_handler.setFormatter(formatter)
                cls._logger.addHandler(console_handler)

                # 文件处理器
                file_handler = logging.FileHandler(settings.LOG_FILE_PATH, encoding="utf-8")
                file_handler.setLevel(settings.LOG_LEVEL)
                file_handler.setFormatter(formatter)
                cls._logger.addHandler(file_handler)
        return cls._logger

# 提供一个方便的日志实例
logger = Logger.get_logger()