from .config import Singleton


class RedisManager:
    def __init__(self) -> None:
        self.redis = Singleton.get_connection()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.redis.close()

    def save_in_redis(self, keys: list, value: str, lifetime: int = -1) -> None:
        self.redis.set(keys, value, lifetime)

    def get_data(self, key: str):
        result = self.redis.get(key)
        return result
