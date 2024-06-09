from src.web.models import BaseModel


class BambuPrinterModel(BaseModel):
    printer_ip: str
    lan_password: str
    device_serial: str