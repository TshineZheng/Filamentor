
class GCodeInfo(object):
    def __init__(self):
        from src import consts
        self.first_channel = 0
        self.layer_height = consts.LAYER_HEIGHT


def decodeFromZipUrl(zip_url: str, file_path: str) -> GCodeInfo:
    import requests
    import zipfile
    import io

    # 发送GET请求并获取ZIP文件的内容
    response = requests.get(zip_url)

    # 确保请求成功
    if response.status_code == 200:
        ret = GCodeInfo()
        # 使用BytesIO读取下载的内容
        zip_data = io.BytesIO(response.content)
        # 使用zipfile读取ZIP文件
        with zipfile.ZipFile(zip_data) as zip_file:
            # 获取ZIP文件中的所有文件名列表
            file_names = zip_file.namelist()
            # 遍历文件名列表
            for file_name in file_names:
                # 如果文件名符合您要查找的路径
                if file_path == file_name:
                    # 打开文本文件
                    with zip_file.open(file_name) as file:
                        # 逐行读取文件内容
                        for line in file:
                            # 将bytes转换为str
                            line_str = line.decode('utf-8')
                            # 检查是否包含特定字符串
                            if line_str.startswith('M620 S'):
                                # 找到匹配的行，返回内容
                                text = line_str.strip()
                                import re
                                # 正则表达式模式，用于匹配'M620 S'后面的数字，直到遇到非数字字符
                                pattern = r'M620 S(\d+)'
                                # 搜索匹配的内容
                                match = re.search(pattern, text)
                                # 如果找到匹配项，则提取数字
                                if match:
                                    number = match.group(1)
                                    print(number)  # 输出匹配到的数字
                                    ret.first_channel = int(int(number))
                                    return ret
                            elif line_str.startswith('; layer_height = '):
                                value = line_str.split('=')[1].strip()
                                ret.layer_height = float(value)

    return None
