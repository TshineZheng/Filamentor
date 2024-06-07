from src.web.exceptions import BadRequest, NotFound


class PrinterNotFoundError(BadRequest):
    DETAIL = "没有对应的打印机"


class ChannelNotFoundError(BadRequest):
    DETAIL = '没有对应的通道'


class PrinterTaken(BadRequest):
    DETAIL = '打印机已存在'


class PrinterTypeNotMatch(BadRequest):
    DETAIL = '打印机类型不支持'


class PrinterHasTaskError(BadRequest):
    DETAIL = '打印机打印中，无法调用该接口，请在没有打印任务时再操作'

class PrinterInfoError(BadRequest):
    DETAIL = '打印机信息有误'
