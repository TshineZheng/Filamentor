from typing import Any
from loguru import logger as LOG


def LOGI(msg, *args: Any, **kwargs: Any):
    LOG.info(msg, *args, **kwargs)

def LOGW(msg, *args: Any, **kwargs: Any):
    LOG.info(msg, *args, **kwargs)

def LOGE(msg, *args: Any, **kwargs: Any):
    LOG.error(msg, *args, **kwargs)

def LOGD(msg, *args: Any, **kwargs: Any):
    LOG.debug(msg, *args, **kwargs)

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