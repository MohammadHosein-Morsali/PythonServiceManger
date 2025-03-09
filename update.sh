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

print_message "در حال به‌روزرسانی پروژه..."

# مسیر پروژه
PROJECT_DIR="/opt/PythonServiceManger"

# به‌روزرسانی کد از گیت‌هاب
cd $PROJECT_DIR
print_message "در حال دریافت تغییرات از مخزن..."
git pull

# نصب وابستگی‌های جدید
print_message "در حال به‌روزرسانی وابستگی‌ها..."
source venv/bin/activate
pip install -r requirements.txt

# اعمال تغییرات دیتابیس
print_message "در حال به‌روزرسانی دیتابیس..."
if [ -f "instance/services.db" ]; then
    mv instance/services.db instance/services.db.backup
    print_message "از دیتابیس قبلی پشتیبان گرفته شد: services.db.backup"
fi

# تنظیم مجدد مالکیت فایل‌ها
print_message "در حال تنظیم مجدد دسترسی‌ها..."
chown -R $SUDO_USER:$SUDO_USER $PROJECT_DIR

# راه‌اندازی مجدد سرویس
print_message "در حال راه‌اندازی مجدد سرویس..."
systemctl restart service-manager

# بررسی وضعیت سرویس
if systemctl is-active --quiet service-manager; then
    print_success "به‌روزرسانی با موفقیت انجام شد!"
    echo
    print_message "سرویس در حال اجراست"
    print_message "برای مشاهده لاگ‌ها:"
    echo "journalctl -u service-manager -f"
else
    print_error "خطا در راه‌اندازی سرویس"
    echo "برای بررسی خطا:"
    echo "journalctl -u service-manager -n 50"
fi 