# 检查是否存在requirements.txt文件
if [ -f "requirements.txt" ]; then
    echo "发现requirements.txt, 正在安装依赖..."
    # 使用pip安装依赖
    pip install -r requirements.txt
else
    echo "未发现requirements.txt, 跳过依赖安装。"
fi

nohup python3 main.py > /dev/null 2>&1 &

echo "启动成功"