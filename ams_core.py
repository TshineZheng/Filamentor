import threading
import time
from typing import List
from app_config import AppConfig
from impl.bambu_broken_detect import BambuBrokenDetect
from impl.bambu_client import BambuClient, BambuClientConfig
import printer_client as printer
from mqtt_config import MQTTConfig
from broken_detect import BrokenDetect
from controller import ChannelAction, Controller
from datetime import datetime

class AmsCore(object):
    def __init__(
        self,
        app_config: AppConfig,
        use_printer: str,
        cur_channel: int,
        change_tem: int,
    ) -> None:
        self.filament_current = cur_channel
        self.filament_next = 0
        self.change_count = 0
        self.change_tem = change_tem
        self.filament_changing = False
        self.app_config = app_config
        self.printer_client = app_config.get_printer(use_printer)
        self.broken_detects = app_config.get_printer_broken_detect(use_printer)

        if self.broken_detects is None or len(self.broken_detects) == 0:
            self.broken_detects = [self.printer_client.filament_broken_detect()]   # 如果没有自定义断线检测，使用打印默认的

        controllers_id:list[str] = []
        self.channels: List[tuple[Controller, int]] = []
        for c in app_config.get_printer_channel_settings(use_printer):
            if c.controller_id not in controllers_id:
                controllers_id.append(c.controller_id)
            self.channels.append([app_config.get_controller(c.controller_id), c.channel])

        self.controllers = [app_config.get_controller(c) for c in controllers_id]

    def run(self):
        self.printer_client.start()    # 启动打印机连接

        for c in self.controllers: # 启动所有控制器
            c.start()

        for bd in self.broken_detects:  # 启动所有断线检测
            bd.start()

    def stop(self):
        self.printer_client.stop() # 关闭打印机连接

        for c in self.controllers: # 启动所有控制器
            c.stop()

        for bd in self.broken_detects:  # 关闭所有断线检测
            bd.stop()

    def driver_control(self, channel: int, action: ChannelAction):
        c,i = self.channels[channel]
        c.control(i, action)

    def on_resumed(self):
        c,i = self.channels[self.filament_current]
        # 非主动送料的通道，直接松开
        if not c.is_active_push(i):
            c.control(i, ChannelAction.STOP)

    def is_filament_broken(self) -> bool:
        """当所有断料检测器都没有料时，返回 True

        Returns:
            bool: _description_
        """
        for bd in self.broken_detects:
            if not bd.is_filament_broken():
                return False
        return True
    
    def get_max_broken_safe_time(self) -> int:
        return max([bd.safe_time() for bd in self.broken_detects])

    def run_filament_change(self, next_filament: int):
        if self.filament_changing:
            return
        self.filament_changing = True
        self.thread = threading.Thread(
            target=self.filament_change, args=(next_filament,))
        self.thread.start()

    def filament_change(self, next_filament: int):
        # FIXME: 要增加通道不匹配的判断，比如接到换第4通道，结果我们只有3通道，可以呼叫用户确认，再继续

        self.change_count += 1
        print(f'开始第 {self.change_count} 次换色')
        self.filament_next = next_filament
        print(f'当前通道 {self.filament_current + 1}，下个通道 {self.filament_next + 1}')

        if self.filament_current == self.filament_next:
            self.printer_client.resume()
            print("无需换色, 恢复打印")
            self.filament_changing = False
            return

        print("等待退料完成")
        self.driver_control(self.filament_current, ChannelAction.PULL)   # 回抽当前通道
        self.printer_client.on_unload(self.change_tem)

        now = datetime.now().timestamp
        max_pull_time = now + 60 * 10_000

        # 等待所有断料检测器都没有料
        while self.is_filament_broken():
            time.sleep(2)
            if datetime.now().timestamp() - now > 10_000:
                print("退料超时，抖一抖")
                self.driver_control(self.filament_current, ChannelAction.PUSH)
                time.sleep(1)
                self.driver_control(self.filament_current, ChannelAction.PULL)
                now = datetime.now().timestamp
            if max_pull_time < datetime.now().timestamp():
                print("退不出来喊人")
                # TODO: 发出警报
                while True:
                    time.sleep(1)

        print("退料检测到位")

        safe_time = self.get_max_broken_safe_time()
        if safe_time > 0:
            time.sleep(safe_time)   # 再退一点
            print("退料到安全距离")

        self.driver_control(self.filament_current, ChannelAction.STOP)   # 停止抽回

        # 强行让打印机材料状态变成无，避免万一竹子消息延迟或什么的，不要完全相信别人的接口，如果可以自己判断的话（使用自定义断料检测器有效）
        self.printer_client.set_filament_state(printer.FilamentState.NO)

        time.sleep(1)  # 休息下呗，万一板子反映不过来呢

        self.driver_control(self.filament_next, ChannelAction.PUSH)   # 输送下一个通道
        print("开始输送下一个通道")

        # 到料目前还只能通过打印机判断，只能等了，不断刷新
        while self.printer_client.get_filament_state() != printer.FilamentState.YES:    # 等待打印机料线到达
            self.printer_client.refresh_status()    # 刷新打印机状态
            # TODO: 这里需要增加超时机制，如果一直送不到，需要呼叫用户确认处理
            time.sleep(2)

        print("料线到达")
        self.filament_current = self.filament_next
        print("换色完成")
        self.printer_client.resume()
        print("恢复打印")

        self.on_resumed()

        self.filament_changing = False

    def on_printer_action(self, action: printer.Action, data):
        if action == printer.Action.CHANGE_FILAMENT:
            self.run_filament_change(data)

        if action == printer.Action.FILAMENT_SWITCH_0:
            pass

        if action == printer.Action.FILAMENT_SWITCH_1:
            pass