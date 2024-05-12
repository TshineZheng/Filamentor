import json
import ssl
import time
import paho.mqtt.client as mqtt

from broken_detect import BrokenDetect
from utils.json_util import ast
from utils.log import LOGD, LOGE, LOGI, LOGW, TAGLOG
from printer_client import Action, FilamentState, PrinterClient

# 定义服务器信息和认证信息
MQTT_PORT = 8883
BAMBU_CLIENT_ID = "open-ams"
# noinspection SpellCheckingInspection
USERNAME = "bblp"

bambu_resume = '{"print":{"command":"resume","sequence_id":"1"},"user_id":"1"}'
bambu_pause = '{"print": {"sequence_id": "0","command": "pause","param": ""}}'
bambu_unload = '{"print":{"command":"ams_change_filament","curr_temp":220,"sequence_id":"1","tar_temp":220,"target":255},"user_id":"1"}'
bambu_load = '{"print":{"command":"ams_change_filament","curr_temp":220,"sequence_id":"1","tar_temp":220,"target":254},"user_id":"1"}'
bambu_done = '{"print":{"command":"ams_control","param":"done","sequence_id":"1"},"user_id":"1"}'
bambu_clear = '{"print":{"command": "clean_print_error","sequence_id":"1"},"user_id":"1"}'
bambu_status = '{"pushing": {"sequence_id": "0", "command": "pushall"}}'

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

    def __init__(self, config: BambuClientConfig):
        super().__init__()

        self.fbd = None
        self.config = config

        self.TOPIC_SUBSCRIBE = f"device/{config.device_serial}/report"
        self.TOPIC_PUBLISH = f"device/{config.device_serial}/request"

        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=BAMBU_CLIENT_ID)
        # 设置TLS
        client.tls_set(cert_reqs=ssl.CERT_NONE)  # 如果服务器使用自签名证书，请使用ssl.CERT_NONE
        client.tls_insecure_set(True)  # 只有在使用自签名证书时才设置为True

        # 设置用户名和密码
        client.username_pw_set(USERNAME, config.lan_password)

        # 设置回调函数
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_message = self.on_message

        self.client = client

        self.wating_pause_flag = False
        self.mc_percent = 0
        self.mc_remaining_time = 0
        self.mc_command = 0

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
    def on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            LOGI("连接竹子成功")
            # 连接成功后订阅主题
            client.subscribe(self.TOPIC_SUBSCRIBE, qos=1)
        else:
            LOGE(f"连接竹子失败，错误代码 {rc}")

    # noinspection PyUnusedLocal
    def on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
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

    def on_message(self, client, userdata, message):
        try:
            payload = str(message.payload.decode('utf-8'))
            json_data = json.loads(payload)
            LOGD(f'bambu_mqtt_msg -> {payload}')
        except json.JSONDecodeError:
            LOGE("JSON解析失败")
            return

        if "print" in json_data:
            json_print = json_data["print"]
            if "mc_percent" in json_print and "mc_remaining_time" in json_print:
                mc_percent = json_print["mc_percent"]
                if mc_percent == 101:  # 换色指令
                    if ast(json_print, 'gcode_state', 'PAUSE'): # 暂停状态
                        filament_next = json_print["mc_remaining_time"]  # 更换通道
                        self.on_action(Action.CHANGE_FILAMENT, filament_next)
                    else:
                        # 有一种情况是暂停了，但打印机不会发消息过来，所以要确保打印机是在暂停状态再执行
                        # FIXME: 还有一种情况是已经恢复打印，但进度没有更新，导致一直触发换色指令，也就会一直尝试获取打印状态，直到下次换色，或进度更新，可能需要通过gcode修复(bambu)
                        LOGW('收到换色指令，但打印机不是暂停状态，重新刷新状态')
                        self.publish_status()
                elif mc_percent >=0 and mc_percent <= 100:
                    self.mc_percent = mc_percent
                    self.mc_remaining_time = json_print["mc_remaining_time"]
                else:
                    self.mc_command = mc_percent

            if "hw_switch_state" in json_print:
                self.filament_state = FilamentState.YES if json_print["hw_switch_state"] == 1 else FilamentState.NO
                self.on_action(Action.FILAMENT_SWITCH, self.filament_state)

            if 'command' in json_print:
                if json_print["command"] == 'project_file':
                    if 'param' in json_print and 'url' in json_data['print'] and 'subtask_name' in json_data['print']:
                        p = json_data['print']['param']
                        url = json_data['print']['url']
                        subtask_name = json_data['print']['subtask_name']
                        ci = BambuClient.get_first_fila_from_gcode(url, p)
                        self.on_action(Action.TASK_START, {
                            'first_filament': ci,
                            'subtask_name': subtask_name
                        })

            if "gcode_state" in json_print:
                gcode_state = json_print["gcode_state"]
                if "PAUSE" == gcode_state:
                    self.wating_pause_flag = True
                if 'FINISH' == gcode_state:
                    if self.mc_percent == 100:
                        self.on_action(Action.TASK_FINISH)
                if 'FAILED' == gcode_state:
                    if ast(json_print, 'print_error', 50348044):
                        self.on_action(Action.TASK_FAILED)
                        

    def refresh_status(self):
        self.publish_status()

    def on_unload(self, pre_tem=255):
        super().on_unload(pre_tem)
        self.publish_gcode("G1 E-25 F500\nM109 S" + str(pre_tem) + "\n")  # 抽回一段距离，提前升温
        # 这B代码，好像是少加个 \n，搞的换完色，打印机就缓慢回抽，导致疯狂飞头。
        # 也可能是没加 str()，不想试了，头很松了

    def resume(self):
        super().resume()
        self.publish_resume()
        self.publish_clear()
        self.publish_gcode(f"M73 P{self.mc_percent} R{self.mc_remaining_time}\n")

    def start(self):
        super().start()
        self.client.connect(self.config.printer_ip, MQTT_PORT, 60)
        self.client.subscribe(self.TOPIC_SUBSCRIBE, qos=1)
        self.client.loop_start()

    def stop(self):
        super().stop()
        self.client.disconnect()

    def filament_broken_detect(self) -> BrokenDetect:
        if self.fbd is None:
            self.fbd = BambuBrokenDetect(self)

        return self.fbd
    
    def waiting_pause(self):
        self.waiing_199_flag = False
        while not self.wating_pause_flag:
            time.sleep(1)

    def waiting_mc_command(self, mc: int):
        while not self.mc_command == mc:
            time.sleep(1)
    
    def change_filament(self, ams, next_fila: int, change_temp: int = 255):
        # time.sleep(10)
        # self.LOGI('发送暂停指令')
        self.publish_pause()    # 先让打印机暂停

        self.waiting_pause()    # 等待打印机暂停

        self.LOGI('已暂停')

        self.LOGI('开始切料')

        # 执行切料
        cut_code = f"""
            M106 P1 S0
            M106 P2 S0
            M109 S{change_temp}

            ; cut filament
            M17 S
            M17 X1.1
            G1 X180 F18000
            G1 X201 F1000
            G1 E-2 F500
            G1 X180 F3000
            G1 X-13.5 F18000
            M17 R

            M400

            M73 P198 R0
        """.replace('\n', '\\n')
        self.publish_gcode(cut_code)
        self.waiting_mc_command(198)

        self.LOGI('切料完成')

        ams.run_filament_change(next_fila, self.__change_fila_swip())

    def __change_fila_swip(self):
        self.LOGI('开始冲刷')
        filament_e_feedrate = 224
        new_filament_temp = 255
        wipe_code = f"""
            M109 S{new_filament_temp}
            M106 P1 S60

            G1 E35 F{filament_e_feedrate}

            G1 E-2 F1800
            G1 E2 F300

            M400

            M73 P199 R0
        """.replace('\n', '\\n')
        self.publish_gcode(wipe_code)
        self.waiting_mc_command(199)
        self.LOGI('冲刷完成')

    @staticmethod
    def get_first_fila_from_gcode(zip_url: str, file_path: str) -> int:
        import requests
        import zipfile
        import io

        # 发送GET请求并获取ZIP文件的内容
        response = requests.get(zip_url)

        # 确保请求成功
        if response.status_code == 200:
            # 使用BytesIO读取下载的内容
            zip_data = io.BytesIO(response.content)
            # 使用zipfile读取ZIP文件
            with zipfile.ZipFile(zip_data) as zip_file:
                # 获取ZIP文件中的所有文件名列表
                file_names = zip_file.namelist()
                # 遍历文件名列表
                for file_name in file_names:
                    # 如果文件名符合您要查找的路径
                    if file_path == file_name:
                        # 打开文本文件
                        with zip_file.open(file_name) as file:
                            # 逐行读取文件内容
                            for line in file:
                                # 将bytes转换为str
                                line_str = line.decode('utf-8')
                                # 检查是否包含特定字符串
                                if line_str.startswith('M620 S'):
                                    # 找到匹配的行，返回内容
                                    text =  line_str.strip()
                                    import re
                                    # 正则表达式模式，用于匹配'M620 S'后面的数字，直到遇到非数字字符
                                    pattern = r'M620 S(\d+)'
                                    # 搜索匹配的内容
                                    match = re.search(pattern, text)
                                    # 如果找到匹配项，则提取数字
                                    if match:
                                        number = match.group(1)
                                        print(number)  # 输出匹配到的数字
                                        return int(int(number))
        return -1


class BambuBrokenDetect(BrokenDetect):
    def type_name() -> str:
        return "bambu_broken_detect"

    def __init__(self, bambu_client: BambuClient):
        super().__init__()
        self.bambu_client = bambu_client

    def to_dict(self) -> dict:
        return super().to_dict()

    def is_filament_broken(self) -> bool:
        self.bambu_client.refresh_status()
        return self.bambu_client.get_filament_state() == FilamentState.NO

    def safe_time(self) -> float:
        return 2

    def start(self):
        return super().start()

    def stop(self):
        return super().stop()