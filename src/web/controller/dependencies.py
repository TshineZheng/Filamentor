from typing import List
from fastapi import Depends, Query
from src.controller import ChannelAction
from src.impl.yba_ams_controller import YBAAMSController
from src.impl.yba_ams_py_controller import YBAAMSPYController
from src.impl.yba_ams_servo_controller import YBAAMSServoController
from src.impl.yba_single_buffer_controller import YBASingleBufferController
from src.web.controller.exceptions import ChannelDuplicate, ControllerChannelBinded, ControllerChannelActionError, ControllerChannelNotFoundError, ControllerChannelUnBinded, ControllerNotFoundError, ControllerTypeNotMatch

from src.app_config import config
from src.web.controller.schemas import ControllerChannelModel


async def valid_controller_type(controller_type: str) -> str:
    if controller_type == YBAAMSPYController.type_name():
        return controller_type
    elif controller_type == YBAAMSServoController.type_name():
        return controller_type
    elif controller_type == YBAAMSController.type_name():
        return controller_type
    elif controller_type == YBASingleBufferController.type_name():
        return controller_type
    else:
        raise ControllerTypeNotMatch()


async def valid_controller_id_exist(controller_id: str) -> str:
    for c in config.controller_list:
        if c.id == controller_id:
            return controller_id
    raise ControllerNotFoundError()


async def valid_controller_channel(channel: int, controller_id: str = Depends(valid_controller_id_exist)) -> ControllerChannelModel:
    for c in config.controller_list:
        if c.id == controller_id:
            if 0 <= channel < c.controller.channel_total:
                return ControllerChannelModel(controller_id=controller_id, channel=channel)
    raise ControllerChannelNotFoundError()


async def valid_channel_binded(channels: List[int] = Query(alias='channels'), controller_id: str = Depends(valid_controller_id_exist)) -> List[ControllerChannelModel]:
    if len(channels) != len(set(channels)):
        raise ChannelDuplicate()

    for channel in channels:
        await valid_controller_channel(channel, controller_id)

    for c in config.channel_relations:
        for channel in channels:
            if c.controller_id == controller_id and c.channel == channel:
                raise ControllerChannelBinded()

    return [ControllerChannelModel(controller_id=controller_id, channel=channel) for channel in channels]


async def valid_channel_unbinded(channel: int, controller_id: str = Depends(valid_controller_id_exist)) -> ControllerChannelModel:
    for c in config.channel_relations:
        if c.controller_id == controller_id and c.channel == channel:
            return ControllerChannelModel(controller_id=controller_id, channel=channel)
    raise ControllerChannelUnBinded()


async def valid_channel_action(action: int) -> ChannelAction:
    if action == ChannelAction.PUSH.value or action == ChannelAction.PULL.value or action == ChannelAction.STOP.value:
        return ChannelAction(action)

    raise ControllerChannelActionError()
