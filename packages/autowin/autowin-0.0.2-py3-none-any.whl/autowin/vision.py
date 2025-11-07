# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-05T06:56:02.738Z
# 文件描述：autowin 模块的图像识别和自动化功能。
# 文件路径：src/autowin/vision.py

import time
from typing import Tuple, Optional

import pyautogui

from .config import settings
from .exceptions import ImageNotFoundError
from .logger import logger
from .input import input_

class Vision:
    """
    提供图像识别和自动化功能。
    """

    def find_image_on_screen(
        self,
        image_path: str,
        confidence: Optional[float] = None,
        region: Optional[Tuple[int, int, int, int]] = None,
        timeout: Optional[int] = None
    ) -> Tuple[int, int, int, int]:
        """
        在屏幕上查找指定的图像。

        :param image_path: 图像文件的路径。
        :param confidence: (可选) 匹配的置信度（0.0到1.0），默认为配置中的 SCREENSHOT_CONFIDENCE。
        :param region: (可选) 查找图像的屏幕区域 (left, top, width, height)。
        :param timeout: (可选) 查找图像的超时时间（秒），默认为配置中的 DEFAULT_TIMEOUT。
        :return: 如果找到图像，返回图像在屏幕上的 (left, top, width, height) 坐标。
        :raises ImageNotFoundError: 如果在超时时间内未找到图像。
        """
        confidence = confidence if confidence is not None else settings.SCREENSHOT_CONFIDENCE
        timeout = timeout if timeout is not None else settings.DEFAULT_TIMEOUT
        start_time = time.time()

        logger.info(f"ℹ️ 尝试在屏幕上查找图像: {image_path}, 置信度: {confidence}, 区域: {region}, 超时: {timeout}s")

        while time.time() - start_time < timeout:
            try:
                box = pyautogui.locateOnScreen(image_path, confidence=confidence, region=region)
                if box:
                    logger.info(f"✅ 成功找到图像: {image_path}, 坐标: {box}")
                    return tuple(box)
            except pyautogui.PyAutoGUIException as e:
                logger.debug(f"🔍 图像查找失败 (尝试中): {e}")
            time.sleep(0.5)  # 等待0.5秒后重试

        logger.error(f"❌ 在 {timeout}s 内未在屏幕上找到图像: {image_path}")
        raise ImageNotFoundError(
            message=f"未在屏幕上找到图像: {image_path}",
            image_path=image_path,
            confidence=confidence
        )

    def click_image(
        self,
        image_path: str,
        confidence: Optional[float] = None,
        region: Optional[Tuple[int, int, int, int]] = None,
        button: str = 'left',
        clicks: int = 1,
        interval: float = 0.0,
        timeout: Optional[int] = None
    ) -> None:
        """
        在屏幕上查找指定图像，并点击其中心。

        :param image_path: 图像文件的路径。
        :param confidence: (可选) 匹配的置信度。
        :param region: (可选) 查找图像的屏幕区域。
        :param button: (可选) 点击的鼠标按钮（'left', 'middle', 'right'），默认为 'left'。
        :param clicks: (可选) 点击次数，默认为 1。
        :param interval: (可选) 每次点击之间的间隔（秒）。
        :param timeout: (可选) 查找图像的超时时间。
        :raises ImageNotFoundError: 如果在超时时间内未找到图像。
        """
        logger.info(f"ℹ️ 尝试点击图像: {image_path}")
        box = self.find_image_on_screen(image_path, confidence, region, timeout)
        
        center_x = box[0] + box[2] // 2
        center_y = box[1] + box[3] // 2
        
        input_.click(x=center_x, y=center_y, button=button, clicks=clicks, interval=interval)
        logger.info(f"✅ 成功点击图像: {image_path}, 坐标: ({center_x}, {center_y})")

    def wait_for_image(
        self,
        image_path: str,
        confidence: Optional[float] = None,
        region: Optional[Tuple[int, int, int, int]] = None,
        timeout: Optional[int] = None
    ) -> bool:
        """
        等待直到指定图像出现在屏幕上。

        :param image_path: 图像文件的路径。
        :param confidence: (可选) 匹配的置信度。
        :param region: (可选) 查找图像的屏幕区域。
        :param timeout: (可选) 等待的超时时间（秒），默认为配置中的 DEFAULT_TIMEOUT。
        :return: 如果图像在超时时间内出现，返回 True，否则返回 False。
        """
        confidence = confidence if confidence is not None else settings.SCREENSHOT_CONFIDENCE
        timeout = timeout if timeout is not None else settings.DEFAULT_TIMEOUT
        start_time = time.time()

        logger.info(f"ℹ️ 等待图像出现: {image_path}, 超时: {timeout}s")

        while time.time() - start_time < timeout:
            try:
                box = pyautogui.locateOnScreen(image_path, confidence=confidence, region=region)
                if box:
                    logger.info(f"✅ 图像 {image_path} 已出现。")
                    return True
            except pyautogui.PyAutoGUIException:
                pass  # 图像未找到是预期行为，继续等待
            time.sleep(0.5)

        logger.warning(f"⚠️ 图像 {image_path} 在 {timeout}s 内未出现。")
        return False

    def wait_until_image_disappears(
        self,
        image_path: str,
        confidence: Optional[float] = None,
        region: Optional[Tuple[int, int, int, int]] = None,
        timeout: Optional[int] = None
    ) -> bool:
        """
        等待直到指定图像从屏幕上消失。

        :param image_path: 图像文件的路径。
        :param confidence: (可选) 匹配的置信度。
        :param region: (可选) 查找图像的屏幕区域。
        :param timeout: (可选) 等待的超时时间（秒），默认为配置中的 DEFAULT_TIMEOUT。
        :return: 如果图像在超时时间内消失，返回 True，否则返回 False。
        """
        confidence = confidence if confidence is not None else settings.SCREENSHOT_CONFIDENCE
        timeout = timeout if timeout is not None else settings.DEFAULT_TIMEOUT
        start_time = time.time()

        logger.info(f"ℹ️ 等待图像消失: {image_path}, 超时: {timeout}s")

        while time.time() - start_time < timeout:
            try:
                box = pyautogui.locateOnScreen(image_path, confidence=confidence, region=region)
                if not box:
                    logger.info(f"✅ 图像 {image_path} 已消失。")
                    return True
            except pyautogui.PyAutoGUIException:
                logger.debug(f"🔍 图像 {image_path} 未找到 (预期行为)。")
                return True # 图像未找到即认为已消失
            time.sleep(0.5)

        logger.warning(f"⚠️ 图像 {image_path} 在 {timeout}s 后仍未消失。")
        return False

# 提供一个 vision 模块的实例
vision = Vision()
