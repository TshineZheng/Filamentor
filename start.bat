@echo off
REM 检查是否存在requirements.txt文件
if exist "requirements.txt" (
    echo 发现requirements.txt, 正在安装依赖...
    REM 使用pip安装依赖
    pip install -r requirements.txt
) else (
    echo 未发现requirements.txt, 跳过依赖安装。
)

REM 在后台运行main.py并且不显示输出
python main.py