import time
from filament_broken_detect import FilamentBrokenDetect
from config.mqtt_config import MQTTConfig
import paho.mqtt.client as mqtt

TOPIC = '/openams/filament_broken_detect'

class MQTTFilamentBrokenDetect(FilamentBrokenDetect):
    """断料检测服务

    通过监听 {TOPIC} 主题，检测打印机是否断料

    当监听数据为 "1" 时表示有料，当监听数据为 "0" 时表示无料

    """
    def __init__(self, mqtt_config: MQTTConfig):
        self.mqtt_config = mqtt_config
        self.topic = TOPIC
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=mqtt_config.client_id)
        self.client.username_pw_set(mqtt_config.username, mqtt_config.password)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.latest_state = None

    def start(self):
        # 连接到MQTT服务器
        self.client.connect(self.mqtt_config.server, self.mqtt_config.port, 60)

        # 订阅主题
        self.client.subscribe(self.topic, qos=1)

        # 启动循环，以便客户端能够处理回调
        self.client.loop_start()

    def stop(self):
        self.client.disconnect()

    def on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            print("连接MQTT成功")
            self.client.subscribe(self.topic, qos=1)
        else:
            print(f"连接MQTT失败，错误代码 {rc}")

    def on_disconnect(self, client, userdata, rc, properties):
        print("MQTT连接已断开，正在尝试重新连接")
        self.reconnect(client)

    def reconnect(self, client, delay=3):
        while True:
            print("尝试重新连接MQTT...")
            try:
                client.reconnect()
                break  # 重连成功则退出循环
            except:
                print(f"重连MQTT失败 {delay} 秒后重试...")
                time.sleep(delay)  # 等待一段时间后再次尝试

    def on_message(self, client, userdata, message):
        payload = str(message.payload.decode('utf-8'))
        print(f"断料检测：{payload}")
        if payload == '1' or payload == '0':
            self.latest_state = payload
        
    def get_latest_state(self):
        return self.latest_state
    
    def is_filament_broken(self) -> bool:
        """判断是否断料

        Returns:
            bool: 是否断料
        """
        if self.latest_state == '0':
            return True
        else:
            return False
    
if __name__ == '__main__':
    config = MQTTConfig("192.168.10.233", 1883, "filament_broken_detect_service_test", "", "")

    filament_broken_detect_service = MQTTFilamentBrokenDetect(config)

    filament_broken_detect_service.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        filament_broken_detect_service.stop() 

