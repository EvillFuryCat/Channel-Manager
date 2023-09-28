from redis.client import Redis


HOST: str
PORT: int
DB: int


class Singleton:
    _instances = {}

    @staticmethod
    def get_connection(host: str, port: int, db: int) -> Redis:
        connection_key = (host, port, db)
        if connection_key not in Singleton._instances:
            Singleton._instances[connection_key] = Redis(host=host, port=port, db=db)
        return Singleton._instances[connection_key]