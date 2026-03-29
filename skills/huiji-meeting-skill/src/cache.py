# 内存 TTL 缓存，用于会议列表等接口结果，减少重复请求
import time
from collections import OrderedDict
from typing import Any, Optional


class CacheManager:
    """简单内存缓存：支持 TTL（毫秒）与最大条数，超出时淘汰最久未访问的项。"""

    def __init__(self, ttl_ms: int = 60000, max_size: int = 100):
        self._ttl_ms = ttl_ms
        self._max_size = max(max_size, 1)
        self._data: OrderedDict[str, tuple[float, Any]] = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        if key not in self._data:
            return None
        expire_at, value = self._data[key]
        if time.time() * 1000 > expire_at:
            del self._data[key]
            return None
        self._data.move_to_end(key)
        return value

    def set(self, key: str, value: Any) -> None:
        now_ms = time.time() * 1000
        expire_at = now_ms + self._ttl_ms
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = (expire_at, value)
        while len(self._data) > self._max_size:
            self._data.popitem(last=False)
