from loguru import logger as LOG

def LOGI(msg):
    LOG.info(msg)

def LOGW(msg):
    LOG.info(msg)

def LOGE(msg):
    LOG.error(msg)

LOG.add(
    sink = './logs/filamentor.log',
    enqueue=True,
    rotation='1 days',
    retention='1 weeks',
    encoding='utf-8',
    backtrace=True,
    diagnose=True,
    compression='zip'
)