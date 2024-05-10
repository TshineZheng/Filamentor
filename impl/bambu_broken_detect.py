from broken_detect import BrokenDetect

    
class BambuBrokenDetect(BrokenDetect):
    import impl.bambu_client as bambu

    def type_name() -> str:
        return "bambu_broken_detect"

    def __init__(self, bambu_client: bambu.BambuClient):
        super().__init__()
        self.bambu_client = bambu_client

    def to_dict(self) -> dict:
        return super().to_dict()

    def is_filament_broken(self) -> bool:
        from printer_client import FilamentState
        self.bambu_client.refresh_status()
        return self.bambu_client.get_filament_state() == FilamentState.NO

    def safe_time(self) -> float:
        return 1.5

    def start(self):
        return super().start()

    def stop(self):
        return super().stop()