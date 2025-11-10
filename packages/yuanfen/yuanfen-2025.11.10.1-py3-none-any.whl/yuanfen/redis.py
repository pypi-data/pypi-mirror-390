import time

import redis


class RedisLock:
    def __init__(self, redis_client, lock_key, timeout=10, retry_interval=None):
        self.redis_client = redis_client
        self.lock_key = lock_key
        self.timeout = timeout
        self.retry_interval = retry_interval
        self.locked = False

    def acquire(self):
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            if self.redis_client.set(self.lock_key, "1", ex=self.timeout, nx=True):
                self.locked = True
                return True
            elif not self.retry_interval:
                return False
            else:
                time.sleep(self.retry_interval)

        return False

    def release(self):
        if self.locked:
            self.redis_client.delete(self.lock_key)
            self.locked = False


class Redis:
    def __init__(self, config: dict):
        self.redis_client = redis.Redis(
            host=config.get("host", "localhost"),
            port=config.get("port", 6379),
            password=config.get("password", None),
            db=config.get("db", 0),
            decode_responses=config.get("decode_responses", True),
        )
        self.prefix = config.get("prefix", "")

    def prefixed(self, key: str):
        return f"{self.prefix}:{key}" if self.prefix else key

    def get(self, key: str) -> str | None:
        return self.redis_client.get(self.prefixed(key))  # type: ignore

    def getset(self, key: str, value: str) -> str | None:
        return self.redis_client.getset(self.prefixed(key), value)  # type: ignore

    def set(self, key: str, value: str, ex=None, px=None, nx=False) -> bool:
        return self.redis_client.set(self.prefixed(key), value, ex=ex, px=px, nx=nx)  # type: ignore

    def setnx(self, key: str, value: str) -> bool:
        return self.redis_client.setnx(self.prefixed(key), value)  # type: ignore

    def setex(self, key: str, time: int, value: str) -> bool:
        return self.redis_client.setex(self.prefixed(key), time, value)  # type: ignore

    def delete(self, key: str) -> int:
        return self.redis_client.delete(self.prefixed(key))  # type: ignore

    def expire(self, key: str, time: int) -> bool:
        return self.redis_client.expire(self.prefixed(key), time)  # type: ignore

    def exists(self, key: str) -> int:
        return self.redis_client.exists(self.prefixed(key))  # type: ignore

    def incr(self, key: str, amount=1) -> int:
        return self.redis_client.incr(self.prefixed(key), amount)  # type: ignore

    def ttl(self, key: str) -> int:
        return self.redis_client.ttl(self.prefixed(key))  # type: ignore
