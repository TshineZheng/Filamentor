from typing import Union
from fastapi import APIRouter, Depends

from src.controller import ChannelAction
from src.web.controller import service
from src.web.controller.dependencies import valid_channel_binded, valid_channel_unbinded, valid_controller_channel, valid_controller_id_exist, valid_controller_type, valid_channel_action
from src.web.controller.schemas import ControllerChannelModel, YBAAMSControllerInfoModel
from src.web.printer.dependencies import valid_ams_printer_task, valid_printer_id_exist


router = APIRouter()


@router.put('/', dependencies=[Depends(valid_ams_printer_task)])
async def add_controller(
    alias: str,
    info: Union[YBAAMSControllerInfoModel],
    type: str = Depends(valid_controller_type)
):
    await service.add_controller(type, alias, info)


@router.delete('/', dependencies=[Depends(valid_ams_printer_task)])
async def delete_controller(
        id: str = Depends(valid_controller_id_exist),
):
    await service.remove_controller(id)


@router.post('/bind_printer', dependencies=[Depends(valid_ams_printer_task)])
async def bind_printer(
        printer_id: str = Depends(valid_printer_id_exist),
        channel: ControllerChannelModel = Depends(valid_channel_binded),
):
    await service.bind_printer(controller_id=channel.controller_id, printer_id=printer_id, channel=channel.channel)


@router.post('/unbind_printer', dependencies=[Depends(valid_ams_printer_task)])
async def unbind_printer(
        printer_id: str = Depends(valid_printer_id_exist),
        channel: ControllerChannelModel = Depends(valid_channel_unbinded),
):
    await service.unbind_printer(controller_id=channel.controller_id, printer_id=printer_id, channel=channel.channel)


@router.post('/control', dependencies=[Depends(valid_ams_printer_task)])
async def controll(
    channel: ControllerChannelModel = Depends(valid_controller_channel),
    action: ChannelAction = Depends(valid_channel_action),
):
    await service.controll(channel.controller_id, channel.channel, action)
