import json
import os
from typing import List, Tuple

from src import consts
from src.broken_detect import BrokenDetect
from src.controller import Controller
from src.impl.bambu_client import BambuClient
from src.impl.mqtt_broken_detect import MQTTBrokenDetect
from src.impl.yba_ams_controller import YBAAMSController
from src.impl.yba_ams_py_controller import YBAAMSPYController
from src.impl.yba_ams_servo_controller import YBAAMSServoController
from src.mqtt_config import MQTTConfig
from src.printer_client import PrinterClient
from src.utils.log import LOGE, LOGI


class ChannelRelation:
    def __init__(self, printer_id: str, controller_id: str, channel: int, filament_type: str = 'GENERAL',
                 filament_color: str = '#FFFFFF') -> None:
        """打印机和通道的绑定关系

        Args:
            printer_id (str): 打印机ID
            controller_id (str): 通道板子ID
            channel (int): 通道在板子上的编号
        """
        self.printer_id = printer_id
        self.controller_id = controller_id
        self.channel = channel
        self.filament_type = filament_type
        self.filament_color = filament_color

    def to_dict(self):
        return {
            "printer_id": self.printer_id,
            "controller_id": self.controller_id,
            "channel": self.channel,
            "filament_type": self.filament_type,
            "filament_color": self.filament_color
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data["printer_id"],
            data["controller_id"],
            data["channel"],
            data["filament_type"],
            data["filament_color"]
        )


class DetectRelation:
    """打印机和断料检测器的绑定关系

    Aegs:
        printer_id (str): 打印机ID
        detect_id (str): 检测器ID
    """

    def __init__(self, printer_id: str, detect_id: str) -> None:
        self.printer_id = printer_id
        self.detect_id = detect_id

    def to_dict(self):
        return {
            "printer_id": self.printer_id,
            "detect_id": self.detect_id
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data["printer_id"],
            data["detect_id"]
        )


class IDPrinterClient:
    def __init__(self, id: str, client: PrinterClient, change_temp: int = 255, alias: str = None) -> None:
        self.id = id
        self.client = client
        self.change_temp = change_temp
        self.alias = alias

    def to_dict(self):
        return {
            "id": self.id,
            'type': self.client.type_name(),
            "alias": self.alias,
            "info": self.client.to_dict(),
            "change_temp": self.change_temp
        }

    @classmethod
    def from_dict(cls, data: dict):
        id = data["id"]
        type = data["type"]
        change_temp = data["change_temp"]
        alias = data["alias"]
        client = None
        if type == BambuClient.type_name():
            client = BambuClient.from_dict(data["info"])
        return cls(id, client, change_temp, alias)


class IDController:
    def __init__(self, id: str, controller: Controller, alias: str = None) -> None:
        self.id = id
        self.controller = controller
        self.alias = alias

    def to_dict(self):
        return {
            "id": self.id,
            'type': self.controller.type_name(),
            "alias": self.alias,
            "info": self.controller.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict):
        id = data["id"]
        type = data["type"]
        alias = data["alias"]
        controller = None
        if type == YBAAMSController.type_name():
            controller = YBAAMSController.from_dict(data["info"])
        elif type == YBAAMSPYController.type_name():
            controller = YBAAMSPYController.from_dict(data["info"])
        elif type == YBAAMSServoController.type_name():
            controller = YBAAMSServoController.from_dict(data["info"])
        return cls(id, controller, alias)


class IDBrokenDetect:
    def __init__(self, id: str, detect: BrokenDetect, alias: str = None) -> None:
        self.id = id
        self.detect = detect
        self.alias = alias

    def to_dict(self):
        return {
            "id": self.id,
            'type': self.detect.type_name(),
            "alias": self.alias,
            "info": self.detect.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict):
        id = data["id"]
        type = data["type"]
        alias = data["alias"]
        detect = None
        if type == MQTTBrokenDetect.type_name():
            detect = MQTTBrokenDetect.from_dict(data["info"])
        return cls(id, detect, alias)


class AMSSettings:
    def __init__(self, cur_filament: int, change_temp: int) -> None:
        pass


class AppConfig():
    def __init__(self) -> None:
        self.printer_list: List[IDPrinterClient] = []
        self.controller_list: List[IDController] = []
        self.detect_list: List[IDBrokenDetect] = []
        self.channel_relations: List[ChannelRelation] = []
        self.detect_relations: List[DetectRelation] = []
        self.mqtt_config: MQTTConfig = MQTTConfig()
        self.load_from_file()

    def load_from_dict(self, data: dict):
        if "printer_list" in data:
            self.printer_list = [IDPrinterClient.from_dict(i) for i in data["printer_list"]]
        if "controller_list" in data:
            self.controller_list = [IDController.from_dict(i) for i in data["controller_list"]]
        if "detect_list" in data:
            self.detect_list = [IDBrokenDetect.from_dict(i) for i in data["detect_list"]]
        if "channel_relations" in data:
            self.channel_relations = [ChannelRelation.from_dict(i) for i in data["channel_relations"]]
        if "detect_relations" in data:
            self.detect_relations = [DetectRelation.from_dict(i) for i in data["detect_relations"]]
        if "mqtt_config" in data:
            self.mqtt_config = MQTTConfig.from_dict(data["mqtt_config"])

    def load_from_file(self):
        if not os.path.exists(f'{consts.STORAGE_PATH}filamentor_config.json'):
            LOGI("没有找到配置文件，忽略")
            return
        try:
            with open(f'{consts.STORAGE_PATH}filamentor_config.json', 'r') as f:
                data = json.load(f)
                self.load_from_dict(data)
        except:
            LOGE("读取配置文件失败")
            pass

    def to_dict(self):
        return {
            "printer_list": [i.to_dict() for i in self.printer_list],
            "controller_list": [i.to_dict() for i in self.controller_list],
            "detect_list": [i.to_dict() for i in self.detect_list],
            "channel_relations": [i.to_dict() for i in self.channel_relations],
            "detect_relations": [i.to_dict() for i in self.detect_relations],
            "mqtt_config": self.mqtt_config.to_dict()
        }

    def save(self):
        with open(f'{consts.STORAGE_PATH}filamentor_config.json', 'w') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)

    def add_printer(self, id: str, client: PrinterClient, alias: str, change_temp: int):
        self.printer_list.append(IDPrinterClient(id, client, change_temp=change_temp, alias=alias))

    def remove_printer(self, id: str):
        for p in self.printer_list[:]:
            if p.id == id:
                self.printer_list.remove(p)
                # 删除所有控制器和检测的引用
                for c in self.channel_relations[:]:
                    if c.printer_id == id:
                        self.channel_relations.remove(c)
                for d in self.detect_relations[:]:
                    if d.printer_id == id:
                        self.detect_relations.remove(d)
                return

    def add_controller(self, id: str, controller: Controller, alias: str) -> Tuple[bool, str]:
        # 确保控制器不重复
        for p in self.controller_list:
            if p.controller.type_name() == controller.type_name():
                # YBA-AMS like controller exists
                if controller.type_name() == YBAAMSController.type_name() or controller.type_name() == YBAAMSPYController.type_name() or controller.type_name() == YBAAMSServoController.type_name():
                    if isinstance(controller, (YBAAMSController, YBAAMSPYController, YBAAMSServoController)):
                        if p.controller.ip == controller.ip:
                            return False, '控制器已存在'

        self.controller_list.append(IDController(id, controller, alias))
        return True, '控制器创建成功'

    def remove_controller(self, id: str):
        for p in self.controller_list[:]:
            if p.id == id:
                self.controller_list.remove(p)
                # 删除所有该控制器的通道引用
                for c in self.channel_relations[:]:
                    if c.controller_id == id:
                        self.channel_relations.remove(c)

    def add_detect(self, id: str, detect: BrokenDetect, alias: str) -> bool:
        # 确保id不重复
        for p in self.detect_list:
            if p.id == id:
                return False

        self.detect_list.append(IDBrokenDetect(id, detect, alias))
        return True

    def remove_detect(self, id: str):
        for p in self.detect_list[:]:
            if p.id == id:
                self.detect_list.remove(p)
                # 删除所有检测器的引用
                for c in self.detect_relations[:]:
                    if c.detect_id == id:
                        self.detect_relations.remove(c)

    def add_channel_setting(self, printer_id: str, controller_id: str, channel: int) -> bool:
        if not self.is_printer_exist(printer_id):
            return False

        if not self.is_channel_exist(controller_id, channel):
            return False

        if self.is_channel_relation_exist(controller_id, channel):
            return False

        self.channel_relations.append(ChannelRelation(printer_id, controller_id, channel))
        return True

    def remove_channel_setting(self, printer_id: str, controller_id: str, channel_id: int):
        for p in self.channel_relations[:]:
            if controller_id == p.controller_id and channel_id == p.channel and printer_id == p.printer_id:
                self.channel_relations.remove(p)

    def add_detect_setting(self, printer_id: str, detect_id: str) -> bool:
        if not self.is_detect_exist(detect_id):
            return False

        # 确保控制器的通道只被添加一次
        if self.is_detect_relation_exist(detect_id):
            return False

        self.detect_relations.append(DetectRelation(printer_id, detect_id))
        return True

    def remove_detect_setting(self, printer_id: str, detect_id: str):
        for p in self.detect_relations[:]:
            if printer_id == p.printer_id and detect_id == p.detect_id:
                self.detect_relations.remove(p)

    def is_printer_exist(self, id: str) -> bool:
        for p in self.printer_list:
            if p.id == id:
                return True
        return False

    def is_channel_exist(self, controller_id: str, channel_id: int) -> bool:
        for p in self.controller_list:
            if p.id == controller_id:
                if channel_id < p.controller.channel_total and channel_id >= 0:
                    return True
        return False

    def is_detect_exist(self, id: str) -> bool:
        for p in self.detect_list:
            if p.id == id:
                return True
        return False

    def is_channel_relation_exist(self, controller_id: str, channel_index: int) -> bool:
        for p in self.channel_relations:
            if p.controller_id == controller_id and p.channel == channel_index:
                return True
        return False

    def is_detect_relation_exist(self, detect_id: str) -> bool:
        for p in self.detect_relations:
            if p.detect_id == detect_id:
                return True
        return False

    def get_printer_channel_settings(self, printer_id: str) -> List[ChannelRelation]:
        return [p for p in self.channel_relations if p.printer_id == printer_id]

    def get_printer(self, printer_id: str) -> PrinterClient:
        for p in self.printer_list:
            if p.id == printer_id:
                return p.client
        return None

    def get_printer_change_tem(self, printer_id: str) -> int:
        for p in self.printer_list:
            if p.id == printer_id:
                return p.change_temp
        return 255

    def set_printer_change_tem(self, printer_id: str, tem: int):
        for p in self.printer_list:
            if p.id == printer_id:
                p.change_temp = tem
                self.save()
                return

    def get_printer_broken_detect(self, printer_id: str) -> List[BrokenDetect]:
        t = [p for p in self.detect_relations if p.printer_id == printer_id]
        return [p.detect for p in self.detect_list if p.id in [d.detect_id for d in t]]

    def get_controller(self, controller_id: str) -> Controller:
        for p in self.controller_list:
            if p.id == controller_id:
                return p.controller
        return None


config = AppConfig()
