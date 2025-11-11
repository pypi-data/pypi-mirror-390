from .client_manager import _ClientManager

class _Streamer:
    @staticmethod
    def init(server: str, stream_key: str):
        client = _ClientManager.get_instance().get_client()
        client.set_stream_service_settings(
            'rtmp_custom',
            {
                "server": server,
                "key": stream_key,
                "use_auth": False
            }
        )

    @staticmethod
    def start():
        client = _ClientManager.get_instance().get_client()
        client.start_stream()

    @staticmethod
    def stop():
        client = _ClientManager.get_instance().get_client()
        client.stop_stream()
