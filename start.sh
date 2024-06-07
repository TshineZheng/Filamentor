if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

python3 src/utils/front.py

nohup uvicorn src.main:app --port 7170 --host 0.0.0.0 --log-level warning > /dev/null 2>&1 &

echo "启动成功"