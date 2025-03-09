# Python Service Manager

مدیریت سرویس‌های پایتون با رابط کاربری وب. این برنامه به شما امکان می‌دهد سرویس‌های systemd را برای اپلیکیشن‌های پایتونی خود مدیریت کنید.

## امکانات
- مدیریت سرویس‌های systemd با رابط کاربری وب
- احراز هویت برای امنیت بیشتر
- ترمینال تحت وب برای اجرای دستورات
- فایل منیجر برای مدیریت فایل‌ها
- آپلود فایل‌های پروژه
- پشتیبانی از فریمورک‌های مختلف (Python, FastAPI, Flask)
- امکان اجرای دستورات سفارشی
- مشاهده لاگ‌های سرویس

## نصب سریع

```bash
# نصب پیش‌نیازها
sudo apt update
sudo apt install python3-pip python3-venv git

# کلون پروژه
git clone https://github.com/MohammadHosein-Morsali/PythonServiceManger.git
cd PythonServiceManger

# ساخت محیط مجازی و نصب وابستگی‌ها
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# تنظیم دسترسی‌های sudo
sudo groupadd systemd-service
sudo usermod -a -G systemd-service $USER
sudo tee /etc/sudoers.d/service-manager << EOF
%systemd-service ALL=(ALL) NOPASSWD: /bin/systemctl
%systemd-service ALL=(ALL) NOPASSWD: /bin/journalctl
%systemd-service ALL=(ALL) NOPASSWD: /bin/chmod
%systemd-service ALL=(ALL) NOPASSWD: /bin/mv
EOF

# تنظیم پسورد (در فایل app.py)
# app.config['ADMIN_PASSWORD'] = 'your-password-here' را تغییر دهید

# راه‌اندازی به عنوان سرویس
sudo tee /etc/systemd/system/service-manager.service << EOF
[Unit]
Description=Python Service Manager
After=network.target

[Service]
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$(pwd)/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# فعال‌سازی و اجرای سرویس
sudo systemctl daemon-reload
sudo systemctl enable service-manager
sudo systemctl start service-manager
```

## نحوه استفاده

### ورود به سیستم
1. به آدرس `http://your-server-ip:5000` بروید
2. با پسورد تنظیم شده وارد شوید

### ایجاد سرویس جدید
1. روی "Add Service" کلیک کنید
2. اطلاعات سرویس را وارد کنید:
   - نام سرویس (مثال: `my-bot`)
   - توضیحات (اختیاری)
   - مسیر پوشه پروژه (با فایل منیجر انتخاب کنید)
   - فایل‌های پروژه را آپلود کنید:
     - فایل اصلی
     - فایل‌های اضافی (config و غیره)
   - نوع پروژه را انتخاب کنید:
     - Python: برای اسکریپت‌های ساده
     - FastAPI: برای سرویس‌های FastAPI
     - Flask: برای سرویس‌های Flask
     - Custom: برای دستور اجرای سفارشی

### مدیریت فایل‌ها
1. روی "File Manager" کلیک کنید
2. امکانات:
   - مرور پوشه‌ها و فایل‌ها
   - کپی کردن مسیر فایل‌ها
   - انتخاب پوشه برای پروژه جدید

### ترمینال
1. روی "Terminal" کلیک کنید
2. دستورات خود را وارد کنید
3. نتیجه اجرا را مشاهده کنید

### مثال‌های کاربردی

#### 1. بات تلگرام
```
Name: telegram-bot
Directory: /home/user/bots/telegram-bot
Main File: bot.py
Framework: Python
```

#### 2. سرویس FastAPI
```
Name: api-service
Directory: /home/user/services/api
Main File: main.py
Framework: FastAPI
```

#### 3. دستور سفارشی
```
Name: custom-bot
Directory: /home/user/bots/custom
Main File: run.py
Framework: Custom
Custom Command: python -m bot --config config.json
```

## عیب‌یابی

### خطای دسترسی
```bash
# بررسی عضویت در گروه
groups

# اجرای مجدد دستورات دسترسی
sudo usermod -a -G systemd-service $USER
sudo chmod 775 /etc/systemd/system
```

### خطای سرویس
```bash
# بررسی لاگ‌ها
sudo journalctl -u service-name -n 50

# بررسی وضعیت
sudo systemctl status service-name
```

### مشکل آپلود
1. بررسی دسترسی‌های پوشه آپلود
2. بررسی حجم فایل (حداکثر 16MB)
3. بررسی پسوند مجاز فایل

## نکات امنیتی
1. حتماً پسورد پیش‌فرض را تغییر دهید
2. فایروال را تنظیم کنید:
   ```bash
   sudo ufw allow 5000
   sudo ufw enable
   ```
3. از HTTPS استفاده کنید
4. دسترسی‌های sudo را محدود کنید

## به‌روزرسانی
```bash
cd PythonServiceManger
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart service-manager
```

## ساختار پروژه
```
PythonServiceManger/
├── app.py              # فایل اصلی برنامه
├── requirements.txt    # وابستگی‌ها
├── templates/          # قالب‌های HTML
│   ├── base.html
│   ├── index.html
│   ├── add_service.html
│   ├── login.html
│   ├── terminal.html
│   └── file_manager.html
└── instance/          # دیتابیس SQLite
    └── services.db
```

## مشارکت
1. پروژه را fork کنید
2. تغییرات خود را اعمال کنید
3. Pull Request ارسال کنید

## لایسنس
MIT 