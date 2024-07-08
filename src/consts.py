STORAGE_PATH = 'data/'  # 数据存储目录

FIX_Z_GCODE = None
FIX_Z_TEMP = None
FIX_Z_PAUSE_COUNT = None
PAUSE_Z_OFFSET = 3.0
DO_HOME_Z_HEIGHT = 10.0
LAYER_HEIGHT = 0.2


def setup():
    import os
    if not os.path.exists(STORAGE_PATH):
        os.mkdir(STORAGE_PATH)
    global FIX_Z_TEMP
    global FIX_Z_PAUSE_COUNT
    global PAUSE_Z_OFFSET
    global DO_HOME_Z_HEIGHT
    global LAYER_HEIGHT

    FIX_Z_TEMP = int(os.getenv("FIX_Z_TEMP", '0'))
    FIX_Z_PAUSE_COUNT = int(os.getenv("FIX_Z_PAUSE_COUNT", '0'))
    PAUSE_Z_OFFSET = float(os.getenv("PAUSE_Z_OFFSET", '3'))
    DO_HOME_Z_HEIGHT = float(os.getenv("DO_HOME_Z_HEIGHT", '10'))
    LAYER_HEIGHT = float(os.getenv("LAYER_HEIGHT", '0.2'))

    fix_z_gcode_path = os.getenv("FIX_Z_GCODE")

    if fix_z_gcode_path:
        print(f'修复 Z 轴抬高 gcode 文件路径为：{fix_z_gcode_path}')
        try:
            with open(fix_z_gcode_path, 'r') as f:
                global FIX_Z_GCODE
                FIX_Z_GCODE = f.read().replace('\n', '\\n')
                print('修复 Z 轴抬高 gcode 读取成功')
        except Exception as e:
            print(f'修复 Z 轴抬高文件读取失败：{fix_z_gcode_path}')
            print(e)
    else:
        print('未设置修复 Z 轴抬高 gcode 文件路径，忽略')
