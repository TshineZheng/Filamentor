import threading
import time
from datetime import datetime
from typing import Callable, List

import printer_client as printer
from controller import ChannelAction, Controller
from utils.log import TAGLOG
import utils.persist as persist
from app_config import config

LOAD_TIMEOUT = 30   # 装料超时，超时会尝试抖动耗材
LOAD_WARNING = 120  # 装料失败警告时间
UNLOAD_TIMEOUT = 30 # 退料超时，超时会尝试抖动耗材
UNLOAD_WARNING = 120 # 退料失败警告时间

PRINTER_UNLOAD_TIMEOUT = 5

class AMSCore(TAGLOG):
    def __init__(
        self,
        use_printer: str
    ) -> None:
        self.use_printer = use_printer
        self.fila_cur = persist.get_printer_channel(use_printer)
        self.fila_next = 0
        self.change_count = 0
        self.fila_changing = False
        self.task_name = None
        self.task_log_id = None
        self.printer_fila_state = printer.FilamentState.UNKNOWN

        self.printer_client = config.get_printer(use_printer)
        self.change_tem = config.get_printer_change_tem(use_printer)
        self.broken_detects = config.get_printer_broken_detect(use_printer)

        if self.broken_detects is None or len(self.broken_detects) == 0:
            self.broken_detects = [self.printer_client.filament_broken_detect()]   # 如果没有自定义断线检测，使用打印默认的
            self.LOGI('没有配置断料检测器，使用打印机自己的断料检测器')

        self.channels: List[tuple[Controller, int]] = []    # 控制器对象, 通道在控制器上的序号
        for c in config.get_printer_channel_settings(use_printer):
            self.channels.append([config.get_controller(c.controller_id), c.channel])

        self.LOGI(f'通道数量: {len(self.channels)}, 断料检测器数量: {len(self.broken_detects)}, 换色温度: {self.change_tem}, 当前通道: {self.fila_cur+1}')
        for c,i in self.channels:
            self.LOGD(f'通道: {c.type_name()} {i}')
        for bd in self.broken_detects:
            self.LOGD(f'断料检测器: {bd.type_name()}')

    def tag(self):
        return self.use_printer

    def driver_control(self, printer_ch: int, action: ChannelAction):
        c,i = self.channels[printer_ch]
        c.control(i, action)
        self.LOGD(f'{action} {printer_ch} ({c.type_name()} {i})')

    def on_resumed(self):
        c,i = self.channels[self.fila_cur]
        # 非主动送料的通道，直接松开
        if not c.is_initiative_push(i):
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

    def fila_shake(self, channel:int, action: ChannelAction, shake_time=1):
        self.driver_control(channel, ChannelAction.PULL if action == ChannelAction.PUSH else ChannelAction.PUSH)
        time.sleep(shake_time)
        self.driver_control(channel, ChannelAction.PUSH if action == ChannelAction.PUSH else ChannelAction.PULL)

    def on_printer_action(self, action: printer.Action, data):
        self.LOGD(f'收到打印机 {self.use_printer} 消息 {action} {"" if data is None else data}')
        if action == printer.Action.CHANGE_FILAMENT:
            self.run_filament_change(data)

        if action == printer.Action.FILAMENT_SWITCH:
            self.printer_fila_state = data

        if action == printer.Action.TASK_START:
            self.__on_task_started(data['subtask_name'], data['first_filament'])
        
        if action == printer.Action.TASK_FINISH:
            self.__on_task_stopped(data, action)
            
        if action == printer.Action.TASK_FAILED:
            self.__on_task_stopped(data, action)

    def __on_task_started(self, task_name: str, first_filament: int):
        self.task_name = task_name
        self.change_count = 0   # 重置换色次数
        self.start_task_log()   # 开始记录打印日志

        self.LOGI(f"接到打印任务: {self.task_name}, 第一个通道: {first_filament + 1}")
        if first_filament < 0 or first_filament >= len(self.channels):
            self.LOGE(f'开始通道{first_filament}不正常')

        # TODO: 如果打印机没有料，就不要送料了，且提示用户进那个料

        # 如果通道是主动送料，则启动时，开始送料
        c,i = self.channels[self.fila_cur]
        if c.is_initiative_push(i):
            self.driver_control(self.fila_cur, ChannelAction.PUSH)
        
        if first_filament != self.fila_cur:
            self.LOGI("打印的第一个通道不是AMS当前通道, 需要换色")
            # threading.Thread(
            #     target=self.printer_client.change_filament, 
            #     args=(self, first_filament, self.change_tem)).start()

    def __on_task_stopped(self, task_name: str, action: printer.Action):
        if self.task_name == task_name:
            self.LOGI(f"{self.task_name} {'打印完成' if action == printer.Action.TASK_FINISH else '打印失败'}")
            self.task_name = None
            self.stop_task_log()
            c,i = self.channels[self.fila_cur]
            c.control(i, ChannelAction.STOP)

    def start_task_log(self):
        from loguru import logger as LOG
        import consts

        self.task_log_id = LOG.add(
            sink = f'{consts.STORAGE_PATH}/logs/task/{self.task_name}_{datetime.now().strftime("%Y%m%d-%H%M%S")}.log',
            enqueue=True,
            rotation='1 days',
            retention='1 weeks',
            encoding='utf-8',
            backtrace=True,
            diagnose=True,
            compression='zip'
        )
    
    def stop_task_log(self):
        if self.task_log_id is not None:
            from loguru import logger as LOG
            LOG.remove(self.task_log_id)
            self.task_log_id = None

    def start(self):
        #TODO: 判断打印机是否有料，如果有料则仅送料，否则需要送料并调用打印机加载材料
        #TODO: 如果可以，最好能自主判断当前打印机的料是哪个通道

        self.printer_client.add_on_action(self.on_printer_action)
        self.printer_client.refresh_status()
        self.LOGI('AMS 启动')

    def stop(self):
        self.printer_client.remove_on_action(self.on_printer_action)

    def run_filament_change(self, next_filament: int, before_done: Callable = None):
        if self.fila_changing:
            return
        self.fila_changing = True
        self.thread = threading.Thread(
            target=self.filament_change, args=(next_filament,before_done,))
        self.thread.start()

    def update_cur_fila(self, fila:int):
        self.fila_cur = fila
        persist.update_printer_channel(self.use_printer, self.fila_cur)
        
    def filament_change(self, next_filament: int, before_done: Callable = None):
        # FIXME: 要增加通道不匹配的判断，比如接到换第4通道，结果我们只有3通道，可以呼叫用户确认，再继续

        self.change_count += 1
        self.fila_next = next_filament

        self.LOGI(f'第 {self.change_count} 次换色, 当前通道 {self.fila_cur + 1}，下个通道 {self.fila_next + 1}')

        if self.fila_cur == self.fila_next:
            self.printer_client.resume()
            self.LOGI("通道相同，无需换色, 恢复打印")
            self.fila_changing = False
            return
        
        self.driver_control(self.fila_cur, ChannelAction.STOP)   # 停止当前通道

        self.LOGI(f"等待通道 {self.fila_cur + 1} 退料完成")
        self.printer_client.on_unload(self.change_tem)

        self.LOGI(f'通道 {self.fila_cur} 开始回抽')
        self.driver_control(self.fila_cur, ChannelAction.PULL)   # 回抽当前通道

        # 等待打印机小绿点消失，如果超过一定时间，估计是卡五通了
        ts = datetime.now().timestamp()
        while self.printer_fila_state != printer.FilamentState.YES: 
            if datetime.now().timestamp() - ts > PRINTER_UNLOAD_TIMEOUT:
                self.LOGI(f"打印机退料卡头了？都{PRINTER_UNLOAD_TIMEOUT}秒了，小绿点还没消失，抖一下")
                self.fila_shake(self.fila_next, ChannelAction.PULL)
                ts = datetime.now().timestamp()

        self.LOGI("打印机退料完成")

        ts = datetime.now().timestamp()
        max_pull_time = ts + UNLOAD_WARNING    # 最大退料时间，如果超出这个时间，则提醒用户
        # 等待所有断料检测器都没有料
        while not self.is_filament_broken():
            time.sleep(2)
            if datetime.now().timestamp() - ts > UNLOAD_TIMEOUT:
                self.LOGI("退料超时，抖一抖")
                self.fila_shake(self.fila_cur, ChannelAction.PULL) 
                ts = datetime.now().timestamp()

            if max_pull_time < datetime.now().timestamp():
                self.LOGI("退不出来，摇人吧（需要手动把料撤回）")
                # TODO: 发出警报

        self.LOGI("退料检测到位")
        safe_time = self.get_max_broken_safe_time()
        if safe_time > 0:
            time.sleep(safe_time)   # 再退一点
            self.LOGI("退料到安全距离")

        self.driver_control(self.fila_cur, ChannelAction.STOP)   # 停止抽回

        # 强行让打印机材料状态变成无，避免万一竹子消息延迟或什么的，不要完全相信别人的接口，如果可以自己判断的话（使用自定义断料检测器有效）
        self.printer_fila_state = printer.FilamentState.NO

        time.sleep(1)  # 休息下呗，万一板子反映不过来呢

        self.driver_control(self.fila_next, ChannelAction.PUSH)   # 输送下一个通道
        self.LOGI(f"开始输送下一个通道 {self.fila_next + 1}")

        ts = datetime.now().timestamp()
        max_push_time = ts + LOAD_WARNING    # 最大送料时间，如果超出这个时间，则提醒用户

        # 到料目前还只能通过打印机判断，只能等了，不断刷新
        while self.printer_fila_state != printer.FilamentState.YES:    # 等待打印机料线到达
            if datetime.now().timestamp() - ts > LOAD_TIMEOUT:
                self.LOGI("送料超时，抖一抖")
                self.fila_shake(self.fila_next, ChannelAction.PUSH)
                ts = datetime.now().timestamp()

            if max_push_time < datetime.now().timestamp():
                self.LOGI("送不进去，摇人吧（需要手动把料送进去）")
                # TODO: 发出警报

            self.printer_client.refresh_status()    # 刷新打印机状态
            time.sleep(2)

        self.update_cur_fila(self.fila_next)
        self.LOGI("料线到达，换色完成")

        if before_done : before_done()

        self.printer_client.resume()
        self.LOGI("恢复打印")

        self.on_resumed()

        self.fila_changing = False

ams_list:list[AMSCore] = []