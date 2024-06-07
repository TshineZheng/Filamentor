STORAGE_PATH = 'data/'  # 数据存储目录


def setup():
    import os
    if not os.path.exists(STORAGE_PATH):
        os.mkdir(STORAGE_PATH)
