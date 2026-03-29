#!/usr/bin/env python3
"""探测 chatListByPage 在什么情况下返回 resultCode=200。打印原始 resultCode 与 data 结构。"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from src.config_loader import get_config

def main():
    cfg = get_config()
    url = cfg["api_base_url"]
    app_key = os.environ.get("XG_BIZ_API_KEY") or cfg.get("app_key") or ""
    if not app_key:
        print("请设置 XG_BIZ_API_KEY")
        return 1
    # 与 client.get_meetings 相同的参数
    params_list = [
        {"pageNum": 0, "pageSize": 5, "sortKey": "createTime", "nameBlur": None, "limit": ""},
        {"pageNum": 0, "pageSize": 5, "sortKey": "createTime", "nameBlur": "", "limit": ""},
    ]
    for i, params in enumerate(params_list):
        body = {k: v for k, v in params.items() if v is not None}
        print(f"--- 请求 {i+1}: {json.dumps(body, ensure_ascii=False)} ---")
        resp = requests.post(
            url,
            headers={"appKey": app_key, "Content-Type": "application/json; charset=utf-8"},
            json=body,
            timeout=30,
        )
        print(f"HTTP {resp.status_code}")
        data = resp.json()
        rc = data.get("resultCode")
        print(f"resultCode: {rc} (type: {type(rc).__name__})")
        if "data" in data and data["data"]:
            d = data["data"]
            print(f"data 键: {list(d.keys())}")
            if "pageContent" in d:
                print(f"  pageContent 条数: {len(d['pageContent']) if isinstance(d['pageContent'], list) else 'N/A'}")
            if "records" in d:
                print(f"  records 条数: {len(d['records']) if isinstance(d['records'], list) else 'N/A'}")
        else:
            print(f"data: {data.get('data')}")
            print(f"resultMsg: {data.get('resultMsg')}")
        print()
    return 0

if __name__ == "__main__":
    sys.exit(main())
