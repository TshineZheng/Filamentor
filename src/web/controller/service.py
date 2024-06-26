from typing import List, Union
import uuid
from src.controller import ChannelAction, Controller
from src.web.controller.exceptions import ControllerTaken
from src.app_config import config
import src.core_services as core_services
from src.web.controller.schemas import ControllerChannelModel, YBAAMSControllerModel


async def add_controller(type: str, alias: str, info: Union[YBAAMSControllerModel]) -> Controller:
    contorller = Controller.generate_controller(type, info.model_dump())

    for c in config.controller_list:
        if c.controller == contorller:
            raise ControllerTaken()

    # TODO: 需要验证控制器是否可用

    config.add_controller(f'{type}_{uuid.uuid1()}', contorller, alias)
    config.save()
    core_services.restart()


async def remove_controller(id: str):
    config.remove_controller(id)
    config.save()
    core_services.restart()


async def bind_printer(printer_id: str, channels: List[ControllerChannelModel]):
    for c in channels:
        config.add_channel_setting(printer_id, c.controller_id, c.channel)

    config.save()
    core_services.restart()


async def unbind_printer(controller_id: str, printer_id: str, channel: int):
    config.remove_channel_setting(printer_id, controller_id, channel)
    config.save()
    core_services.restart()


async def controll(controller_id: str, channel: int, action: int):
    config.get_controller(controller_id).control(
        channel, ChannelAction(action))
