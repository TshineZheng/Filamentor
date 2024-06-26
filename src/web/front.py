
import http.server
from typing import Any

from src.utils.net_util import get_ip_address

front_server: http.server.HTTPServer = None


class FrontHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, directory='web')

    def log_message(self, format: str, *args: Any) -> None:
        pass


def start():
    import os
    import threading
    if os.path.exists('web'):
        global front_server
        front_server = http.server.HTTPServer(('', 8001), FrontHandler)
        threading.Thread(target=front_server.serve_forever).start()

        myip = get_ip_address()
        print("========================================")
        print(f"| 管理页面: http://{myip}:8001      |")
        print(f"| 接口文档: http://{myip}:7170/docs |")
        print("========================================")


def stop():
    if front_server:
        front_server.shutdown()
