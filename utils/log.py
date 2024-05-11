from abc import abstractmethod
from typing import Any
from loguru import logger as LOG
import consts

def LOGI(msg, *args: Any, **kwargs: Any):
    LOG.info(msg, *args, **kwargs)

def LOGW(msg, *args: Any, **kwargs: Any):
    LOG.info(msg, *args, **kwargs)

def LOGE(msg, *args: Any, **kwargs: Any):
    LOG.error(msg, *args, **kwargs)

def LOGD(msg, *args: Any, **kwargs: Any):
    LOG.debug(msg, *args, **kwargs)

LOG.add(
    sink = f'{consts.STORAGE_PATH}/logs/filamentor.log',
    enqueue=True,
    rotation='1 days',
    retention='1 weeks',
    encoding='utf-8',
    backtrace=True,
    diagnose=True,
    compression='zip'
)

class TAGLOG:
    @abstractmethod
    def tag(self):
        return ''
    
    def LOGI(self, msg, *args: Any, **kwargs: Any):
        LOGI(self.__mix_msg__(msg), *args, **kwargs)

    def LOGW(self, msg, *args: Any, **kwargs: Any):
        LOGW(self.__mix_msg__(msg), *args, **kwargs)

    def LOGE(self, msg, *args: Any, **kwargs: Any):
        LOGE(self.__mix_msg__(msg), *args, **kwargs)

    def LOGD(self, msg, *args: Any, **kwargs: Any):
        LOGD(self.__mix_msg__(msg), *args, **kwargs)

    def __mix_msg__(self, msg:str):
        if self.tag == '' or self.tag is None:
            return msg
        return f'{self.tag()} | {msg}'