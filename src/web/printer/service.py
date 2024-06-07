import uuid
from src.printer_client import PrinterClient
from src.utils import persist
from src.app_config import config
import src.core_services as core_services
from src.ams_core import ams_list


async def create_printer(printerClient: PrinterClient, alias: str, change_temp: int) -> str:
    id = f'{printerClient.type_name()}_{uuid.uuid1()}'

    #TODO：需要验证打印是否可用

    config.add_printer(id, printerClient, alias, change_temp)
    config.save()
    core_services.restart()

    return id


async def delete_printer(printer_id: str) -> str:
    config.remove_printer(printer_id)
    config.save()
    core_services.restart()
    return printer_id


async def update_printer_channel(printer_id: str, channel_index: int):
    persist.update_printer_channel(printer_id, channel_index)
    core_services.restart()


async def update_printer_change_temp(printer_id: str, change_temp: int):
    config.set_printer_change_tem(printer_id, change_temp)
    config.save()
    
    for p in ams_list:
        if p.use_printer == printer_id:
            p.change_tem = change_temp


async def edit_channel_filament_setting(printer_id:str, channel:int, filament_type:str, filament_color:str):
    channels = config.get_printer_channel_settings(printer_id)
    channels[channel].filament_type = filament_type
    channels[channel].filament_color = filament_color
    config.save()
