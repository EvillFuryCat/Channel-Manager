from redis.client import Redis


class Singleton:
    _instance = None

    @staticmethod
    def get_connection():
        if not Singleton._instance:
            Singleton._instance = Redis(host="redis", port=6379, db=0)
        return Singleton._instance
