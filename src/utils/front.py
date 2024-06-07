import requests
import zipfile
import os

def unzip_file(zip_path, extract_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    print(f"文件已解压到 {extract_path}")


if os.path.exists('web'):
    exit('前端已存在，如果要更新，请删除 web 文件夹后重新运行本脚本')

print('正在下载前端资源...')

# GitHub 用户名和仓库名
owner = "TshineZheng"
repo = "FilamentorApp"

# GitHub API URL
url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"

# 获取最新的 release 信息
response = requests.get(url)
release_data = response.json()

# 获取最新的 release 的资产（文件）
assets = release_data['assets']
for asset in assets:
    download_url = asset['browser_download_url']
    print(f"下载 URL: {download_url}")
    # 下载文件
    file_response = requests.get(download_url)
    file_name = asset['name']
    with open(file_name, 'wb') as f:
        f.write(file_response.content)
    print(f"文件 {file_name} 已下载")


unzip_file('web.zip', 'web/')

os.remove('web.zip')


