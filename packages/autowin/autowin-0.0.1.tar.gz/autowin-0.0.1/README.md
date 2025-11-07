# ✨ AutoWin: 基于 pywinauto 和 pyautogui 的 Windows 自动化库

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Poetry](https://img.shields.io/badge/Poetry-Enabled-brightgreen)](https://python-poetry.org/)

## 📝 项目简介

AutoWin 是一个强大且易用的 Windows 自动化库，它封装了 [`pywinauto`](https://pywinauto.readthedocs.io/en/latest/) 和 [`pyautogui`](https://pyautogui.readthedocs.io/en/latest/) 的核心功能，并提供了一套统一、高层的 API。通过 AutoWin，开发者可以轻松实现 Windows 桌面应用程序的自动化操作，包括窗口管理、UI 控件交互、鼠标键盘模拟、屏幕截图与图像识别以及剪贴板操作。

AutoWin 的设计理念是提供一个健壮、可靠且用户友好的自动化解决方案，内置了日志记录、重试机制和完善的错误处理，以应对自动化过程中可能遇到的各种复杂情况。

## 🚀 主要特性

*   **统一 API**: 整合 `pywinauto` 和 `pyautogui`，提供简洁一致的接口。
*   **窗口操作**: 查找、激活、最大化、最小化、恢复、关闭、移动、调整窗口大小。
*   **控件交互**: 查找、点击按钮、输入文本、选择列表项、操作复选框等。
*   **鼠标键盘**: 模拟点击、双击、右键、拖拽、滚动、输入文本、按键组合。
*   **屏幕感知**: 截取屏幕、在屏幕上查找图像并点击。
*   **剪贴板**: 复制文本到剪贴板，从剪贴板粘贴文本。
*   **应用管理**: 启动应用程序、打开URL、获取网页标题。
*   **事件监听**: 监听鼠标、键盘事件和剪贴板内容变化，支持热键设置。
*   **健壮性**: 内置可配置的重试机制（支持重试次数、延迟和指数退避），提高操作成功率，确保自动化流程的稳定执行。
*   **应用与窗口管理**: 改进应用程序启动逻辑，确保应用程序及其主窗口在操作前完全就绪；提供更精确的窗口查找和获取方式，支持通过进程关联获取顶级窗口。
*   **控件信息**: 提供简洁的 API (`print_control_info`)，用于打印窗口中所有控件的详细标识符，方便UI自动化定位。
*   **可观测性**: 完善的日志系统，记录自动化脚本的执行过程和关键信息。
*   **错误处理**: 详细的自定义异常，帮助快速定位和解决问题。
*   **灵活配置**: 支持通过全局配置调整模块行为（如超时时间、日志级别、重试策略）。

## 📦 安装

您可以通过 `pip` 直接安装 AutoWin：

```bash
pip install autowin
```

### 从源代码安装 (使用 Poetry)

如果您希望从源代码安装或进行开发，AutoWin 使用 [Poetry](https://python-poetry.org/) 进行项目管理和依赖安装。请确保您的系统已安装 Poetry。

1.  **克隆仓库**:
    ```bash
    git clone https://github.com/your_username/autowin.git
    cd autowin
    ```

2.  **安装依赖**:
    ```bash
    poetry install
    ```

3.  **激活虚拟环境**:
    ```bash
    poetry shell
    ```

## 💡 使用示例

以下是一些基本的 AutoWin 使用示例。

```python
from autowin import core, window, input as autowin_input, screenshot, clipboard, vision, listener, application, settings, logger
from autowin.exceptions import WindowNotFoundError, ImageNotFoundError, ClipboardError
import time
import logging # 导入logging模块
from pynput import keyboard # 导入 keyboard 模块

# 配置日志级别 (可选)
settings.LOG_LEVEL = logging.DEBUG
# 或者直接通过 logger 对象设置
# logger.setLevel(logging.DEBUG)

def on_clipboard_change(text: str) -> bool:
    """剪贴板内容变化时的回调函数。"""
    logger.info(f"📋 剪贴板内容变化: {text[:50]}...")
    return True # 返回 True 继续监听

def on_key_press(key):
    """键盘按下时的回调函数。"""
    print(f"DEBUG: 键盘按下事件捕获到：{key}") # 添加直接打印，排除日志问题
    try:
        logger.debug(f"⌨️ 按下: {key.char}")
    except AttributeError:
        logger.debug(f"⌨️ 按下特殊键: {key}")
    
    # 如果按下 Esc 键，停止所有监听
    if key == keyboard.Key.esc:
        logger.info("检测到 Esc 键，停止监听。")
        listener.stop_all_listening()

def run_notepad_automation():
    logger.info("--- 开始记事本自动化测试 ---")
    try:
        # 启动记事本应用
        app = application.start_application(r"C:\Windows\System32\notepad.exe")
        
        # 获取记事本主窗口
        notepad_window = window.get_window(title="无标题 - 记事本", regex=r".* - 记事本")
        window.activate(notepad_window)

        # 设置窗口置顶
        window.set_topmost(notepad_window)
        
        # 查找文本编辑区
        edit_control = core.find_control(notepad_window, class_name="Edit")
        
        # 输入文本
        autowin_input.type_text("你好，AutoWin! 这是自动化测试。\n")
        autowin_input.type_text("剪贴板测试:\n")

        # 剪贴板操作
        test_text = "这是一段从剪贴板粘贴的文本。"
        clipboard.copy(test_text)
        autowin_input.hotkey('ctrl', 'v') # 粘贴
        autowin_input.press_key('enter')

        # 模拟键盘输入更多文本
        autowin_input.type_text("现在模拟按键操作：")
        autowin_input.press_key('capslock')
        autowin_input.type_text("HELLO WORLD")
        autowin_input.press_key('capslock')
        autowin_input.press_key('enter')

        # 模拟鼠标点击菜单 (需要根据实际UI结构调整)
        # 例如，点击“文件”菜单
        # file_menu = core.find_control(notepad_window, title="文件", control_type="MenuItem")
        # control.click_control(file_menu)
        # time.sleep(1)
        # save_menu_item = core.find_control(notepad_window, title="保存(S)", control_type="MenuItem")
        # control.click_control(save_menu_item)
 
        # 屏幕截图示例
        screenshot.take_screenshot(filename="notepad_content.png", region=(0, 0, 800, 600))

        # 图像识别示例
        # 假设你有一个名为 "save_button.png" 的图片，表示记事本中的“保存”按钮
        # if vision.wait_for_image("save_button.png", timeout=5):
        #     vision.click_image("save_button.png")
        #     logger.info("成功点击保存按钮。")
        
        # 暂停以便观察
        time.sleep(3)

        # 取消窗口置顶
        window.remove_topmost(notepad_window)

        # 关闭记事本
        window.close(notepad_window)
        # 可能会弹出保存提示，这里简单处理为不保存
        # save_prompt = window.get_window(title="记事本", regex=r".*记事本", timeout=5)
        # if save_prompt:
        #     no_button = core.find_control(save_prompt, title="不保存(N)", control_type="Button")
        #     control.click_control(no_button)
        
    except WindowNotFoundError as e:
        logger.error(f"❌ 窗口未找到错误: {e}")
    except ImageNotFoundError as e:
        logger.error(f"❌ 图像未找到错误: {e}")
    except ClipboardError as e:
        logger.error(f"❌ 剪贴板错误: {e}")
    except Exception as e:
        logger.error(f"❌ 发生未知错误: {e}")
    finally:
        logger.info("--- 记事本自动化测试结束 ---")

if __name__ == "__main__":
    # 启动剪贴板监听
    listener.start_listen_clipboard(on_clipboard_change, interval=1)
    
    # 启动键盘监听
    keyboard_listener = listener.start_listen_keyboard(on_press=on_key_press, stop_key=None)
    
    # 保持主线程活跃，以便监听器可以运行
    print("键盘监听已启动。按 Esc 键停止...")
    keyboard_listener.join() # 阻塞主线程直到监听器停止

    # 运行记事本自动化测试
    # run_notepad_automation()

    # 停止所有监听 (如果需要手动停止，可以在这里调用)
    listener.stop_all_listening()
```

## 📚 模块文档

以下是 AutoWin 各个功能模块的详细文档：

*   [Application 模块](docs/application.md)
*   [Clipboard 模块](docs/clipboard.md)
*   [Config 模块](docs/config.md)
*   [Control 模块](docs/control.md)
*   [Core 模块](docs/core.md)
*   [Decorators 模块](docs/decorators.md)
*   [Exceptions 模块](docs/exceptions.md)
*   [Input 模块](docs/input.md)
*   [Listener 模块](docs/listener.md)
*   [Logger 模块](docs/logger.md)
*   [Screenshot 模块](docs/screenshot.md)
*   [Utils 模块](docs/utils.md)
*   [Vision 模块](docs/vision.md)
*   [Window 模块](docs/window.md)

## ️ 开发与贡献

欢迎通过 Pull Request 贡献代码，或提交 Issue 报告 Bug 和提出新功能建议。

### 代码风格

本项目遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范。


## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## ❤️ 鸣谢

*   [pywinauto](https://pywinauto.readthedocs.io/en/latest/): 强大的 Windows GUI 自动化库。
*   [pyautogui](https://pyautogui.readthedocs.io/en/latest/): 跨平台的 GUI 自动化工具。
*   [pyperclip](https://pyperclip.readthedocs.io/en/latest/): 跨平台剪贴板模块。
*   [Pillow](https://python-pillow.org/): Python 图像处理库。

---
**作者**: Xiaoqiang  
**微信公众号**: XiaoqiangClub