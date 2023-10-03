from redis.client import Redis
import os


HOST: str = os.getenv("HOST")
PORT: int = os.getenv("PORT")
DB: int = os.getenv("DB")


class Singleton:
    _instances = {}

    @staticmethod
    def get_connection(host: str, port: int, db: int) -> Redis:
        connection_key = (host, port, db)
        if connection_key not in Singleton._instances:
            Singleton._instances[connection_key] = Redis(host=HOST, port=PORT, db=DB)
        return Singleton._instances[connection_key]
