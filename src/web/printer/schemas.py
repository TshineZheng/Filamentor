from pydantic import BaseModel


class BambuPrinterInfo(BaseModel):
    printer_ip: str
    lan_password: str
    device_serial: str