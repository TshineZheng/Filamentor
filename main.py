import time
from ams_core import AmsCore
from app_config import AppConfig, ChannelRelation, DetectRelation, IDBrokenDetect, IDController, IDPrinterClient
from controller import ChannelAction
from impl.bambu_client import BambuClient, BambuClientConfig
from impl.mqtt_broken_detect import MQTTBrokenDetect
from impl.yba_ams_controller import YBAAMSController
from mqtt_config import MQTTConfig

PRINTER_IP = ''    # 打印机ip
PRINTER_LAN_PASSWORD = ''   # 打印机Lan密码
PRINTER_DEVICE_SERIAL = ''   # 打印机设备序列号

YBAAMS_IP = ''    # yba AMS ip

CUR_CHANNEL = 0     # 当前通道

CHANGE_TEM = 255    # 换色问题

################################################

YBAAMS_PORT = 3333

MQTT_SERVER = 'MQTT 服务器'
MQTT_PORT = 1883
MQTT_USERNAME = 'MQTT 用户名'
MQTT_PASSWORD = 'MQTT 密码'

mqtt_config = MQTTConfig(MQTT_SERVER, MQTT_PORT, 'Filamentor', MQTT_USERNAME, MQTT_PASSWORD)

bambu_client = BambuClient(BambuClientConfig(PRINTER_IP, PRINTER_LAN_PASSWORD, PRINTER_DEVICE_SERIAL))

yba_asm = YBAAMSController(YBAAMS_IP, YBAAMS_PORT, 3)

app_config = AppConfig(
        printers=[
            IDPrinterClient('bambu-1', bambu_client)
        ], 
        controllers=[
            IDController('yba-ams-1', yba_asm)
        ], 
        detects=[
            # IDBrokenDetect('detector-1', MQTTBrokenDetect(mqtt_config))
        ], 
        channel_set=[
            ChannelRelation('bambu-1', 'yba-ams-1', 0), 
            ChannelRelation('bambu-1', 'yba-ams-1', 1),
            ChannelRelation('bambu-1', 'yba-ams-1', 2)
        ], 
        detect_set=[
            # DetectRelation('bambu-1', 'yba-ams-1', 'detector-1')
        ], 
        mqtt_config=mqtt_config
    )

if __name__ == '__main__':

    ams = AmsCore(app_config, 'bambu-1', CUR_CHANNEL, CHANGE_TEM)
    ams.run()

    ams.driver_control(ams.filament_current, ChannelAction.PUSH)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ams.stop()
