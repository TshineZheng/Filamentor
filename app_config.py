import json
from typing import List

from broken_detect import BrokenDetect
from impl.bambu_client import BambuClient, BambuClientConfig
from mqtt_config import MQTTConfig
from controller import Controller
from impl.mqtt_broken_detect import MQTTBrokenDetect
from impl.yba_ams_controller import YBAAMSController
from printer_client import PrinterClient


class ChannelRelation:
    def __init__(self, printer_id: str, controller_id: str, channel: int) -> None:
        """打印机和通道的绑定关系

        Args:
            printer_id (str): 打印机ID
            controller_id (str): 通道板子ID
            channel (int): 通道在板子上的编号
        """
        self.printer_id = printer_id
        self.controller_id = controller_id
        self.channel = channel

    def to_dict(self):
        return {
            "printer_id": self.printer_id,
            "controller_id": self.controller_id,
            "channel": self.channel
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data["printer_id"],
            data["controller_id"],
            data["channel"]
        )


class DetectRelation:
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
    def __init__(self, id: str, client: PrinterClient) -> None:
        self.id = id
        self.client = client

    def to_dict(self):
        return {
            "id": self.id,
            'type': self.client.type_name(),
            "info": self.client.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict):
        id = data["id"]
        type = data["type"]
        client = None
        if type == BambuClient.type_name():
            client = BambuClient.from_dict(data["info"])
        return cls(id, client)


class IDController:
    def __init__(self, id: str, controller: Controller) -> None:
        self.id = id
        self.controller = controller

    def to_dict(self):
        return {
            "id": self.id,
            'type': self.controller.type_name(),
            "info": self.controller.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict):
        id = data["id"]
        type = data["type"]
        controller = None
        if type == YBAAMSController.type_name():
            controller = YBAAMSController.from_dict(data["info"])
        return cls(id, controller)


class IDBrokenDetect:
    def __init__(self, id: str, detect: BrokenDetect) -> None:
        self.id = id
        self.detect = detect

    def to_dict(self):
        return {
            "id": self.id,
            'type': self.detect.type_name(),
            "info": self.detect.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict):
        id = data["id"]
        type = data["type"]
        detect = None
        if type == MQTTBrokenDetect.type_name():
            detect = MQTTBrokenDetect.from_dict(data["info"])
        return cls(id, detect)


class AppConfig:

    def __init__(self,
                 printers: List[IDPrinterClient],
                 controllers: List[IDController],
                 detects: List[IDBrokenDetect],
                 channel_set: List[ChannelRelation],
                 detect_set: List[DetectRelation],
                 mqtt_config: MQTTConfig
                 ) -> None:
        self.printer_list = printers
        self.controller_list = controllers
        self.detect_list = detects
        self.channel_settings = channel_set
        self.detect_settings = detect_set
        self.mqtt_config = mqtt_config

    @classmethod
    def from_dict(cls, data: dict):
        printers = [IDPrinterClient.from_dict(i) for i in data["printer_list"]]
        controllers = [IDController.from_dict(i) for i in data["controller_list"]]
        detects = [IDBrokenDetect.from_dict(i) for i in data["detect_list"]]
        channel_set = [ChannelRelation.from_dict(i) for i in data["channel_settings"]]
        detect_set = [DetectRelation.from_dict(i) for i in data["detect_settings"]]
        mqtt_config = MQTTConfig.from_dict(data["mqtt_config"])
        return cls(printers, controllers, detects, channel_set, detect_set, mqtt_config)

    def to_dict(self):
        return {
            "printer_list": [i.to_dict() for i in self.printer_list],
            "controller_list": [i.to_dict() for i in self.controller_list],
            "detect_list": [i.to_dict() for i in self.detect_list],
            "channel_settings": [i.to_dict() for i in self.channel_settings],
            "detect_settings": [i.to_dict() for i in self.detect_settings],
            "mqtt_config": self.mqtt_config.to_dict()
        }
    
    def add_printer(self, id: str, client: PrinterClient) -> bool:
        # 确保id不重复
        for p in self.printer_list:
            if p.id == id:
                return False
            
        self.printer_list.append(IDPrinterClient(id, client))
        return True
    
    def remove_printer(self, id: str):
        for p in self.printer_list[:]:
            if p.id == id:
                self.printer_list.remove(p)
                # 删除所有控制器和检测的引用
                for c in self.channel_settings[:]:
                    if c.printer_id == id:
                        self.channel_settings.remove(c)
                for d in self.detect_settings[:]:
                    if d.printer_id == id:
                        self.detect_settings.remove(d)
                return

    
    def add_controller(self, id: str, controller: Controller) -> bool:
        # 确保id不重复
        for p in self.controller_list:
            if p.id == id:
                return False
            
        self.controller_list.append(IDController(id, controller))
        return True
    
    def remove_controller(self, id: str):
        for p in self.controller_list[:]:
            if p.id == id:
                self.controller_list.remove(p)
                # 删除所有该控制器的通道引用
                for c in self.channel_settings[:]:
                    if c.controller_id == id:
                        self.channel_settings.remove(c)

    def add_detect(self, id: str, detect: BrokenDetect) -> bool:
        # 确保id不重复
        for p in self.detect_list:
            if p.id == id:
                return False
            
        self.detect_list.append(IDBrokenDetect(id, detect))
        return True
    
    def remove_detect(self, id: str):
        for p in self.detect_list[:]:
            if p.id == id:
                self.detect_list.remove(p)
                # 删除所有检测器的引用
                for c in self.detect_settings[:]:
                    if c.detect_id == id:
                        self.detect_settings.remove(c)

    def add_channel_setting(self, printer_id: str, controller_id: str, channel: int) -> bool:
        if not self.is_printer_exist(printer_id):
            return False
        
        if not self.is_channel_exist(controller_id, channel):
            return False

        if self.is_channel_relation_exist(controller_id, channel):
            return False
        
        self.channel_settings.append(ChannelRelation(printer_id, controller_id, channel))
        return True

    def remove_channel_setting(self, printer_id: str, controller_id: str, channel_id: int):
        for p in self.channel_settings[:]:
            if controller_id == p.controller_id and channel_id == p.channel:
                self.channel_settings.remove(p)

    def add_detect_setting(self, printer_id: str, detect_id: str) -> bool:
        if not self.is_detect_exist(detect_id):
            return False

        # 确保控制器的通道只被添加一次
        if self.is_detect_relation_exist(detect_id):
            return False
        
        self.detect_settings.append(DetectRelation(printer_id, detect_id))
        return True

    def remove_detect_setting(self, printer_id: str, detect_id: str):
        for p in self.detect_settings[:]:
            if printer_id == p.printer_id and detect_id == p.detect_id:
                self.detect_settings.remove(p)

    def is_printer_exist(self, id: str) -> bool:
        for p in self.printer_list:
            if p.id == id:
                return True
        return False
    
    def is_channel_exist(self, controller_id: str, channel_id: int) -> bool:
        for p in self.controller_list:
            if p.id == controller_id:
                if channel_id < p.controller.channel_count and channel_id >= 0:
                    return True
        return False
    
    def is_detect_exist(self, id: str) -> bool:
        for p in self.detect_list:
            if p.id == id:
                return True
        return False
    
    def is_channel_relation_exist(self, controller_id: str, channel_index: int) -> bool:
        for p in self.channel_settings:
            if p.controller_id == controller_id and p.channel == channel_index:
                return True
        return False
    
    def is_detect_relation_exist(self, detect_id: str) -> bool:
        for p in self.detect_settings:
            if p.detect_id == detect_id:
                return True
        return False
    
    def get_printer_channel_settings(self, printer_id: str) -> list[ChannelRelation]:
        return [p for p in self.channel_settings if p.printer_id == printer_id]

    def get_printer(self, printer_id: str) -> PrinterClient:
        for p in self.printer_list:
            if p.id == printer_id:
                return p.client
        return None
    
    def get_printer_broken_detect(self, printer_id: str) -> list[BrokenDetect]:
        t =  [p for p in self.detect_list if p.id == printer_id]
        # 把 IDBrokenDetect 转换为 BrokenDetect
        return [p.detect for p in t]
    
    def get_controller(self, controller_id: str) -> Controller:
        for p in self.controller_list:
            if p.id == controller_id:
                return p.controller
        return None
        



