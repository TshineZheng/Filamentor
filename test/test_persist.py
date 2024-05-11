
import os
import consts 


def setup_module():
    consts.setup()

def teardown_module():
    # 删除 test_channel.txt
    import os
    os.remove(f'{consts.STORAGE_PATH}pytest.channel')

def test_update_printer_channel():
    import utils.persist as persist
    persist.update_printer_channel('pytest', 3)
    
    with open(f'{consts.STORAGE_PATH}pytest.channel', 'r') as f:
        assert f.read() == '3'

def test_get_printer_channel():
    import utils.persist as persist

    # 文件不存在
    if os.path.exists(f'{consts.STORAGE_PATH}pytest.channel'):
        os.remove(f'{consts.STORAGE_PATH}pytest.channel')
    assert persist.get_printer_channel('pytest') == 0

    # 写个错误的内容
    with open(f'{consts.STORAGE_PATH}pytest.channel', 'w') as f:
        f.write('a')
    assert persist.get_printer_channel('pytest') == 0

    # 数值测试
    with open(f'{consts.STORAGE_PATH}pytest.channel', 'w') as f:
        f.write('11')
    assert persist.get_printer_channel('pytest') == 11

    with open(f'{consts.STORAGE_PATH}pytest.channel', 'w') as f:
        f.write('2')
    assert persist.get_printer_channel('pytest') == 2

