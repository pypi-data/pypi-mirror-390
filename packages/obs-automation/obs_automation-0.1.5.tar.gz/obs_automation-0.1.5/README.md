# obs-automation

A simple Python library that provides a clean interface to automate OBS streaming using the `obsws-python` WebSocket client.

## Installation
```bash
pip install obs-automation

## Method Signature

    def configure_connection(host: str = "localhost", port: int = 4455, password: str = "YourPassword", timeout: int = 3):

    def init(server: str, stream_key: str):
        """Initialize OBS stream configuration"""

    def set_video_source_media(file_path_or_url: str):
        """Set video source as local file or URL"""

    def set_video_source_browser(url: str):
        """Set video source as browser source"""

    def start():


    def stop():
        



