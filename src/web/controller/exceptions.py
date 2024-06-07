from src.web.exceptions import BadRequest


class ControllerTypeNotMatch(BadRequest):
    DETAIL = "控制器类型不支持"

class ControllerNotFoundError(BadRequest):
    DETAIL = "控制器不存在"

class ControllerChannelNotFoundError(BadRequest):
    DETAIL = "控制器通道不存在"

class ControllerChannelBinded(BadRequest):
    DETAIL = "控制器通道已绑定"

class ControllerChannelUnBinded(BadRequest):
    DETAIL = "控制器通道未绑定"

class ControllerTaken(BadRequest):
    DETAIL = "控制器已存在"

class ControllerInfoError(BadRequest):
    DETAIL = "控制器信息有误"

class ControllerChannelActionError(BadRequest):
    DETAIL = "控制器通道动作有误"

class ChannelDuplicate(BadRequest):
    DETAIL = "请求设置的通道有重复"