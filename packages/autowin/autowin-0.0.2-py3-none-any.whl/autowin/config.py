# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-05T06:10:18.750Z
# 文件描述：autowin 模块的全局配置管理。
# 文件路径：src/autowin/config.py

import logging
import os
from typing import Dict, Any

class Config:
    """
    autowin 模块的全局配置类。
    用户可以通过修改此类的属性来调整模块的行为。
    """
    def __init__(self):
        # 自动化操作的默认超时时间（秒）
        self.DEFAULT_TIMEOUT: int = 10

        # pywinauto 后端类型，可选 "uia" 或 "win32"
        # uia 更现代，支持更多UI元素，但可能在老应用上不如win32稳定
        self.PYWINAUTO_BACKEND: str = "uia"

        # 日志配置
        self.LOG_LEVEL: int = logging.INFO
        self.LOG_FILE_PATH: str = os.path.join(os.getcwd(), "autowin.log")
        self.LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

        # 屏幕截图保存路径
        self.SCREENSHOT_DIR: str = os.path.join(os.getcwd(), "screenshots")
        # 屏幕截图默认置信度 (0.0 - 1.0)
        self.SCREENSHOT_CONFIDENCE: float = 0.9

        # 重试机制默认配置
        self.MAX_RETRIES: int = 5 # 最大重试次数
        self.RETRY_DELAY: float = 1.0 # 每次重试之间的延迟（秒）
        self.RETRY_BACKOFF: float = 2 # 重试延迟的指数退避因子

    def to_dict(self) -> Dict[str, Any]:
        """将当前配置转换为字典。"""
        return {attr: getattr(self, attr) for attr in dir(self) if not attr.startswith('__') and not callable(getattr(self, attr))}

# 创建一个全局配置实例
settings = Config()

# 确保截图目录存在
os.makedirs(settings.SCREENSHOT_DIR, exist_ok=True)