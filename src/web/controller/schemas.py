from src.web.models import BaseModel


class ControllerChannelModel(BaseModel):
    controller_id: str
    channel: int


class YBAAMSControllerModel(BaseModel):
    ip: str
    port: int
    channel_total: int


class YBASingleBufferControllerModel(BaseModel):
    fila_broken_safe_time: int
    ip: str
    port: int
    channel_total: int
