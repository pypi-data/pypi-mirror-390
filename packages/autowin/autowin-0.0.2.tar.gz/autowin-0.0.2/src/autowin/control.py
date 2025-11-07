# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-05T06:12:08.444Z
# 文件描述：autowin 模块的控件操作封装。
# 文件路径：src/autowin/control.py

from typing import Any, Optional, Union, Dict
from pywinauto.controls.uia_controls import EditWrapper, ButtonWrapper, ComboBoxWrapper
from pywinauto.findwindows import ElementNotFoundError
# 移除了 CheckBoxWrapper, ListItemWrapper, ListViewWrapper 的直接导入，
# 因为它们在 pywinauto 0.6.9+ 版本中可能不再直接从 uia_controls 导出。
# 将通过更通用的方式处理这些控件类型。

from .core import core
from .logger import logger
from .decorators import retry
from .exceptions import ControlNotFoundError, AutoWinInputError

class AutoWinControl:
    """
    autowin 模块的控件操作类。
    封装了 pywinauto 对控件的常用操作，并加入了日志和重试机制。
    """
    def __init__(self):
        logger.debug("✨ autowin 控件模块初始化。")

    @retry(exceptions=(ControlNotFoundError, ElementNotFoundError))
    def get_control(self, parent_window: Any, control_type: Optional[str] = None,
                    title: Optional[str] = None, auto_id: Optional[str] = None,
                    class_name: Optional[str] = None, regex: Optional[str] = None,
                    timeout: int = 10) -> Any:
        """
        在指定父窗口中查找并返回一个控件对象。

        :param parent_window: 父窗口对象 (pywinauto WindowSpecification)。
        :param control_type: 控件的类型（如 "Button", "Edit", "Pane"）。
        :param title: 控件的文本或标题。
        :param auto_id: 控件的自动化 ID。
        :param class_name: 控件的类名。
        :param regex: 用于匹配控件标题或类名的正则表达式。
        :param timeout: 查找控件的超时时间（秒）。
        :return: 找到的控件对象。
        :raises ControlNotFoundError: 如果在超时时间内未找到控件。
        """
        logger.debug(f"ℹ️ 尝试在窗口 '{parent_window.window_text()}' 中获取控件，条件: type='{control_type}', title='{title}', auto_id='{auto_id}', class_name='{class_name}', regex='{regex}', 超时: {timeout}s")
        control = core.find_control(parent_window, control_type=control_type, title=title,
                                    auto_id=auto_id, class_name=class_name, regex=regex, timeout=timeout)
        logger.info(f"✅ 成功获取控件: {control.window_text() if hasattr(control, 'window_text') else control.class_name()}")
        return control

    @retry(exceptions=ControlNotFoundError)
    def click_control(self, control_obj: Any) -> None:
        """
        点击指定的控件。

        :param control_obj: 控件对象。
        :raises ControlNotFoundError: 如果控件不存在或无法点击。
        """
        try:
            logger.debug(f"🖱️ 尝试点击控件: {control_obj.window_text() if hasattr(control_obj, 'window_text') else control_obj.class_name()}")
            control_obj.click()
            logger.info(f"✅ 成功点击控件: {control_obj.window_text() if hasattr(control_obj, 'window_text') else control_obj.class_name()}")
        except Exception as e:
            logger.error(f"❌ 点击控件失败: {control_obj.window_text() if hasattr(control_obj, 'window_text') else control_obj.class_name()} - {e}")
            raise ControlNotFoundError(f"点击控件失败: {e}")

    @retry(exceptions=ControlNotFoundError)
    def set_text(self, control_obj: Any, text: str) -> None:
        """
        向文本框控件输入文本。

        :param control_obj: 文本框控件对象 (e.g., EditWrapper)。
        :param text: 要输入的文本。
        :raises ControlNotFoundError: 如果控件不存在或不是文本输入类型。
        :raises AutoWinInputError: 如果输入文本失败。
        """
        try:
            logger.debug(f"⌨️ 尝试向控件 '{control_obj.window_text() if hasattr(control_obj, 'window_text') else control_obj.class_name()}' 输入文本: '{text}'")
            if isinstance(control_obj, EditWrapper):
                control_obj.set_text(text)
            else:
                control_obj.type_keys(text) # 对于非EditWrapper控件尝试使用type_keys
            logger.info(f"✅ 成功向控件 '{control_obj.window_text() if hasattr(control_obj, 'window_text') else control_obj.class_name()}' 输入文本。")
        except Exception as e:
            logger.error(f"❌ 向控件输入文本失败: {control_obj.window_text() if hasattr(control_obj, 'window_text') else control_obj.class_name()} - {e}")
            raise AutoWinInputError(f"向控件输入文本失败: {e}")

    @retry(exceptions=ControlNotFoundError)
    def get_text(self, control_obj: Any) -> str:
        """
        获取控件的文本内容。

        :param control_obj: 控件对象。
        :return: 控件的文本内容。
        :raises ControlNotFoundError: 如果控件不存在或没有文本内容。
        """
        try:
            text = control_obj.window_text()
            logger.debug(f"ℹ️ 获取控件 '{control_obj.class_name()}' 文本: '{text}'")
            return text
        except Exception as e:
            logger.error(f"❌ 获取控件文本失败: {control_obj.class_name()} - {e}")
            raise ControlNotFoundError(f"获取控件文本失败: {e}")

    @retry(exceptions=ControlNotFoundError)
    def select_item(self, control_obj: Any, item_text_or_index: Union[str, int]) -> None:
        """
        选择下拉列表、列表框或菜单中的项。

        :param control_obj: 控件对象 (e.g., ComboBoxWrapper, ListBoxWrapper, MenuWrapper)。
        :param item_text_or_index: 要选择的项的文本或索引。
        :raises ControlNotFoundError: 如果控件不存在或无法选择指定项。
        """
        try:
            logger.debug(f"ℹ️ 尝试在控件 '{control_obj.window_text() if hasattr(control_obj, 'window_text') else control_obj.class_name()}' 中选择项: '{item_text_or_index}'")
            # 对于 ComboBoxWrapper
            if control_obj.element_info.control_type == "ComboBox":
                control_obj.select(item_text_or_index)
            # 对于 ListItemWrapper 或 ListViewWrapper (通过 control_type 判断)
            elif control_obj.element_info.control_type in ["ListItem", "List"]:
                control_obj.select(item_text_or_index)
            # 对于其他可能包含菜单项的控件
            else:
                try:
                    control_obj.menu_item(item_text_or_index).click()
                except Exception:
                    # 如果不是菜单项，尝试直接点击或选择
                    control_obj.select(item_text_or_index) # 尝试通用select
            logger.info(f"✅ 成功在控件 '{control_obj.window_text() if hasattr(control_obj, 'window_text') else control_obj.class_name()}' 中选择项: '{item_text_or_index}'")
        except Exception as e:
            logger.error(f"❌ 选择控件项失败: {control_obj.window_text() if hasattr(control_obj, 'window_text') else control_obj.class_name()} - {e}")
            raise ControlNotFoundError(f"选择控件项失败: {e}")

    @retry(exceptions=ControlNotFoundError)
    def is_checked(self, control_obj: Any) -> bool:
        """
        检查复选框或单选按钮是否被选中。

        :param control_obj: 复选框或单选按钮控件对象 (e.g., CheckBoxWrapper, RadioButtonWrapper)。
        :return: 如果被选中则为 True，否则为 False。
        :raises ControlNotFoundError: 如果控件不存在或不是可检查类型。
        """
        try:
            # 使用 control_type 判断是否为 CheckBox
            if control_obj.element_info.control_type == "CheckBox":
                checked = control_obj.get_check_state() == 1
            else:
                # 尝试其他控件的通用 checked 属性，例如 ToggleState
                checked = control_obj.get_toggle_state() == 1 # UI Automation ToggleState
            logger.debug(f"ℹ️ 控件 '{control_obj.window_text() if hasattr(control_obj, 'window_text') else control_obj.class_name()}' 选中状态: {checked}")
            return checked
        except Exception as e:
            logger.error(f"❌ 检查控件选中状态失败: {control_obj.window_text() if hasattr(control_obj, 'window_text') else control_obj.class_name()} - {e}")
            raise ControlNotFoundError(f"检查控件选中状态失败: {e}")

    @retry(exceptions=ControlNotFoundError)
    def check_control(self, control_obj: Any) -> None:
        """
        选中复选框或单选按钮。

        :param control_obj: 复选框或单选按钮控件对象。
        :raises ControlNotFoundError: 如果控件不存在或无法选中。
        """
        try:
            logger.debug(f"ℹ️ 尝试选中控件: {control_obj.window_text() if hasattr(control_obj, 'window_text') else control_obj.class_name()}")
            # 使用 control_type 判断是否为 CheckBox
            if control_obj.element_info.control_type == "CheckBox":
                control_obj.check()
            else:
                control_obj.toggle() # 尝试通用切换状态
            logger.info(f"✅ 成功选中控件: {control_obj.window_text() if hasattr(control_obj, 'window_text') else control_obj.class_name()}")
        except Exception as e:
            logger.error(f"❌ 选中控件失败: {control_obj.window_text() if hasattr(control_obj, 'window_text') else control_obj.class_name()} - {e}")
            raise ControlNotFoundError(f"选中控件失败: {e}")

    @retry(exceptions=ControlNotFoundError)
    def uncheck_control(self, control_obj: Any) -> None:
        """
        取消选中复选框或单选按钮。

        :param control_obj: 复选框或单选按钮控件对象。
        :raises ControlNotFoundError: 如果控件不存在或无法取消选中。
        """
        try:
            logger.debug(f"ℹ️ 尝试取消选中控件: {control_obj.window_text() if hasattr(control_obj, 'window_text') else control_obj.class_name()}")
            # 使用 control_type 判断是否为 CheckBox
            if control_obj.element_info.control_type == "CheckBox":
                control_obj.uncheck()
            else:
                control_obj.toggle() # 尝试通用切换状态
            logger.info(f"✅ 成功取消选中控件: {control_obj.window_text() if hasattr(control_obj, 'window_text') else control_obj.class_name()}")
        except Exception as e:
            logger.error(f"❌ 取消选中控件失败: {control_obj.window_text() if hasattr(control_obj, 'window_text') else control_obj.class_name()} - {e}")
            raise ControlNotFoundError(f"取消选中控件失败: {e}")

    def get_properties(self, control_obj: Any) -> Dict[str, Any]:
        """
        获取控件的所有可用属性。

        :param control_obj: 控件对象。
        :return: 包含控件属性的字典。
        """
        properties = {}
        try:
            properties['class_name'] = control_obj.class_name()
            properties['window_text'] = control_obj.window_text()
            properties['control_id'] = control_obj.control_id()
            properties['automation_id'] = control_obj.automation_id()
            properties['framework_id'] = control_obj.framework_id()
            properties['rectangle'] = control_obj.rectangle().as_rect()
            properties['is_enabled'] = control_obj.is_enabled()
            properties['is_visible'] = control_obj.is_visible()
            properties['control_type'] = control_obj.friendly_class_name() # 或者 control_obj.element_info.control_type
            logger.debug(f"ℹ️ 获取控件 '{properties.get('window_text', properties['class_name'])}' 属性: {properties}")
        except Exception as e:
            logger.warning(f"⚠️ 获取控件部分属性失败: {e}")
        return properties

# 提供一个控件模块的实例
control = AutoWinControl()