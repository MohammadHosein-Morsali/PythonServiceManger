#!/bin/bash

# رنگ‌ها برای خروجی بهتر
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# تابع نمایش پیام
print_message() {
    echo -e "${BLUE}[*]${NC} $1"
}

# تابع نمایش خطا
print_error() {
    echo -e "${RED}[!]${NC} $1"
}

# تابع نمایش موفقیت
print_success() {
    echo -e "${GREEN}[+]${NC} $1"
}

# بررسی اجرا با دسترسی روت
if [ "$EUID" -ne 0 ]; then 
    print_error "این اسکریپت باید با دسترسی روت اجرا شود"
    print_message "لطفاً با دستور sudo اجرا کنید:"
    echo "sudo $0"
    exit 1
fi

# دریافت اطلاعات از کاربر
read -p "نام کاربری سیستم را وارد کنید: " USERNAME
read -s -p "پسورد پنل مدیریت را وارد کنید: " PANEL_PASSWORD
echo
read -p "پورت پنل مدیریت را وارد کنید [5000]: " PANEL_PORT
PANEL_PORT=${PANEL_PORT:-5000}

# نصب پیش‌نیازها
print_message "در حال نصب پیش‌نیازها..."
apt update
apt install -y python3-pip python3-venv git ufw

# کلون پروژه
print_message "در حال کلون کردن پروژه..."
cd /opt
git clone https://github.com/MohammadHosein-Morsali/PythonServiceManger.git
cd PythonServiceManger

# ساخت محیط مجازی و نصب وابستگی‌ها
print_message "در حال نصب وابستگی‌ها..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# تنظیم مالکیت فایل‌ها
chown -R $USERNAME:$USERNAME /opt/PythonServiceManger

# ایجاد گروه و تنظیم دسترسی‌ها
print_message "در حال تنظیم دسترسی‌ها..."
groupadd -f systemd-service
usermod -a -G systemd-service $USERNAME

# تنظیم دسترسی‌های sudo
cat > /etc/sudoers.d/service-manager << EOF
%systemd-service ALL=(ALL) NOPASSWD: /bin/systemctl
%systemd-service ALL=(ALL) NOPASSWD: /bin/journalctl
%systemd-service ALL=(ALL) NOPASSWD: /bin/chmod
%systemd-service ALL=(ALL) NOPASSWD: /bin/mv
EOF
chmod 440 /etc/sudoers.d/service-manager

# تنظیم پسورد در فایل کانفیگ
print_message "در حال تنظیم کانفیگ برنامه..."
sed -i "s/your-password-here/$PANEL_PASSWORD/" app.py
sed -i "s/port=5000/port=$PANEL_PORT/" app.py

# ایجاد سرویس systemd
print_message "در حال ایجاد سرویس..."
cat > /etc/systemd/system/service-manager.service << EOF
[Unit]
Description=Python Service Manager
After=network.target

[Service]
User=$USERNAME
WorkingDirectory=/opt/PythonServiceManger
Environment="PATH=/opt/PythonServiceManger/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/opt/PythonServiceManger/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# تنظیم فایروال
print_message "در حال تنظیم فایروال..."
ufw allow $PANEL_PORT/tcp
ufw --force enable

# راه‌اندازی سرویس
print_message "در حال راه‌اندازی سرویس..."
systemctl daemon-reload
systemctl enable service-manager
systemctl start service-manager

# بررسی وضعیت سرویس
if systemctl is-active --quiet service-manager; then
    print_success "نصب با موفقیت انجام شد!"
    echo
    echo "اطلاعات دسترسی:"
    echo "URL: http://SERVER_IP:$PANEL_PORT"
    echo "Password: $PANEL_PASSWORD"
    echo
    print_message "برای مشاهده لاگ‌ها:"
    echo "journalctl -u service-manager -f"
else
    print_error "خطا در راه‌اندازی سرویس"
    echo "برای بررسی خطا:"
    echo "journalctl -u service-manager -n 50"
fi 