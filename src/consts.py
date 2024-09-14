STORAGE_PATH = 'data/'  # 数据存储目录

FIX_Z = False
FIX_Z_GCODE = None
# FIX_Z_TEMP = None
FIX_Z_PAUSE_COUNT = None
PAUSE_Z_OFFSET = 3.0
DO_HOME_Z_HEIGHT = 10.0
LAYER_HEIGHT = 0.2


def setup():
    import os
    if not os.path.exists(STORAGE_PATH):
        os.mkdir(STORAGE_PATH)
    global FIX_Z
    global FIX_Z_GCODE
    # global FIX_Z_TEMP
    global FIX_Z_PAUSE_COUNT
    global PAUSE_Z_OFFSET
    global DO_HOME_Z_HEIGHT
    global LAYER_HEIGHT

    FIX_Z = True if os.getenv("FIX_Z", '0') == '1' else False
    # FIX_Z_TEMP = int(os.getenv("FIX_Z_TEMP", '0'))
    FIX_Z_PAUSE_COUNT = int(os.getenv("FIX_Z_PAUSE_COUNT", '0'))
    PAUSE_Z_OFFSET = float(os.getenv("PAUSE_Z_OFFSET", '3'))
    DO_HOME_Z_HEIGHT = float(os.getenv("DO_HOME_Z_HEIGHT", '170.0'))
    LAYER_HEIGHT = float(os.getenv("LAYER_HEIGHT", '0.2'))

    fix_z_gcode_path = os.getenv("FIX_Z_GCODE")

    if FIX_Z and fix_z_gcode_path:
        from src.utils.log import LOGI, LOGE
        # LOGI(f'FIX_Z_TEMP: {FIX_Z_TEMP}')
        LOGI(f'FIX_Z_PAUSE_COUNT: {FIX_Z_PAUSE_COUNT}')
        LOGI(f'PAUSE_Z_OFFSET: {PAUSE_Z_OFFSET}')
        LOGI(f'DO_HOME_Z_HEIGHT: {DO_HOME_Z_HEIGHT}')
        LOGI(f'LAYER_HEIGHT: {LAYER_HEIGHT}')
        LOGI(f'Z 轴抬高 gcode 文件路径为：{fix_z_gcode_path}')
        try:
            with open(fix_z_gcode_path, 'r') as f:
                FIX_Z_GCODE = f.read().replace('\n', '\\n')
                LOGI('修复 Z 轴抬高 gcode 读取成功')
        except Exception as e:
            LOGE(f'修复 Z 轴抬高文件读取失败：{fix_z_gcode_path}')
            LOGE(e)
