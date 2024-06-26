import json
from app_config import AppConfig, ChannelRelation, DetectRelation, IDBrokenDetect, IDController, IDPrinterClient
from impl.bambu_client import BambuClient, BambuClientConfig
from impl.mqtt_broken_detect import MQTTBrokenDetect
from impl.yba_ams_controller import YBAAMSController
from mqtt_config import MQTTConfig

def make_config() -> AppConfig:
        config = AppConfig()

        config.printer_list = [
            IDPrinterClient('bambu_1', BambuClient(BambuClientConfig("127.0.0.1", 'lan_pwd', "device_serial"))),
            IDPrinterClient('bambu_2', BambuClient(BambuClientConfig("127.0.0.2", 'lan_pwd', "device_serial"))),
        ]

        config.controller_list = [
            IDController('yba_ams_1', YBAAMSController('192.168.10.1', 1883, 4)),
            IDController('yba_ams_2', YBAAMSController('192.168.10.2', 1883, 3)),
        ]

        config.detect_list = [
            IDBrokenDetect('mqtt_detect_1', MQTTBrokenDetect(MQTTConfig('192.168.10.2', 1833, 'client_id', 'username', 'password'))),
            IDBrokenDetect('mqtt_detect_2', MQTTBrokenDetect(MQTTConfig('192.168.10.2', 1833, 'client_id', 'username', 'password'))),
        ]

        config.channel_relations = [
            ChannelRelation('bambu_1', 'yba_ams_1', 0),
            ChannelRelation('bambu_1', 'yba_ams_1', 1),
            ChannelRelation('bambu_1', 'yba_ams_1', 2),
            # ChannelRelation('bambu_1', 'yba_ams_1', 3),
            ChannelRelation('bambu_2', 'yba_ams_2', 0),
            ChannelRelation('bambu_2', 'yba_ams_2', 1),
            ChannelRelation('bambu_2', 'yba_ams_2', 2),
        ]

        config.detect_relations = [
            DetectRelation('bambu_1', 'mqtt_detect_1'),
            DetectRelation('bambu_2', 'mqtt_detect_2'),
        ]

        config.mqtt_config = MQTTConfig('192.168.10.1', 1833, 'client_id', 'username', 'password')

        return config


def test_app_config_json():
        config =   make_config()

        json_data = json.dumps(config.to_dict(), indent=4)

        config.load_from_dict(json.loads(json_data))

        assert config.to_dict() == json.loads(json_data)

def test_add_printer():
    config = make_config()
    bambu_client = BambuClient(BambuClientConfig("127.0.0.3", 'lan_pwd', "device_serial"))
    assert config.add_printer('bambu_3', bambu_client) == True
    assert config.printer_list[-1].id == 'bambu_3'

    assert config.add_printer('bambu_3', bambu_client) == False

def test_remove_printer():
    config = make_config()
    config.remove_printer('bambu_1')
    for i in config.printer_list:
        assert i.id != 'bambu_1'
    
    for i in config.channel_relations:
        assert i.printer_id != 'bambu_1'

    for i in config.detect_relations:
        assert i.printer_id != 'bambu_1'

def test_add_controller():
    config = make_config()
    bambu_client = BambuClient(BambuClientConfig("127.0.0.3", 'lan_pwd', "device_serial"))
    assert config.add_controller('yba_ams_3', bambu_client, 'ams1') == True,any
    assert config.controller_list[-1].id == 'yba_ams_3'

    assert config.add_controller('yba_ams_3', bambu_client,'ams1') == False,any

def test_remove_controller():
    config = make_config()
    config.remove_controller('yba_ams_1')
    for i in config.controller_list:
        assert i.id != 'yba_ams_1'
    
    for i in config.channel_relations:
        assert i.controller_id != 'yba_ams_1'

def test_add_detect():
    config = make_config()
    bambu_client = BambuClient(BambuClientConfig("127.0.0.3", 'lan_pwd', "device_serial"))
    assert config.add_detect('mqtt_detect_3', bambu_client) == True
    assert config.detect_list[-1].id == 'mqtt_detect_3'

    assert config.add_detect('mqtt_detect_3', bambu_client) == False

def test_remove_detect():
    config = make_config()
    config.remove_detect('mqtt_detect_1')
    for i in config.detect_list:
        assert i.id != 'mqtt_detect_1'

def test_add_channel_relation():
    config = make_config()
    # 增加已经被使用的通道
    assert config.add_channel_setting('bambu_2', 'yba_ams_1', 0) == False
    assert config.add_channel_setting('bambu_1', 'yba_ams_2', 0) == False

    # 增加一个在控制器中不存在的通道
    assert config.add_channel_setting('bambu_1', 'yba_ams_1', 4) == False

    # 增加一个通道到一个不存在的打印机
    assert config.add_channel_setting('bambu_3', 'yba_ams_1', 0) == False

    # 增加一个不存在的控制器到打印机
    assert config.add_channel_setting('bambu_1', 'yba_ams_3', 0) == False

    # 增加未使用的通道
    assert config.add_channel_setting('bambu_1', 'yba_ams_1', 3) == True

def test_remove_channel_relation():
    config = make_config()
    config.remove_channel_setting('bambu_1', 'yba_ams_1', 0)
    for i in config.channel_relations:
        assert not (i.printer_id == 'bambu_1' and i.controller_id == 'yba_ams_1' and i.channel==0)

def test_add_detect_relation():
    config = make_config()
    # 增加已经被使用的检测
    assert config.add_detect_setting('bambu_1', 'mqtt_detect_1') == False

    # 增加不存在的检测器
    assert config.add_detect_setting('bambu_1', 'mqtt_detect_9') == False

    # 增加未使用的检测
    config.add_detect('mqtt_detect_9', BambuClient(BambuClientConfig("127.0.0.3", 'lan_pwd', "device_serial")))
    assert config.add_detect_setting('bambu_1', 'mqtt_detect_9') == True

def test_remove_detect_relation():
    config = make_config()
    config.remove_detect_setting('bambu_1', 'mqtt_detect_1')
    for i in config.detect_relations:
        assert i.detect_id != 'mqtt_detect_1'

