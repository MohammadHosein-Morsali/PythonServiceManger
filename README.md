# Python Service Manager

مدیریت سرویس‌های پایتون با رابط کاربری وب. این برنامه به شما امکان می‌دهد سرویس‌های systemd را برای اپلیکیشن‌های پایتونی خود مدیریت کنید.

## امکانات
- ایجاد و مدیریت سرویس‌های systemd
- آپلود فایل‌های پروژه و مدیریت آن‌ها
- پشتیبانی از فریمورک‌های مختلف (FastAPI, Flask, Python)
- امکان اجرای دستورات سفارشی
- مدیریت محیط‌های مجازی و پکیج‌ها
- مشاهده لاگ‌های سرویس
- تنظیم متغیرهای محیطی
- مدیریت پورت و هاست

## پیش‌نیازها
- Python 3.x
- pip
- systemd
- دسترسی sudo

## نصب و راه‌اندازی

1. نصب پیش‌نیازها:
   ```bash
   sudo apt update
   sudo apt install python3-venv python3-pip
   ```

2. کلون و نصب پروژه:
   ```bash
   git clone <repository-url>
   cd service-manager
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. تنظیم دسترسی‌های sudo:
   ```bash
   sudo visudo
   ```
   این خط را اضافه کنید (به جای your-username نام کاربری خود را بنویسید):
   ```
   your-username ALL=(ALL) NOPASSWD: /usr/bin/systemctl, /usr/bin/journalctl
   ```

4. تنظیم مسیر آپلود در `app.py`:
   ```python
   app.config['UPLOAD_FOLDER'] = '/path/to/your/upload/directory'
   ```

5. اجرای برنامه:
   ```bash
   python app.py
   ```

## نصب به عنوان سرویس

1. ایجاد فایل سرویس:
   ```bash
   sudo nano /etc/systemd/system/service-manager.service
   ```

2. محتوای فایل سرویس:
   ```ini
   [Unit]
   Description=Python Service Manager
   After=network.target

   [Service]
   User=your-username
   WorkingDirectory=/path/to/service-manager
   Environment="PATH=/path/to/service-manager/venv/bin"
   ExecStart=/path/to/service-manager/venv/bin/python app.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. فعال‌سازی و اجرای سرویس:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable service-manager
   sudo systemctl start service-manager
   ```

## نحوه استفاده

### ایجاد سرویس جدید
1. به آدرس `http://your-server-ip:5000` بروید
2. روی "Add Service" کلیک کنید
3. اطلاعات سرویس را وارد کنید:
   - نام سرویس
   - توضیحات
   - نام پوشه پروژه
   - فایل‌های پروژه را آپلود کنید
   - فریمورک را انتخاب کنید
   - فایل اصلی یا دستور سفارشی را مشخص کنید
   - پورت و هاست را تنظیم کنید
   - پکیج‌های مورد نیاز را وارد کنید
   - متغیرهای محیطی را تنظیم کنید

### مدیریت سرویس‌ها
- **شروع/توقف**: از دکمه‌های Start/Stop استفاده کنید
- **ریستارت**: دکمه Restart را بزنید
- **مشاهده لاگ**: روی دکمه Logs کلیک کنید
- **ویرایش**: با دکمه Edit تنظیمات را تغییر دهید
- **حذف**: از دکمه Delete برای حذف سرویس استفاده کنید

### مدیریت فایل‌ها
1. روی "File Manager" کلیک کنید
2. می‌توانید:
   - پوشه جدید بسازید
   - فایل آپلود کنید
   - فایل‌ها را مدیریت کنید
   - در پوشه‌ها بگردید

## نکات امنیتی
1. حتماً فایروال را تنظیم کنید:
   ```bash
   sudo ufw allow 5000
   ```
2. برای محیط تولید:
   - از HTTPS استفاده کنید
   - احراز هویت اضافه کنید
   - از nginx به عنوان reverse proxy استفاده کنید

## عیب‌یابی
- اگر سرویس اجرا نشد، لاگ‌ها را بررسی کنید
- دسترسی‌های پوشه‌ها را چک کنید
- مطمئن شوید systemd فعال است
- دسترسی‌های sudo را بررسی کنید

## پشتیبانی از فریمورک‌ها

### FastAPI
```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
```

### Flask
```python
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"
```

### دستور سفارشی
می‌توانید هر دستوری را اجرا کنید:
```bash
python -m bot --config config.json
python script.py --arg1 value1
``` 