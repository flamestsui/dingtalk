import logging
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import json
import functools
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.notify import (
    BaseNotificationService,
    ATTR_MESSAGE,
    ATTR_TITLE,
    ATTR_DATA,
    ATTR_TARGET,
    DOMAIN as NOTIFY_DOMAIN,
)

# 集成唯一标识
DOMAIN = "dingtalk"
# 配置项键名（与config_flow.py一致）
CONF_WEBHOOK = "webhook"
CONF_SECRET = "secret"

_LOGGER = logging.getLogger(__name__)
DIVIDER = "———————————"


class DingtalkNotificationService(BaseNotificationService):
    """钉钉机器人通知服务实现"""

    def __init__(self, webhook: str, secret: str):
        self._webhook = webhook
        self._secret = secret.strip()  # 移除首尾空格
        _LOGGER.debug(f"钉钉机器人初始化，Webhook: {webhook[:20]}...")

    def _sign(self, timestamp: str) -> str:
        """生成签名（钉钉机器人安全设置）"""
        if not self._secret:
            return ""
        secret_enc = self._secret.encode("utf-8")
        string_to_sign = f"{timestamp}\n{self._secret}"
        string_to_sign_enc = string_to_sign.encode("utf-8")
        hmac_code = hmac.new(
            secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
        ).digest()
        return urllib.parse.quote_plus(base64.b64encode(hmac_code))

    def send_message(self, message: str = "", **kwargs):
        """同步发送通知（由异步方法包装）"""
        # 1. 准备基础参数
        timestamp = str(round(time.time() * 1000))
        sign = self._sign(timestamp)
        send_url = self._webhook

        # 2. 处理签名（若有密钥则拼接URL参数）
        if sign:
            send_url += f"&timestamp={timestamp}&sign={sign}"

        # 3. 解析消息参数
        title = kwargs.get(ATTR_TITLE)
        data = kwargs.get(ATTR_DATA) or {}
        msgtype = data.get("type", "text").lower()  # 消息类型（小写处理）
        url = data.get("url", "")
        picurl = data.get("picurl", "")
        atmoblies = kwargs.get(ATTR_TARGET)  # @指定用户的手机号列表

        # 4. 构建消息内容（按钉钉API格式）
        try:
            if msgtype == "text":
                content = ""
                if title:
                    content += f"{title}\n{DIVIDER}\n"
                content += message
                msg = {"content": content}

            elif msgtype == "markdown":
                msg = {"title": title or "通知", "text": message}

            elif msgtype == "link":
                msg = {
                    "title": title or "通知",
                    "text": message,
                    "picUrl": picurl,
                    "messageUrl": url
                }

            elif msgtype == "actioncard":
                msg = {
                    "title": title or "通知",
                    "text": message,
                    "btnOrientation": "0",
                    "singleTitle": "阅读全文",
                    "singleURL": url
                }

            else:
                _LOGGER.error(f"不支持的消息类型：{msgtype}，请使用 text/link/markdown/actionCard")
                return

        except Exception as e:
            _LOGGER.error(f"构建消息失败：{str(e)}")
            return

        # 5. 构建完整请求体
        send_values = {
            "at": {
                "atMobiles": atmoblies or [],
                "atUserIds": [],
                "isAtAll": "false"
            },
            "msgtype": msgtype,
            msgtype: msg
        }

        # 6. 发送请求
        try:
            response = requests.post(
                send_url,
                data=json.dumps(send_values),
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()  # 捕获HTTP错误
            result = response.json()

            if result.get("errcode") != 0:
                _LOGGER.error(f"发送失败：{result.get('errmsg', '未知错误')}（错误码：{result.get('errcode')}）")
            else:
                _LOGGER.debug(f"发送成功：{result}")

        except requests.exceptions.RequestException as e:
            _LOGGER.error(f"网络请求失败：{str(e)}")
        except json.JSONDecodeError:
            _LOGGER.error(f"响应格式错误，原始内容：{response.text[:200]}")
        except Exception as e:
            _LOGGER.error(f"发送异常：{str(e)}")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """加载配置项并注册服务（添加日志调试）"""
    _LOGGER.debug("开始加载钉钉集成配置项...")  # 新增日志
    
    # 注册配置更新监听
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    # 定义服务处理函数
    async def async_handle_service(call: ServiceCall) -> None:
        webhook = entry.data[CONF_WEBHOOK]
        secret = entry.data.get(CONF_SECRET, "")
        service = DingtalkNotificationService(webhook, secret)
        
        message = call.data.get(ATTR_MESSAGE, "")
        other_kwargs = call.data.copy()
        other_kwargs.pop(ATTR_MESSAGE, None)
        
        send_func = functools.partial(
            service.send_message,
            message=message,** other_kwargs
        )
        await hass.async_add_executor_job(send_func)

    # 注册服务（关键步骤）
    hass.services.async_register(NOTIFY_DOMAIN, DOMAIN, async_handle_service)
    _LOGGER.debug(f"服务注册成功：{NOTIFY_DOMAIN}.{DOMAIN}")  # 新增日志，确认服务名
    
    return True  # 必须返回True，否则配置项加载失败


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """卸载配置项（移除服务）"""
    hass.services.async_remove(NOTIFY_DOMAIN, DOMAIN)
    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """配置更新后重新加载服务"""
    await hass.config_entries.async_reload(entry.entry_id)