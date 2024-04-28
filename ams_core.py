import threading
import time

import printer_client as printer
from config.mqtt_config import MQTTConfig
from filament_broken_detect import FilamentBrokenDetect
from filament_driver import DriverAction
from impl.bambu_client import BambuClient, BambuClientConfig
from impl.bambu_filament_broken_detect import BambuFilamentBrokenDetect
from impl.yba_driver import YBAAMS, YBADriver


class AmsCore(object):
    def __init__(
                self, 
                OPENAMS_MQTT_CONFIG = MQTTConfig('MQTT 服务器', 1883, 'filamentor', '', '')
        ) -> None:
        config = BambuClientConfig(
            printer_ip="打印机ip",
            lan_password="打印机局域网密码",
            device_serial="打印机序列号"
        )
        self.printer_client:printer.PrinterClient = BambuClient(
            config=config,
            on_action=self.on_printer_action
        )

        self.fbd:FilamentBrokenDetect = BambuFilamentBrokenDetect(self.printer_client)    # 断料检测

        self.ybaams = YBAAMS('YBAAMS板子地址', 3333)    # YBA AMS 控制器

        self.drivers =[
            YBADriver(self.ybaams, 0),  # 通道 0
            YBADriver(self.ybaams, 1),  # 通道 1
            YBADriver(self.ybaams, 2),  # 通道 2
            # 通道 N
        ]

        self.filament_current = 0
        self.filament_next = 0
        self.change_count = 0
        self.change_tem = 255
        self.filament_changing = False

    def run(self):
        self.printer_client.start()
        self.fbd.start()
        self.ybaams.start()

    def stop(self):
        self.printer_client.stop()
        self.fbd.stop()
        self.ybaams.stop()

    def driver_control(self, channel, action:DriverAction):
        self.drivers[channel].control(action)

    def run_filament_change(self, next_filament: int):
        if self.filament_changing:
            return
        self.filament_changing = True
        self.thread = threading.Thread(target=self.filament_change, args=(next_filament,))
        self.thread.start()

    def filament_change(self, next_filament: int):
        # FIXME: 要增加通道不匹配的判断，比如接到换第4通道，结果我们只有3通道，可以呼叫用户确认，再继续
        
        self.change_count +=1
        print(f'开始第 {self.change_count} 次换色')
        self.filament_next = next_filament
        print(f'当前通道 {self.filament_current + 1}，下个通道 {self.filament_next + 1}')

        if self.filament_current == self.filament_next:
            print('无需换色')
            self.printer_client.resume()
            print("恢复打印")
        else:
            print("等待退料完成")
            self.driver_control(self.filament_current, DriverAction.PULL)   # 回抽当前通道
            self.printer_client.on_unload(self.change_tem)

            # while self.printer_client.get_filament_state() != printer.FilamentState.NO:
            #     self.printer_client.refresh_status()    # 刷新打印机状态

            #     # TODO: 这里需要增加超时机制，如果一直退不了，则需要停止通道回抽，并呼叫用户q确认处理
            #     time.sleep(2)
            # print("打印机退料完成")

            while not self.fbd.is_filament_broken():    # 通过断料检测器，判断是否断料
                time.sleep(2)
            print("退料检测到位")

            if self.fbd.safeTime() > 0:
                time.sleep(self.fbd.safeTime())   # 再退一点
                print("退料到安全距离")
            
            self.driver_control(self.filament_current, DriverAction.STOP)   # 停止抽回

            self.printer_client.set_filament_state(printer.FilamentState.NO)    # 强行让打印材料状态变成无，避免万一竹子消息延迟或什么的，不要完全相信别人的接口，如果可以自己判断的话（使用自定义断料检测器有效）

            time.sleep(1) # 休息下呗，万一板子反映不过来呢

            self.driver_control(self.filament_next, DriverAction.PUSH)   # 输送下一个通道
            print("开始输送下一个通道")

            while self.printer_client.get_filament_state() != printer.FilamentState.YES:    # 等待打印机料线到达
                self.printer_client.refresh_status()    # 刷新打印机状态
                # TODO: 这里需要增加超时机制，如果一直送不到，需要呼叫用户确认处理
                time.sleep(2)

            print("料线到达")
            self.filament_current = self.filament_next
            print("换色完成")
            self.printer_client.resume()
            print("恢复打印")

        self.filament_changing = False

    def on_printer_action(self, action:printer.Action, data):
        if action == printer.Action.CHANGE_FILAMENT:
            self.run_filament_change(data)

        if action == printer.Action.FILAMENT_SWITCH_0:
            pass

        if action == printer.Action.FILAMENT_SWITCH_1:
            pass


if __name__ == "__main__":
    ams = AmsCore()
    ams.run()

    ams.filament_current = 0

    ams.driver_control(ams.filament_current, DriverAction.PUSH)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ams.stop()

