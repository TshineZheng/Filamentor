import os


PERSIST_PATH = 'persist'

def setup():
    import os
    if not os.path.exists(PERSIST_PATH):
        os.mkdir(PERSIST_PATH)

def update_printer_channel(printer_id: str, channel: int):
    with open(f'{PERSIST_PATH}/{printer_id}.channel', 'w') as f:
        f.write(str(channel))

def get_printer_channel(printer_id: str) -> int:
    # 如果文件不存在，则返回 0
    if not os.path.exists(f'{PERSIST_PATH}/{printer_id}.channel'):
        return 0
    
    try:
        with open(f'{PERSIST_PATH}/{printer_id}.channel', 'r') as f:
            return int(f.read())
    except:
        return 0