# -*- coding: utf-8 -*-
# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-07T03:55:00.000Z
# 文件描述：企业微信消息发送模块，支持 Webhook 模式和应用消息模式。
# 文件路径：src/autowin/message.py

import httpx
import json
import time
from typing import Optional, List, Dict, Any

class WeChatSender:
    """
    企业微信消息发送器，支持 Webhook 模式和应用消息模式。
    """
    def __init__(self, webhook_url: Optional[str] = None, corp_id: Optional[str] = None, agent_id: Optional[str] = None, corp_secret: Optional[str] = None):
        """
        初始化 WeChatSender。
        :param webhook_url: 企业微信群机器人的 Webhook URL。
        :param corp_id: 企业微信的企业 ID。
        :param agent_id: 企业微信应用的消息 AgentID。
        :param corp_secret: 企业微信应用的 Secret。
        """
        self.webhook_url: Optional[str] = webhook_url
        self.corp_id: Optional[str] = corp_id
        self.agent_id: Optional[str] = agent_id
        self.corp_secret: Optional[str] = corp_secret
        self._access_token: Optional[str] = None
        self._access_token_expires_at: float = 0

        if not self.webhook_url and not (self.corp_id and self.agent_id and self.corp_secret):
            raise ValueError("❌ 必须提供 webhook_url 或 (corp_id, agent_id, corp_secret) 之一。")
        
    def _get_access_token(self) -> str:
        """
        获取企业微信的 access_token。
        :return: 企业微信的 access_token。
        :raises Exception: 如果获取 access_token 失败。
        """
        if self._access_token and self._access_token_expires_at > time.time():
            return self._access_token

        url: str = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corp_id}&corpsecret={self.corp_secret}"
        try:
            response: httpx.Response = httpx.get(url)
            response.raise_for_status()
            result: Dict[str, Any] = response.json()
            if result.get("errcode") == 0:
                self._access_token = result["access_token"]
                self._access_token_expires_at = time.time() + result["expires_in"] - 60  # 提前60秒过期
                return self._access_token
            else:
                raise Exception(f"❌ 获取 access_token 失败: {result.get('errmsg')}")
        except httpx.RequestError as e:
            raise Exception(f"❌ 请求 access_token 失败: {e}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"❌ HTTP 错误，获取 access_token 失败: {e.response.status_code} - {e.response.text}")

    def send_message(self, content: str, msg_type: str = "text", mentioned_list: Optional[List[str]] = None, mentioned_mobile_list: Optional[List[str]] = None, to_user: str = "@all") -> Dict[str, Any]:
        """
        发送企业微信消息。
        :param content: 消息内容。
        :param msg_type: 消息类型，目前支持 "text" 和 "markdown"。
        :param mentioned_list: 需要 @ 的成员 ID 列表。
        :param mentioned_mobile_list: 需要 @ 的成员手机号列表。
        :param to_user: 消息接收者，可以是用户 ID 或 "@all"。
        :return: 包含发送结果的字典。
        """
        headers: Dict[str, str] = {'Content-Type': 'application/json'}
        data: Dict[str, Any] = {
            "msgtype": msg_type,
            msg_type: {"content": content}
        }

        if msg_type == "text" or msg_type == "markdown":
            if mentioned_list:
                data[msg_type]["mentioned_list"] = mentioned_list
            if mentioned_mobile_list:
                data[msg_type]["mentioned_mobile_list"] = mentioned_mobile_list
        else:
            raise ValueError("❌ 不支持的消息类型。目前只支持 'text' 和 'markdown'。")

        try:
            if self.webhook_url:
                response: httpx.Response = httpx.post(self.webhook_url, headers=headers, content=json.dumps(data))
            else:
                access_token: str = self._get_access_token()
                url: str = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
                data["agentid"] = self.agent_id
                data["touser"] = to_user
                response: httpx.Response = httpx.post(url, headers=headers, content=json.dumps(data))
            
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            return {"errcode": -1, "errmsg": f"❌ 请求失败: {e}"}
        except httpx.HTTPStatusError as e:
            return {"errcode": -1, "errmsg": f"❌ HTTP 错误: {e.response.status_code} - {e.response.text}"}
        except Exception as e:
            return {"errcode": -1, "errmsg": f"❌ 发生未知错误: {e}"}
