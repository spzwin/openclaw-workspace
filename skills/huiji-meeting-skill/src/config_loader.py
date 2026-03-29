# 配置加载 - 从 config/default.json 或环境变量读取
# AppKey 读取顺序与 common/auth.md 一致：1) 环境变量 XG_BIZ_API_KEY  2) 配置文件 appKey
import json
import os
from pathlib import Path

_config = None

def _default_config():
    return {
        "api_base_url": "https://sg-al-ai-voice-assistant.mediportal.com.cn/api/open-api/ai-huiji/meetingChat/chatListByPage",
        "split_record_url": "https://sg-al-ai-voice-assistant.mediportal.com.cn/api/open-api/ai-huiji/meetingChat/splitRecordList",
        "check_second_stt_url": "https://sg-al-ai-voice-assistant.mediportal.com.cn/api/open-api/ai-huiji/meetingChat/checkSecondSttV2",
        "report_info_url": "https://sg-al-ai-voice-assistant.mediportal.com.cn/api/open-api/ai-huiji/report/reportInfo",
        "app_key": os.environ.get("XG_BIZ_API_KEY", ""),
        "cache": {"ttl": 60000, "max_size": 100},
        "monitor": {"enabled": True, "interval": 30000, "threshold": 3},
        "notification": {"enabled": False, "webhook_url": "", "channels": ["console"]},
    }


def load_config():
    global _config
    if _config is not None:
        return _config
    root = Path(__file__).resolve().parent.parent
    config_path = root / "config" / "default.json"
    _config = _default_config()
    def _merge(data: dict) -> None:
        _config["api_base_url"] = data.get("apiBaseUrl", _config["api_base_url"])
        _config["split_record_url"] = data.get("splitRecordUrl", _config["split_record_url"])
        _config["check_second_stt_url"] = data.get("checkSecondSttUrl", _config["check_second_stt_url"])
        _config["report_info_url"] = data.get("reportInfoUrl", _config["report_info_url"])
        if data.get("appKey"):
            _config["app_key"] = data["appKey"]
        _config["cache"] = {**_config["cache"], **data.get("cache", {})}
        _config["monitor"] = {**_config["monitor"], **data.get("monitor", {})}
        _config["notification"] = {**_config["notification"], **data.get("notification", {})}

    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            _merge(json.load(f))
    local_path = root / "config" / "local.json"
    if local_path.exists():
        with open(local_path, "r", encoding="utf-8") as f:
            _merge(json.load(f))
    # 环境变量优先（与 common/auth.md 一致）
    if os.environ.get("XG_BIZ_API_KEY"):
        _config["app_key"] = os.environ["XG_BIZ_API_KEY"]
    return _config


def get_config():
    return load_config()
