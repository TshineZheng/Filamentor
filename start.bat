@echo off

if exist "requirements.txt" (
    pip install -r requirements.txt
)

python src/utils/front.py

uvicorn src.main:app --port 7170 --host 0.0.0.0 --log-level warning

