from fastapi import APIRouter, Depends
from src.printer_client import PrinterClient
from src.web.printer.dependencies import valid_ams_printer_task, valid_printer_channel, valid_printer_id_exist, valid_printer_taken
import src.web.printer.service as service

router = APIRouter()


@router.put('/', dependencies=[Depends(valid_ams_printer_task)])
async def create_printer(alias: str, change_temp: int, printer: PrinterClient = Depends(valid_printer_taken)):
    id = await service.create_printer(printer, alias=alias, change_temp=change_temp),
    return {'id': id}


@router.delete('/', dependencies=[Depends(valid_ams_printer_task)])
async def delete_printer(
    printer_id: str = Depends(valid_printer_id_exist),
):
    await service.delete_printer(printer_id)
    return {'id': printer_id}


@router.post('/set_channel', dependencies=[Depends(valid_ams_printer_task)])
async def set_channel(
        printer_id: str = Depends(valid_printer_id_exist),
        printer_channel: int = Depends(valid_printer_channel)):
    await service.update_printer_channel(printer_id, printer_channel)


@ router.post('/set_change_temp')
async def set_change_temp(
    change_temp: int,
    printer_id: str = Depends(valid_printer_id_exist),
):
    await service.update_printer_change_temp(printer_id, change_temp)


@router.post('/edit_channel_filament_setting')
async def edit_channel_filament_setting(
    filament_type: str,
    filament_color: str,
    printer_id: str = Depends(valid_printer_id_exist),
    printer_channel: int = Depends(valid_printer_channel),
):
    await service.edit_channel_filament_setting(printer_id, printer_channel, filament_type, filament_color)
