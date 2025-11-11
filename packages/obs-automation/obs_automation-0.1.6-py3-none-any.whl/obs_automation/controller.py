from ._impl.client_manager import _ClientManager
from ._impl.streamer import _Streamer
from ._impl.video_source import _VideoSource

class ObsController:
    """Public interface for OBS automation"""

    @staticmethod
    def configure_connection(host: str = "localhost", port: int = 4455, password: str = "LocoTeam", timeout: int = 3):
        """
        Configure OBS WebSocket connection before initialization.
        Example:
            ObsController.configure_connection(host="192.168.1.10", password="secret")
        """
        manager = _ClientManager.get_instance()
        manager.configure(host=host, port=port, password=password, timeout=timeout)

    @staticmethod
    def init(server: str, stream_key: str):
        """Initialize OBS stream configuration"""
        _Streamer.init(server, stream_key)

    @staticmethod
    def set_video_source_media(file_path_or_url: str):
        """Set video source as local file or URL"""
        _VideoSource.set_media(file_path_or_url)

    @staticmethod
    def set_video_source_browser(url: str):
        """Set video source as browser source"""
        _VideoSource.set_browser(url)

    @staticmethod
    def start():
        """Start the stream"""
        _Streamer.start()

    @staticmethod
    def stop():
        """Stop the stream"""
        _Streamer.stop()
