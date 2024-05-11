from loguru import logger
import sys

from ams_core import AMSCore
from app_config import AppConfig

import web.web_configuration as web

app_config = AppConfig.load()

if __name__ == '__main__':
    logger.remove(0)
    logger.add(sys.stderr, level="INFO")

    # 启动所有控制器
    for c in app_config.controller_list:
        c.controller.start()

    # 启动所有断料检测
    for d in app_config.detect_list:
        d.detect.start()

    ams_list:list[AMSCore] = []

    # 启动所有打印机 和 对应AMS 连接
    for p in app_config.printer_list:
        p.client.start()
        ams = AMSCore(app_config, p.id)
        ams.start()
        ams_list.append(ams)

    try:
        web.run()
    except KeyboardInterrupt:
        web.stop()
        for a in ams_list:
            a.stop()
        for p in app_config.printer_list:
            p.client.stop()
        for c in app_config.controller_list:
            c.controller.stop()
        for d in app_config.detect_list:
            d.detect.stop()
        