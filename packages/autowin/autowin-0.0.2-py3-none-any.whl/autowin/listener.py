# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-05T07:02:56.846Z
# 文件描述：autowin 模块的鼠标、键盘和剪贴板监听功能。
# 文件路径：src/autowin/listener.py

import time
import pyperclip
import threading
from typing import Callable, Optional, List, Union
from pynput import (mouse, keyboard)

from .logger import logger

class MouseKeyboardClipboardListener:
    """
    监听鼠标、键盘和剪贴板的变化
    官网文档：https://pynput.readthedocs.io/en/latest/
    """
    def __init__(self, listen_name: str = 'AutoWinListener'):
        """
        初始化 MouseKeyboardClipboardListener 类。

        :param listen_name: 监听实例的名称，用于日志记录。
        """
        self.listen_name = listen_name
        self.mouse_listener: Optional[mouse.Listener] = None
        self.keyboard_listener: Optional[keyboard.Listener] = None
        self.clipboard_thread: Optional[threading.Thread] = None
        self.hotkey_listener: Optional[keyboard.GlobalHotKeys] = None
        self.stop_event = threading.Event()  # 用于控制监听的停止事件
        self.stop_key: Union[str, keyboard.Key] = keyboard.Key.esc  # 默认停止键为Esc键
        logger.debug(f"✨ {self.listen_name} 监听模块初始化。")

    def start(self, target: str, **kwargs):
        """
        统一的监听启动方法。

        :param target: 监听目标，可选 'clipboard', 'mouse', 'keyboard', 'hotkey'。
        :param kwargs: 传递给具体监听启动方法的参数。
        :return: 监听器实例。
        """
        if target == 'clipboard':
            return self.start_listen_clipboard(on_change=kwargs.get('on_change'), interval=kwargs.get('interval', 0.5))
        elif target == 'mouse':
            return self.start_listen_mouse(on_move=kwargs.get('on_move'), on_click=kwargs.get('on_click'), on_scroll=kwargs.get('on_scroll'))
        elif target == 'keyboard':
            return self.start_listen_keyboard(on_press=kwargs.get('on_press'), on_release=kwargs.get('on_release'), stop_key=kwargs.get('stop_key'))
        elif target == 'hotkey':
            return self.start_listen_hotkey(hotkeys=kwargs.get('hotkey'), callback=kwargs.get('on_activate'))
        else:
            raise ValueError(f"无效的监听目标: {target}")

    def stop(self, listener_instance):
        """
        统一的监听停止方法。

        :param listener_instance: 由 start 方法返回的监听器实例。
        """
        if isinstance(listener_instance, mouse.Listener):
            self.stop_mouse_listener()
        elif isinstance(listener_instance, keyboard.Listener):
            self.stop_keyboard_listener()
        elif isinstance(listener_instance, threading.Thread): # Clipboard listener
            self.stop_clipboard_listener()
        elif isinstance(listener_instance, keyboard.GlobalHotKeys):
            self.stop_hotkey_listener()
        else:
            logger.warning("提供的实例不是一个有效的监听器，尝试全部停止。")
            self.stop_all_listening()

    def stop_keyboard_on_press(self, key):
        """
        键盘按下时的回调函数，判断是否按下自定义停止键。
        :param key: 按下的键
        """
        if key == self.stop_key:
            self.stop_all_listening()  # 直接调用停止监听方法
            logger.info(f"{self.listen_name} -> 检测到停止键 {self.stop_key}，所有监听已停止。")

    @property
    def clipboard_data(self) -> str:
        """获取剪贴板数据"""
        return pyperclip.paste()

    def listen_clipboard_base(self, callback: Callable[[str], bool], interval: float = 0.5):
        """
        启动剪贴板监听的基础函数。
        :param callback: 剪贴板变化时的回调函数，用户需要根据需求自行编写。返回 False 可停止监听。
        :param interval: 监听间隔，单位为秒。
        """
        recent_data = self.clipboard_data
        while not self.stop_event.is_set():
            now_data = self.clipboard_data
            if now_data != recent_data:
                logger.debug(f"{self.listen_name} -> 剪贴板内容变化。")
                recent_data = now_data
                reply = callback(now_data)
                if not reply:
                    logger.info(f"{self.listen_name} -> 剪贴板回调函数返回 False，停止监听。")
                    break
            time.sleep(interval)
        logger.info(f"{self.listen_name} -> 剪贴板监听基础函数停止运行。")

    def start_listen_clipboard(self, on_change: Callable[[str], bool], interval: float = 0.5) -> threading.Thread:
        """
        启动剪贴板监听，并在新线程中运行。

        :param on_change: 剪贴板变化时的回调函数，用户需要根据需求自行编写。
        :param interval: 监听间隔，单位为秒。
        :return: 剪贴板监听线程。
        """
        if self.clipboard_thread and self.clipboard_thread.is_alive():
            logger.warning(f"{self.listen_name} -> 剪贴板监听已在运行。")
            return self.clipboard_thread
        self.stop_event.clear() # 确保停止事件是清除状态
        self.clipboard_thread = threading.Thread(target=self.listen_clipboard_base, args=(on_change, interval))
        self.clipboard_thread.daemon = True # 设置为守护线程，主程序退出时自动终止
        self.clipboard_thread.start()
        logger.info(f"{self.listen_name} -> 剪贴板监听已启动。")
        return self.clipboard_thread

    def start_listen_mouse(self, on_move: Optional[Callable] = None, on_click: Optional[Callable] = None,
                           on_scroll: Optional[Callable] = None) -> mouse.Listener:
        """
        启动鼠标监听，并在新线程中运行。

        :param on_move: 鼠标移动时的回调函数。
        :param on_click: 鼠标点击时的回调函数。
        :param on_scroll: 鼠标滚动时的回调函数。
        :return: 鼠标监听器实例。
        """
        if self.mouse_listener and self.mouse_listener.is_alive():
            logger.warning(f"{self.listen_name} -> 鼠标监听已在运行。")
            return self.mouse_listener
        self.mouse_listener = mouse.Listener(
            on_move=on_move,
            on_click=on_click,
            on_scroll=on_scroll
        )
        self.mouse_listener.daemon = True
        self.mouse_listener.start()
        logger.info(f"{self.listen_name} -> 鼠标监听已启动。")
        return self.mouse_listener

    def start_listen_keyboard(self, on_press: Optional[Callable] = None, on_release: Optional[Callable] = None,
                              stop_key: Optional[Union[str, keyboard.Key]] = keyboard.Key.esc) -> keyboard.Listener:
        """
        启动键盘监听，并在新线程中运行。

        :param on_press: 键盘按下时的回调函数。
        :param on_release: 键盘释放时的回调函数。
        :param stop_key: 自定义停止监听的按键，默认为Esc键。
        :return: 键盘监听器实例。
        """
        if self.keyboard_listener and self.keyboard_listener.is_alive():
            logger.warning(f"{self.listen_name} -> 键盘监听已在运行。")
            return self.keyboard_listener
        self.stop_key = stop_key
        self.keyboard_listener = keyboard.Listener(on_press=on_press or self.stop_keyboard_on_press,
                                                   on_release=on_release)
        self.keyboard_listener.daemon = True
        self.keyboard_listener.start()
        logger.info(f"{self.listen_name} -> 键盘监听已启动。")
        return self.keyboard_listener

    def start_listen_hotkey(self, hotkeys: List[str], callback: Callable) -> keyboard.GlobalHotKeys:
        """
        启动热键监听。

        :param hotkeys: 快捷键列表，如 ['ctrl', 'shift', 'a']。
        :param callback: 热键触发时的回调函数。
        :return: 热键监听器实例。
        """
        if self.hotkey_listener and self.hotkey_listener.is_alive():
            logger.warning(f"{self.listen_name} -> 热键监听已在运行。")
            return self.hotkey_listener
        hot_key_str = '+'.join(f"<{key}>" for key in hotkeys)
        self.hotkey_listener = keyboard.GlobalHotKeys({hot_key_str: callback})
        self.hotkey_listener.daemon = True
        self.hotkey_listener.start()
        logger.info(f"{self.listen_name} -> 热键监听 {hot_key_str} 已启动。")
        return self.hotkey_listener

    def stop_all_listening(self) -> None:
        """
        停止所有正在运行的监听器。
        """
        logger.info(f"{self.listen_name} -> 尝试停止所有监听器...")
        self.stop_event.set()  # 设置停止事件以停止剪贴板线程

        if self.mouse_listener and self.mouse_listener.is_alive():
            self.mouse_listener.stop()
            self.mouse_listener = None
            logger.info(f"{self.listen_name} -> 鼠标监听已停止。")

        if self.keyboard_listener and self.keyboard_listener.is_alive():
            self.keyboard_listener.stop()
            self.keyboard_listener = None
            logger.info(f"{self.listen_name} -> 键盘监听已停止。")
        
        if self.clipboard_thread and self.clipboard_thread.is_alive():
            self.clipboard_thread.join(timeout=1.0) # 等待线程结束，设置超时
            if self.clipboard_thread.is_alive():
                logger.warning(f"{self.listen_name} -> 剪贴板线程未能正常停止。")
            self.clipboard_thread = None
            logger.info(f"{self.listen_name} -> 剪贴板监听已停止。")

        if self.hotkey_listener and self.hotkey_listener.is_alive():
            self.hotkey_listener.stop()
            self.hotkey_listener = None
            logger.info(f"{self.listen_name} -> 热键监听已停止。")

        logger.info(f'{self.listen_name} -> 所有监听已停止。')

    def stop_mouse_listener(self) -> None:
        """单独停止鼠标监听。"""
        if self.mouse_listener and self.mouse_listener.is_alive():
            self.mouse_listener.stop()
            self.mouse_listener = None
            logger.info(f'{self.listen_name} -> 鼠标监听已停止。')
        else:
            logger.debug(f'{self.listen_name} -> 鼠标监听未运行。')

    def stop_keyboard_listener(self) -> None:
        """单独停止键盘监听。"""
        if self.keyboard_listener and self.keyboard_listener.is_alive():
            self.keyboard_listener.stop()
            self.keyboard_listener = None
            logger.info(f'{self.listen_name} -> 键盘监听已停止。')
        else:
            logger.debug(f'{self.listen_name} -> 键盘监听未运行。')

    def stop_clipboard_listener(self) -> None:
        """单独停止剪贴板监听。"""
        if self.clipboard_thread and self.clipboard_thread.is_alive():
            self.stop_event.set()
            self.clipboard_thread.join(timeout=1.0)
            if self.clipboard_thread.is_alive():
                logger.warning(f"{self.listen_name} -> 剪贴板线程未能正常停止。")
            self.clipboard_thread = None
            logger.info(f'{self.listen_name} -> 剪贴板监听已停止。')
        else:
            logger.debug(f'{self.listen_name} -> 剪贴板监听未运行。')

    def stop_hotkey_listener(self) -> None:
        """单独停止热键监听。"""
        if self.hotkey_listener and self.hotkey_listener.is_alive():
            self.hotkey_listener.stop()
            self.hotkey_listener = None
            logger.info(f'{self.listen_name} -> 热键监听已停止。')
        else:
            logger.debug(f'{self.listen_name} -> 热键监听未运行。')

# 提供一个监听模块的实例
listener = MouseKeyboardClipboardListener()