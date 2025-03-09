# راهنمای جامع Python Service Manager

## فهرست مطالب
1. [مقدمه](#مقدمه)
2. [نصب](#نصب)
3. [پیکربندی](#پیکربندی)
4. [مدیریت سرویس‌ها](#مدیریت-سرویس‌ها)
5. [مدیریت فایل‌ها](#مدیریت-فایل‌ها)
6. [ترمینال تحت وب](#ترمینال-تحت-وب)
7. [نکات امنیتی](#نکات-امنیتی)
8. [عیب‌یابی](#عیب‌یابی)

## مقدمه
Python Service Manager یک ابزار مدیریتی تحت وب برای کنترل سرویس‌های پایتون در لینوکس است. این برنامه به شما امکان می‌دهد تا سرویس‌های مختلف پایتونی خود را از طریق یک رابط کاربری ساده مدیریت کنید.

### ویژگی‌های اصلی
- مدیریت متمرکز سرویس‌ها
- رابط کاربری تحت وب
- پشتیبانی از فریم‌ورک‌های مختلف
- امنیت بالا
- نصب و پیکربندی خودکار

## نصب

### پیش‌نیازها
- سیستم‌عامل لینوکس (Ubuntu/Debian)
- Python 3.8 یا بالاتر
- دسترسی sudo
- اتصال به اینترنت

### روش نصب خودکار
1. دانلود اسکریپت نصب:
```bash
wget https://raw.githubusercontent.com/MohammadHosein-Morsali/PythonServiceManger/main/install.sh
```

2. اعطای دسترسی اجرا:
```bash
chmod +x install.sh
```

3. اجرای اسکریپت:
```bash
sudo ./install.sh
```

4. وارد کردن اطلاعات درخواستی:
   - نام کاربری سیستم
   - پسورد پنل مدیریت
   - پورت (پیش‌فرض: 5000)

### بررسی نصب
پس از نصب، می‌توانید با دستورات زیر وضعیت سرویس را بررسی کنید:
```bash
systemctl status service-manager
journalctl -u service-manager -f
```

## پیکربندی

### تنظیمات امنیتی
1. تغییر پسورد پیش‌فرض:
   - ویرایش فایل `config.json`
   - تغییر مقدار `password`
   - راه‌اندازی مجدد سرویس

2. تنظیم فایروال:
```bash
sudo ufw allow 5000/tcp
sudo ufw enable
```

### تنظیمات پیشرفته
1. تغییر مسیر ذخیره‌سازی:
   - ویرایش `app.config['UPLOAD_FOLDER']` در `app.py`
   - ایجاد پوشه جدید با دسترسی مناسب

2. تنظیم محدودیت حجم فایل:
   - تغییر `MAX_CONTENT_LENGTH` در `app.py`

## مدیریت سرویس‌ها

### ایجاد سرویس جدید
1. کلیک روی "Add Service"
2. وارد کردن اطلاعات:
   - نام سرویس (منحصر به فرد)
   - توضیحات
   - مسیر پوشه
   - فریم‌ورک
   - فایل اصلی
   - فایل‌های اضافی

### مدیریت سرویس موجود
- شروع: دکمه "Start"
- توقف: دکمه "Stop"
- راه‌اندازی مجدد: دکمه "Restart"
- مشاهده لاگ: دکمه "Logs"
- ویرایش: دکمه "Edit"
- حذف: دکمه "Delete"

### نمونه پیکربندی‌ها

#### بات تلگرام
```python
# config.json
{
    "token": "YOUR_BOT_TOKEN",
    "admin_id": 123456789
}

# bot.py
import telebot
import json

with open('config.json') as f:
    config = json.load(f)

bot = telebot.TeleBot(config['token'])
# ... rest of the code
```

#### سرویس FastAPI
```python
# main.py
from fastapi import FastAPI
from uvicorn import run

app = FastAPI()

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)
```

## مدیریت فایل‌ها

### آپلود فایل
1. انتخاب پوشه مقصد
2. کشیدن فایل یا کلیک روی "Upload"
3. انتخاب فایل(ها)
4. تأیید آپلود

### مدیریت دسترسی‌ها
```bash
# تغییر مالک فایل
sudo chown $USER:$USER /path/to/file

# تنظیم دسترسی
chmod 644 /path/to/file
```

## ترمینال تحت وب

### دستورات پرکاربرد
```bash
# مشاهده سرویس‌های فعال
systemctl list-units --type=service

# بررسی پورت‌های باز
netstat -tulpn

# مشاهده لاگ‌ها
tail -f /var/log/syslog
```

### نکات امنیتی ترمینال
- محدود کردن دستورات مجاز
- عدم اجرای دستورات خطرناک
- ثبت تمام دستورات

## نکات امنیتی

### بهترین شیوه‌ها
1. استفاده از HTTPS:
   - نصب Let's Encrypt
   - پیکربندی Nginx/Apache
   - تنظیم ریدایرکت

2. محدودسازی دسترسی:
   - تنظیم فایروال
   - محدود کردن IP‌های مجاز
   - استفاده از Basic Auth

3. به‌روزرسانی منظم:
   - سیستم‌عامل
   - پایتون و وابستگی‌ها
   - خود برنامه

### پشتیبان‌گیری
```bash
# پشتیبان از دیتابیس
cp instance/services.db backup/

# پشتیبان از تنظیمات
cp config.json backup/
```

## عیب‌یابی

### مشکلات رایج

#### خطای دسترسی
1. بررسی گروه:
```bash
groups
sudo usermod -a -G systemd-service $USER
```

2. بررسی دسترسی‌های فایل:
```bash
ls -la /opt/PythonServiceManger
sudo chown -R $USER:$USER /opt/PythonServiceManger
```

#### خطای سرویس
1. بررسی وضعیت:
```bash
systemctl status service-manager
```

2. بررسی لاگ‌ها:
```bash
journalctl -u service-manager -n 100
```

#### مشکل پورت
1. بررسی پورت:
```bash
netstat -tulpn | grep 5000
```

2. تغییر پورت:
   - ویرایش فایل کانفیگ
   - راه‌اندازی مجدد سرویس

### گزارش مشکل
1. جمع‌آوری اطلاعات:
   - نسخه سیستم‌عامل
   - نسخه پایتون
   - لاگ‌های خطا
   - مراحل تکرار مشکل

2. ارسال گزارش:
   - ایجاد Issue در GitHub
   - ارائه اطلاعات کامل
   - پیگیری پاسخ‌ها 