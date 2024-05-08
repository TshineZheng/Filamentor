import threading
import time
from datetime import datetime
from typing import List

import printer_client as printer
from app_config import AppConfig
from controller import ChannelAction, Controller
from log import LOGD, LOGI


class AmsCore(object):
    def __init__(
        self,
        app_config: AppConfig,
        use_printer: str,
        cur_channel: int,
        change_tem: int,
    ) -> None:
        self.fila_cur = cur_channel
        self.fila_next = 0
        self.change_count = 0
        self.change_tem = change_tem
        self.fila_changing = False
        self.app_config = app_config
        self.printer_client = app_config.get_printer(use_printer)
        self.printer_client.on_action = self.on_printer_action    

        self.broken_detects = app_config.get_printer_broken_detect(use_printer)

        if self.broken_detects is None or len(self.broken_detects) == 0:
            self.broken_detects = [self.printer_client.filament_broken_detect()]   # 如果没有自定义断线检测，使用打印默认的
            LOGI(f'打印机{use_printer} 没有配置断料检测器，使用打印机自己的断料检测器')

        self.channels: List[tuple[Controller, int]] = []    # 控制器对象, 通道在控制器上的序号
        for c in app_config.get_printer_channel_settings(use_printer):
            self.channels.append([app_config.get_controller(c.controller_id), c.channel])

        LOGD(f'打印机: {use_printer}, 通道数量{len(self.channels)}, 断料检测器数量{len(self.broken_detects)}')
        # 打印所有通道
        for c,i in self.channels:
            LOGD(f'通道: {c.type_name()} {i}')

        # 打印所有断料检测器
        for bd in self.broken_detects:
            LOGD(f'断料检测器: {bd.type_name()}')

    def driver_control(self, printer_ch: int, action: ChannelAction):
        c,i = self.channels[printer_ch]
        c.control(i, action)

    def on_resumed(self):
        c,i = self.channels[self.fila_cur]
        # 非主动送料的通道，直接松开
        if not c.is_active_push(i):
            c.control(i, ChannelAction.STOP)

    def is_filament_broken(self) -> bool:
        """当所有断料检测器都没有料时，返回 True

        Returns:
            bool: _description_
        """
        for bd in self.broken_detects:
            if bd.is_filament_broken() is not True:
                return False
        return True
    
    def get_max_broken_safe_time(self) -> int:
        return max([bd.safe_time() for bd in self.broken_detects])

    def run_filament_change(self, next_filament: int):
        if self.fila_changing:
            return
        self.fila_changing = True
        self.thread = threading.Thread(
            target=self.filament_change, args=(next_filament,))
        self.thread.start()

    def filament_change(self, next_filament: int):
        # FIXME: 要增加通道不匹配的判断，比如接到换第4通道，结果我们只有3通道，可以呼叫用户确认，再继续

        self.change_count += 1
        LOGI(f'第 {self.change_count} 次换色')
        self.fila_next = next_filament
        LOGI(f'当前通道 {self.fila_cur + 1}，下个通道 {self.fila_next + 1}')

        if self.fila_cur == self.fila_next:
            self.printer_client.resume()
            LOGI("通道相同，无需换色, 恢复打印")
            self.fila_changing = False
            return

        LOGI("等待退料完成")
        self.driver_control(self.fila_cur, ChannelAction.PULL)   # 回抽当前通道
        self.printer_client.on_unload(self.change_tem)

        ts = datetime.now().timestamp()
        max_pull_time = ts + 120    # 最大退料时间，如果超出这个时间，则提醒用户

        # 等待所有断料检测器都没有料
        while not self.is_filament_broken():
            time.sleep(2)
            if datetime.now().timestamp() - ts > 30:   # 超时还没退到断料检测器
                LOGI("退料超时，抖一抖")
                self.driver_control(self.fila_cur, ChannelAction.PUSH)
                time.sleep(0.5)
                self.driver_control(self.fila_cur, ChannelAction.PULL)
                ts = datetime.now().timestamp()
            if max_pull_time < datetime.now().timestamp():
                LOGI("退不出来，摇人吧（需要手动把料撤回）")
                # TODO: 发出警报

        LOGI("退料检测到位")
        safe_time = self.get_max_broken_safe_time()
        if safe_time > 0:
            time.sleep(safe_time)   # 再退一点
            LOGI("退料到安全距离")

        self.driver_control(self.fila_cur, ChannelAction.STOP)   # 停止抽回

        # 强行让打印机材料状态变成无，避免万一竹子消息延迟或什么的，不要完全相信别人的接口，如果可以自己判断的话（使用自定义断料检测器有效）
        self.printer_client.set_filament_state(printer.FilamentState.NO)

        time.sleep(1)  # 休息下呗，万一板子反映不过来呢

        self.driver_control(self.fila_next, ChannelAction.PUSH)   # 输送下一个通道
        LOGI("开始输送下一个通道")

        # 到料目前还只能通过打印机判断，只能等了，不断刷新
        while self.printer_client.get_filament_state() != printer.FilamentState.YES:    # 等待打印机料线到达
            self.printer_client.refresh_status()    # 刷新打印机状态
            # TODO: 这里需要增加超时机制，如果一直送不到，需要呼叫用户确认处理
            time.sleep(2)

        self.fila_cur = self.fila_next
        LOGI("料线到达，换色完成")
        self.printer_client.resume()
        LOGI("恢复打印")

        self.on_resumed()

        self.fila_changing = False

    def on_printer_action(self, action: printer.Action, data):
        LOGD(f'收到打印机消息 {action} {data}')
        if action == printer.Action.CHANGE_FILAMENT:
            self.run_filament_change(data)

        if action == printer.Action.FILAMENT_SWITCH_0:
            pass

        if action == printer.Action.FILAMENT_SWITCH_1:
            pass

    def run(self):
        pass

    def stop(self):
        pass