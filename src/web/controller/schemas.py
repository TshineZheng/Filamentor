from src.web.models import BaseModel

class ControllerChannelModel(BaseModel):
    controller_id:str
    channel:int

class YBAAMSControllerModel(BaseModel):
    ip: str
    port: int
    channel_total: int