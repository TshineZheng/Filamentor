

if __name__ == '__main__':
    from loguru import logger
    import sys

    from ams_core import AMSCore, ams_list
    import web.web_configuration as web
    import consts
    from app_config import config

    logger.remove(0)
    logger.add(sys.stderr, level="INFO")

    consts.setup()

    # 启动所有控制器
    for c in config.controller_list:
        c.controller.start()

    # 启动所有断料检测
    for d in config.detect_list:
        d.detect.start()

    # 启动所有打印机 和 对应AMS 连接
    for p in config.printer_list:
        p.client.start()
        ams = AMSCore(p.id)
        ams.start()
        ams_list.append(ams)

    try:
        web.run()
    except KeyboardInterrupt:
        web.stop()
        for a in ams_list:
            a.stop()
        for p in config.printer_list:
            p.client.stop()
        for c in config.controller_list:
            c.controller.stop()
        for d in config.detect_list:
            d.detect.stop()
        