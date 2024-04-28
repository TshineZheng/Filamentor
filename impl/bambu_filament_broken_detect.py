from filament_broken_detect import FilamentBrokenDetect
from impl.bambu_client import BambuClient
import printer_client as printer


class BambuFilamentBrokenDetect(FilamentBrokenDetect):

    def __init__(self, bambu_client:BambuClient):
        self.bambu_client = bambu_client

    def is_filament_broken(self) -> bool:
        self.bambu_client.refresh_status()
        return self.bambu_client.get_filament_state() == printer.FilamentState.NO
    
    def safeTime(self) -> float:
        return 1.5
    
    def start(self):
        return super().start()
    
    def stop(self):
        return super().stop()