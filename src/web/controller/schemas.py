from pydantic import BaseModel

class ControllerChannelModel(BaseModel):
    controller_id:str
    channel:int

class YBAAMSControllerInfoModel(BaseModel):
    ip: str
    port: int
    channel_total: int