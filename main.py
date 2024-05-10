from loguru import logger
import sys

from ams_core import AMSCore
from app_config import AppConfig

import web.web_configuration as web

CUR_CHANNEL = 2     # 当前通道

CHANGE_TEM = 255    # 换色温度

app_config = AppConfig.load()

if app_config == None:
    print('配置文件加载失败')
    exit(1)

if __name__ == '__main__':
    logger.remove(0)
    logger.add(sys.stderr, level="INFO")
    
    # 启动所有打印机连接
    for p in app_config.printer_list:
        p.client.start()

    # 启动所有控制器
    for c in app_config.controller_list:
        c.controller.start()

    # 启动所有断料检测
    for d in app_config.detect_list:
        d.detect.start()

    ams = AMSCore(app_config, 'bambu-1', CUR_CHANNEL, CHANGE_TEM)
    ams.start()

    try:
        web.run()
    except KeyboardInterrupt:
        web.stop()
        ams.stop()
        for p in app_config.printer_list:
            p.client.stop()
        for c in app_config.controller_list:
            c.controller.stop()
        for d in app_config.detect_list:
            d.detect.stop()
        