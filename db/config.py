from redis.client import Redis

class Singleton:
    _instance = None
    @staticmethod
    def get_connection():
        if not Singleton._instance:
            Singleton._instance = Redis(host='0.0.0.0', port=6379)
        return Singleton._instance