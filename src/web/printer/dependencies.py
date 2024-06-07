
from typing import Union
from fastapi import Depends
from src.impl.bambu_client import BambuClient
from src.printer_client import PrinterClient
from src.web.exceptions import DetailedHTTPException
from src.web.printer.exceptions import ChannelNotFoundError, PrinterHasTaskError, PrinterInfoError, PrinterNotFoundError, PrinterTaken, PrinterTypeNotMatch
from src.app_config import config
import src.core_services as core_services
from src.web.printer.schemas import BambuPrinterInfo


async def valid_printer_type(type:str) -> str:
    if type == BambuClient.type_name():
        return BambuClient.type_name()
    else:
        raise PrinterTypeNotMatch()


async def valid_printer_taken(info: Union[BambuPrinterInfo], type: str = Depends(valid_printer_type)) -> PrinterClient:
    printer_client: PrinterClient = None

    if type == BambuClient.type_name():
        try:
            printer_client = BambuClient(info)
        except:
            raise PrinterInfoError()
        
    if printer_client is None:
        raise DetailedHTTPException(status_code=500, detail="未知错误")
    
    for p in config.printer_list:
        if p.client == printer_client:
            raise PrinterTaken()
        
    return printer_client

async def valid_printer_id_exist(printer_id:str):
    for p in config.printer_list:
        if p.id == printer_id:
            return printer_id

    raise PrinterNotFoundError()


async def valid_printer_channel(printer_id : str, channel_index: int) -> int:

    channels = config.get_printer_channel_settings(printer_id)

    if 0 <= channel_index < len(channels):
        return channel_index

    raise ChannelNotFoundError()


async def valid_ams_printer_task():
    #TODO: 最好能分开打印机判断
    if core_services.hasPrintTaskRunning():
        raise PrinterHasTaskError()
