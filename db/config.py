from redis.client import Redis


HOST: str
PORT: int
DB: int


class Singleton:
    _instance = None

    @staticmethod
    def get_connection() -> Redis:
        if not Singleton._instance:
            Singleton._instance = Redis(host="0.0.0.0", port=6379, db=0)
        return Singleton._instance
