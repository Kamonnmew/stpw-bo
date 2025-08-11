#!/bin/bash

# เข้าสู่ directory ที่ถูกต้อง
cd /home/site/wwwroot

# อัปเดต pip
python -m pip install --upgrade pip

# ติดตั้ง dependencies
echo "Installing dependencies from requirements.txt..."
python -m pip install --no-cache-dir -r requirements.txt

# แสดง packages ที่ติดตั้งแล้ว (debug)
echo "Installed packages:"
pip list

# เริ่มแอปพลิเคชัน
echo "Starting application..."
gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 1 --access-logfile '-' --error-logfile '-' app:app
