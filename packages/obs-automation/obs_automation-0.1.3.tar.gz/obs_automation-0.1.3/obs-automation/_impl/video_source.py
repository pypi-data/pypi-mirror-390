from .client_manager import _ClientManager
class _VideoSource:
    @staticmethod
    def set_media(file_path_or_url: str):
        client = _ClientManager.get_instance().get_client()
        client.set_input_settings(
            "Media Source",
            {
                "local_file": file_path_or_url,
                "is_local_file": file_path_or_url.startswith('/')
            },
            overlay=False
        )

    @staticmethod
    def set_browser(url: str):
        client = _ClientManager.get_instance().get_client()
        client.set_input_settings("Browser", { "url": url }, overlay=False)
