def stop():
    import ams_core
    import app_config
    from utils.log import LOGI
    LOGI('关闭所有连接')
    # stop all
    for a in ams_core.ams_list:
        a.stop()
    for p in app_config.config.printer_list:
        p.client.stop()
    for c in app_config.config.controller_list:
        c.controller.stop()
    for d in app_config.config.detect_list:
        d.detect.stop()

def start():
    import ams_core
    import app_config
    from utils.log import LOGI
    LOGI('启动所有连接')
    # 启动所有控制器
    for c in app_config.config.controller_list:
        c.controller.start()
    # 启动所有断料检测
    for d in app_config.config.detect_list:
        d.detect.start()
    ams_core.ams_list.clear()
    # 启动所有打印机 和 对应AMS 连接
    for p in app_config.config.printer_list:
        p.client.start()
        ams = ams_core.AMSCore(p.id)
        ams.start()
        ams_core.ams_list.append(ams)

def restart():
    stop()
    start()

if __name__ == '__main__':
    from loguru import logger
    import sys
    import web.web_configuration as web
    import consts

    logger.remove(0)
    logger.add(sys.stderr, level="INFO")

    consts.setup()

    start()
    
    try:
        web.run()
    except KeyboardInterrupt:
        web.stop()
        stop()
        