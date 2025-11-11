import obsws_python as obs
import threading

class _ClientManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self._client = None
        self._config = {
            "host": "localhost",
            "port": 4455,
            "password": "LocoTeam",
            "timeout": 3
        }

    @classmethod
    def get_instance(cls):
        """Thread-safe singleton access"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def configure(self, host: str = None, port: int = None, password: str = None, timeout: int = None):
        """Update connection parameters (before creating client)"""
        if self._client is not None:
            raise RuntimeError("Cannot reconfigure OBS connection after client is created.")

        if host: self._config["host"] = host
        if port: self._config["port"] = port
        if password: self._config["password"] = password
        if timeout: self._config["timeout"] = timeout

    def get_client(self):
        """Create or return existing OBS client"""
        if self._client is None:
            self._client = obs.ReqClient(**self._config)
        return self._client
