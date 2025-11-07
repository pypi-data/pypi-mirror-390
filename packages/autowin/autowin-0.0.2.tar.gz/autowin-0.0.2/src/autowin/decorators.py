# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-05T06:10:38.402Z
# 文件描述：autowin 模块的装饰器，主要包含重试机制。
# 文件路径：src/autowin/decorators.py

import time
from functools import wraps
from typing import Callable, Tuple, Type, Any
from .config import settings
from .logger import logger
from .exceptions import AutoWinError

def retry(attempts: int = settings.MAX_RETRIES, delay: float = settings.RETRY_DELAY, backoff: float = settings.RETRY_BACKOFF, exceptions: Tuple[Type[Exception], ...] = (AutoWinError,)) -> Callable:
    """
    一个用于自动化操作的重试装饰器。
    当被装饰的函数抛出指定异常时，会自动进行重试。

    :param attempts: 重试的次数。
    :param delay: 每次重试之间的延迟（秒）。
    :param exceptions: 一个元组，包含需要捕获并重试的异常类型。
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            _attempts = 0
            current_delay = delay
            last_exception = None # 用于存储最后一次捕获的异常
            while _attempts < attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e # 捕获异常
                    _attempts += 1
                    logger.warning(f"⚠️ 函数 '{func.__name__}' 执行失败 (第 {_attempts}/{attempts} 次尝试): {e}")
                    if _attempts < attempts:
                        time.sleep(current_delay)
                        current_delay *= backoff # 应用指数退避
            logger.error(f"❌ 函数 '{func.__name__}' 达到最大重试次数 ({attempts}) 后仍然失败。")
            if last_exception:
                raise last_exception # 重新抛出最后一次捕获的异常
            else:
                # 理论上不会走到这里，除非 exceptions 为空或捕获了非 AutoWinError
                raise AutoWinError(f"函数 '{func.__name__}' 在重试后失败，但未捕获到具体异常。")
        return wrapper
    return decorator