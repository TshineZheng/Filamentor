def stop():
    import src.ams_core as ams_core
    import src.app_config as app_config
    from src.utils.log import LOGI
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
    import src.ams_core as ams_core
    import src.app_config as app_config
    from src.utils.log import LOGI
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

def hasPrintTaskRunning():
    from src.ams_core import ams_list
    #TODO: 这里没有分开判断，需要优化
    for a in ams_list:
        if a.hasTask():
            return True
    return False