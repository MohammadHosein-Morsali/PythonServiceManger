# Python Service Manager (PSM)

مدیریت سرویس‌های پایتون با رابط کاربری وب. این برنامه به شما امکان می‌دهد سرویس‌های systemd را برای اپلیکیشن‌های پایتونی خود مدیریت کنید.

![داشبورد](screenshots/dashboard.png)

[English Version](README_EN.md)

## مدیریت سرویس‌های لینوکس
پنل مدیریت سرویس‌های لینوکس با قابلیت‌های پیشرفته

### امکانات
- مدیریت سرویس‌های systemd از طریق وب
- احراز هویت برای امنیت بیشتر
- ترمینال تحت وب با پشتیبانی از WebSocket برای اجرای دستورات در لحظه
- مدیریت فایل‌ها و آپلود پروژه با دسترسی sudo
- پشتیبانی از فریم‌ورک‌های مختلف (Python, FastAPI, Flask)
- اجرای دستورات سفارشی با دسترسی sudo
- مشاهده لاگ سرویس‌ها
- به‌روزرسانی و حذف خودکار
- رابط کاربری دوزبانه (فارسی و انگلیسی)

### نصب خودکار (توصیه شده)
برای نصب سریع و خودکار:
```bash
wget https://raw.githubusercontent.com/MohammadHosein-Morsali/PythonServiceManger/main/install.sh
chmod +x install.sh
sudo ./install.sh
```

![نصب](screenshots/install.png)

اسکریپت نصب از شما موارد زیر را می‌پرسد:
1. نام کاربری سیستم
2. پسورد دلخواه برای پنل مدیریت
3. پورت دلخواه (پیش‌فرض: 5000)

اسکریپت به صورت خودکار:
- پیش‌نیازها را نصب می‌کند
- پروژه را در `/opt/PythonServiceManger` نصب می‌کند
- محیط مجازی Python را می‌سازد
- دسترسی‌های لازم را تنظیم می‌کند
- سرویس systemd را ایجاد و فعال می‌کند
- فایروال را تنظیم می‌کند

### به‌روزرسانی خودکار
برای به‌روزرسانی به نسخه جدید:
```bash
wget https://raw.githubusercontent.com/MohammadHosein-Morsali/PythonServiceManger/main/update.sh
chmod +x update.sh
sudo ./update.sh
```

![به‌روزرسانی](screenshots/update.png)

اسکریپت به‌روزرسانی:
- کد را از مخزن به‌روز می‌کند
- وابستگی‌های جدید را نصب می‌کند
- از دیتابیس پشتیبان می‌گیرد
- سرویس را مجدداً راه‌اندازی می‌کند

### حذف کامل
برای حذف کامل سرویس:
```bash
wget https://raw.githubusercontent.com/MohammadHosein-Morsali/PythonServiceManger/main/uninstall.sh
chmod +x uninstall.sh
sudo ./uninstall.sh
```

اسکریپت حذف:
- سرویس را متوقف و غیرفعال می‌کند
- از دیتابیس پشتیبان می‌گیرد
- تمام فایل‌ها و دسترسی‌ها را پاک می‌کند

### نصب دستی
اگر می‌خواهید به صورت دستی نصب کنید:

1. نصب پیش‌نیازها:
```bash
sudo apt update
sudo apt install python3-pip python3-venv git
```

2. کلون پروژه:
```bash
cd /opt
sudo git clone https://github.com/MohammadHosein-Morsali/PythonServiceManger.git
cd PythonServiceManger
```

3. ساخت محیط مجازی و نصب وابستگی‌ها:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. تنظیم دسترسی‌ها:
```bash
sudo groupadd -f systemd-service
sudo usermod -a -G systemd-service $USER
```

5. تنظیم دسترسی sudo:
```bash
sudo tee /etc/sudoers.d/service-manager << EOF
%systemd-service ALL=(ALL) NOPASSWD: /bin/systemctl
%systemd-service ALL=(ALL) NOPASSWD: /bin/journalctl
%systemd-service ALL=(ALL) NOPASSWD: /bin/chmod
%systemd-service ALL=(ALL) NOPASSWD: /bin/mv
EOF
sudo chmod 440 /etc/sudoers.d/service-manager
```

### نحوه استفاده

1. **ورود به پنل**:
   - مراجعه به `http://SERVER_IP:5000`
   - وارد کردن پسورد تنظیم شده

![ورود](screenshots/login.png)

2. **مدیریت سرویس‌ها**:
   - ایجاد سرویس جدید
   - شروع/توقف/راه‌اندازی مجدد سرویس‌ها
   - مشاهده وضعیت و لاگ‌ها

![سرویس‌ها](screenshots/services.png)

3. **مدیریت فایل‌ها**:
   - آپلود پروژه‌ها
   - ویرایش فایل‌های پیکربندی
   - مدیریت دسترسی‌ها

![مدیریت فایل](screenshots/file-manager.png)

4. **ترمینال تحت وب**:
   - اجرای دستورات سیستمی با دسترسی sudo
   - مشاهده خروجی در لحظه با WebSocket
   - پشتیبانی از رنگ‌های ANSI
   - قابلیت تغییر اندازه خودکار
   - پشتیبانی از کلیدهای کنترلی (مثل Ctrl+C)
   - عملکرد دوطرفه و بلادرنگ

![ترمینال](screenshots/terminal.png)

### مثال‌های عملی

1. **بات تلگرام**:
```python
# bot.py
import telebot

bot = telebot.TeleBot("YOUR_TOKEN")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! خوش آمدید")

bot.polling()
```

2. **سرویس FastAPI**:
```python
# api.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "سلام دنیا!"}
```

### عیب‌یابی

1. **خطای دسترسی**:
   - بررسی عضویت در گروه `systemd-service`
   - بررسی دسترسی‌های sudo
   - بررسی مالکیت فایل‌ها

2. **خطای سرویس**:
   - بررسی لاگ‌ها: `journalctl -u service-manager -f`
   - بررسی وضعیت: `systemctl status service-manager`
   - بررسی پورت: `netstat -tulpn | grep 5000`

3. **مشکل آپلود**:
   - بررسی دسترسی‌های پوشه
   - بررسی محدودیت حجم فایل

### نکات امنیتی
1. تغییر پسورد پیش‌فرض
2. تنظیم فایروال
3. استفاده از HTTPS
4. محدود کردن دسترسی sudo
5. استفاده از NOPASSWD برای دستورات مجاز
6. کنترل دسترسی‌های فایل و دایرکتوری

### ساختار پروژه
```
PythonServiceManger/
├── app.py              # برنامه اصلی
├── requirements.txt    # وابستگی‌ها
├── install.sh         # اسکریپت نصب
├── update.sh          # اسکریپت به‌روزرسانی
├── uninstall.sh       # اسکریپت حذف
└── static/            # فایل‌های استاتیک
```

### مشارکت
1. Fork کردن پروژه
2. ایجاد شاخه برای تغییرات
3. ارسال Pull Request

### لایسنس
این پروژه تحت لایسنس MIT منتشر شده است. 
```
           (بخش هایی از این پروژه با کرسر نوشته و حل باگ شده)
```
