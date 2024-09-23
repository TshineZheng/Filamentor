from datetime import datetime
import json
import os
import ssl
import time
import paho.mqtt.client as mqtt

from src import consts
from src.broken_detect import BrokenDetect
import src.utils.gcode_util as gcode_util
from src.utils.json_util import ast
from src.utils.log import LOGD, LOGE, LOGI, LOGW, TAGLOG
from src.printer_client import Action, FilamentState, PrinterClient

# 定义服务器信息和认证信息
MQTT_PORT = 8883
BAMBU_CLIENT_ID = "Filamentor-Bambu-Client"
# noinspection SpellCheckingInspection
USERNAME = "bblp"

bambu_resume = '{"print":{"command":"resume","sequence_id":"1"},"user_id":"1"}'
bambu_pause = '{"print": {"sequence_id": "0","command": "pause","param": ""}}'
bambu_unload = '{"print":{"command":"ams_change_filament","curr_temp":220,"sequence_id":"1","tar_temp":220,"target":255},"user_id":"1"}'
bambu_load = '{"print":{"command":"ams_change_filament","curr_temp":220,"sequence_id":"1","tar_temp":220,"target":254},"user_id":"1"}'
bambu_done = '{"print":{"command":"ams_control","param":"done","sequence_id":"1"},"user_id":"1"}'
bambu_clear = '{"print":{"command": "clean_print_error","sequence_id":"1"},"user_id":"1"}'
bambu_status = '{"pushing": {"sequence_id": "0", "command": "pushall"}}'

MAGIC_CHANNEL = 1000
MAGIC_COMMAND = 2000
MAGIC_AWAIT = MAGIC_COMMAND


class BambuClientConfig(object):

    def __init__(self, printer_ip: str, lan_password: str, device_serial: str) -> None:
        self.printer_ip = printer_ip
        self.lan_password = lan_password
        self.device_serial = device_serial


class BambuClient(PrinterClient, TAGLOG):

    @staticmethod
    def type_name() -> str:
        return "bambu_client"

    def tag(self):
        return self.type_name()

    def __eq__(self, other):
        if isinstance(other, BambuClient):
            return self.config.printer_ip == other.config.printer_ip
        return False

    def __init__(self, config: BambuClientConfig):
        super().__init__()

        self.fbd = BambuBrokenDetect(self)
        self.config = config

        self.TOPIC_SUBSCRIBE = f"device/{config.device_serial}/report"
        self.TOPIC_PUBLISH = f"device/{config.device_serial}/request"

        client = mqtt.Client(client_id=BAMBU_CLIENT_ID)
        # 设置TLS
        # 如果服务器使用自签名证书，请使用ssl.CERT_NONE
        client.tls_set(cert_reqs=ssl.CERT_NONE)
        client.tls_insecure_set(True)  # 只有在使用自签名证书时才设置为True

        # 设置用户名和密码
        client.username_pw_set(USERNAME, config.lan_password)

        # 设置回调函数
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_message = self.on_message

        self.client = client

        self.clean()

        self.read_env()

    def read_env(self):
        self.change_count = int(os.getenv("CHANGE_COUNT", '0'))
        self.latest_home_change_count = int(os.getenv("LATEST_HOME_CHANGE_COUNT", '0'))
        LOGI(f'CHANGE_COUNT: {self.change_count}')
        LOGI(f'LATEST_HOME_CHANGE_COUNT: {self.latest_home_change_count}')

    def isPrinting(self):
        return self.print_status == 'PAUSE' or self.print_status == 'RUNNING'

    def clean(self):
        self.wating_pause_flag = False
        self.mc_percent = 0
        self.mc_remaining_time = 0
        self.magic_command = 0
        self.cur_layer = 0
        self.new_fila_temp = 0
        self.pre_fila_temp = 0
        self.next_extruder = -1
        self.change_count = 0
        self.latest_home_change_count = 0
        self.gcodeInfo = gcode_util.GCodeInfo()
        self.print_status = 'unkonw'

        # self.trigger_pause = False

    @classmethod
    def from_dict(cls, config: dict):
        return cls(
            BambuClientConfig(
                config["printer_ip"],
                config["lan_password"],
                config["device_serial"]
            ))

    def to_dict(self) -> dict:
        return {
            'printer_ip': self.config.printer_ip,
            'lan_password': self.config.lan_password,
            'device_serial': self.config.device_serial
        }

    def publish_gcode_await(self, gcode, after_gcode=None):
        save_percent = self.mc_percent
        self.publish_gcode(f'{gcode}\nM400\nM73 P101\n{after_gcode if after_gcode else ""}\n')
        ts = 0
        while self.mc_percent != 101:
            if ts < datetime.now().timestamp():
                self.publish_status()
                ts = datetime.now().timestamp() + 0.5
        self.publish_gcode(f'M73 P{save_percent}\n')

    def publish_gcode(self, g_code):
        operation_code = '{"print": {"sequence_id": "1", "command": "gcode_line", "param": "' + g_code + '"},"user_id":"1"}'
        self.client.publish(self.TOPIC_PUBLISH, operation_code)

    def publish_resume(self):
        self.client.publish(self.TOPIC_PUBLISH, bambu_resume)

    def publish_status(self):
        self.client.publish(self.TOPIC_PUBLISH, bambu_status)

    def publish_clear(self):
        self.client.publish(self.TOPIC_PUBLISH, bambu_clear)

    def publish_pause(self):
        self.client.publish(self.TOPIC_PUBLISH, bambu_pause)

    # noinspection PyUnusedLocal
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            LOGI("连接竹子成功")
            # 连接成功后订阅主题
            client.subscribe(self.TOPIC_SUBSCRIBE, qos=1)
        else:
            LOGE(f"连接竹子失败，错误代码 {rc}")

    # noinspection PyUnusedLocal
    def on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        if not self.is_running:
            return

        LOGE("连接已断开，请检查打印机状态，以及是否有其它应用占用了打印机")
        self.reconnect(client)

    def reconnect(self, client, delay=3):
        while True:
            LOGE("尝试重新连接竹子...")
            try:
                client.reconnect()
                break  # 重连成功则退出循环
            except:
                LOGE(f"重连竹子失败 {delay} 秒后重试...")
                time.sleep(delay)  # 等待一段时间后再次尝试

    def on_message(self, client, userdata, message: mqtt.MQTTMessage):
        try:
            payload = str(message.payload.decode('utf-8'))
            self.process_message(payload)
        except Exception as e:
            LOGE(f"mqtt数据解析失败: {e}")
            return

    def process_message(self, payload):
        try:
            json_data = json.loads(payload)
            LOGD(f'bambu_mqtt_msg -> {payload}')
        except Exception as e:
            LOGE(f"JSON解析失败: {e}")
            return

        if 'print' not in json_data:
            return

        json_print = json_data["print"]

        if 'gcode_state' in json_print:
            gcode_state = json_print["gcode_state"]

            if gcode_state != self.print_status:
                if self.print_status != 'unkonw':
                    if 'PAUSE' == gcode_state:
                        self.wating_pause_flag = True
                    if 'FINISH' == gcode_state:
                        self.on_action(Action.TASK_FINISH)
                        self.clean()

                    if 'FAILED' == gcode_state:
                        if ast(json_print, 'print_error', 50348044):
                            self.on_action(Action.TASK_FAILED)
                            self.clean()
                self.print_status = gcode_state

        if "hw_switch_state" in json_print:
            self.on_action(Action.FILAMENT_SWITCH,
                           FilamentState.YES if json_print["hw_switch_state"] == 1 else FilamentState.NO)

        if 'command' in json_print:
            if json_print["command"] == 'project_file':
                if 'param' in json_print and 'url' in json_data['print'] and 'subtask_name' in json_data['print']:
                    p = json_data['print']['param']
                    url = json_data['print']['url']
                    subtask_name = json_data['print']['subtask_name']
                    self.gcodeInfo = gcode_util.decodeFromZipUrl(url, p)
                    self.on_action(Action.TASK_START, {
                        'first_filament': self.gcodeInfo.first_channel,
                        'subtask_name': subtask_name
                    })

        if not self.isPrinting():
            return

        if 'mc_percent' in json_print:
            self.mc_percent = json_print["mc_percent"]

        if 'mc_remaining_time' in json_print:
            self.mc_remaining_time = json_print["mc_remaining_time"]

        if 'layer_num' in json_print:
            layer_num = json_print["layer_num"]

            if layer_num >= MAGIC_CHANNEL:
                # 解码 num
                num_adjusted = layer_num - MAGIC_CHANNEL
                # 提取 next_extruder
                next_extruder = num_adjusted // 1000
                # 提取 new_filament_temp
                new_filament_temp = num_adjusted % 1000
                if next_extruder != self.next_extruder:
                    LOGI(f'next_extruder: {next_extruder} new_filament_temp: {new_filament_temp}')
                    if ast(json_print, 'gcode_state', 'PAUSE'):  # 暂停状态
                        # self.trigger_pause = False
                        self.next_extruder = next_extruder
                        self.new_fila_temp = new_filament_temp
                        self.change_count += 1

                        # FIXME: 这里实际上应该是当前耗材温度，而不是新耗材温度
                        # 因为恢复暂停时会自动恢复之前的温度，所以这里的温度操作，实际上是为了维持温度，避免因为暂停导致温度暂停
                        # 而且换料后，有一小断耗材还在打印头上，需要挤出，也需要维持之前的温度
                        self.on_action(Action.CHANGE_FILAMENT, {
                            'next_extruder': next_extruder,
                            'next_filament_temp': self.pre_fila_temp if self.pre_fila_temp > 0 else new_filament_temp
                        })

                        self.pre_fila_temp = new_filament_temp
                    else:
                        self.publish_status()
            else:
                self.cur_layer = layer_num

    def refresh_status(self):
        self.publish_status()

    def fix_z(self, pre_tem):
        cc = self.change_count - self.latest_home_change_count  # 计算距离上一次回中后换了几次色了
        modle_z = self.cur_layer * self.gcodeInfo.layer_height  # 当前模型已经打印了多高
        need_z_home = False
        if consts.FIX_Z_PAUSE_COUNT == 0:  # 高度判断
            z_height = cc * consts.PAUSE_Z_OFFSET + modle_z    # 计算当前z高度
            LOGI(f'暂停次数:{self.change_count}, 抬高次数{cc}, 当前z高度{z_height}')
            if z_height > consts.DO_HOME_Z_HEIGHT:  # 如果当前高度超过回中预设高度则回中
                need_z_home = True
        else:
            if cc >= consts.FIX_Z_PAUSE_COUNT:  # 次数判断
                need_z_home = True

        if need_z_home:
            LOGI('修复z高度')
            self.publish_gcode_await(f'G1 E-28 F500\n{consts.FIX_Z_GCODE}\nG1 Z{modle_z + 2} F30000\n', after_gcode=f'M104 S{pre_tem}\n')
            self.latest_home_change_count = self.change_count
        else:
            self.pull_filament(pre_tem)

    def on_unload(self, pre_tem=255):
        super().on_unload(pre_tem)

        if consts.FIX_Z and consts.FIX_Z_GCODE:
            self.fix_z(pre_tem)
        else:
            self.pull_filament(pre_tem)

    def pull_filament(self, pre_tem=255):
        # 抽回一段距离，提前升温
        self.publish_gcode_await('G1 E-28 F500\n', f'M104 S{pre_tem}\n')

    def resume(self):
        super().resume()
        self.publish_gcode_await('M83\nG1 E3 F500\n')    # 夹紧耗材
        self.publish_resume()
        self.publish_clear()
        self.publish_status()

    def start(self):
        super().start()
        self.client.connect(self.config.printer_ip, MQTT_PORT, 60)
        self.client.subscribe(self.TOPIC_SUBSCRIBE, qos=1)
        self.client.loop_start()
        self.fbd.start()

    def stop(self):
        super().stop()
        self.client.disconnect()
        self.client.loop_stop()
        self.fbd.stop()

    def filament_broken_detect(self) -> BrokenDetect:
        return self.fbd


class BambuBrokenDetect(BrokenDetect):
    @staticmethod
    def type_name() -> str:
        return "bambu_broken_detect"

    def __init__(self, bambu_client: BambuClient):
        self.bambu_client = bambu_client
        self.fila_state = FilamentState.UNKNOWN

    def is_filament_broken(self) -> bool:
        return FilamentState.NO == self.fila_state

    def get_safe_time(self) -> float:
        return 2

    def on_printer_action(self, action: Action, data):
        if Action.FILAMENT_SWITCH == action:
            self.fila_state = data

    def start(self):
        self.bambu_client.add_on_action(self.on_printer_action)

    def stop(self):
        self.bambu_client.remove_on_action(self.on_printer_action)

    def to_dict(self) -> dict:
        return super().to_dict()
