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

print_message "در حال حذف سرویس..."

# توقف و غیرفعال‌سازی سرویس
print_message "در حال توقف سرویس..."
systemctl stop service-manager
systemctl disable service-manager

# حذف فایل سرویس
print_message "در حال حذف فایل سرویس..."
rm -f /etc/systemd/system/service-manager.service
systemctl daemon-reload

# حذف گروه و دسترسی‌های sudo
print_message "در حال حذف دسترسی‌ها..."
rm -f /etc/sudoers.d/service-manager

# پشتیبان‌گیری از دیتابیس
if [ -f "/opt/PythonServiceManger/instance/services.db" ]; then
    print_message "در حال پشتیبان‌گیری از دیتابیس..."
    cp /opt/PythonServiceManger/instance/services.db ~/services.db.backup
    print_message "از دیتابیس در مسیر ~/services.db.backup پشتیبان گرفته شد"
fi

# حذف پوشه پروژه
print_message "در حال حذف فایل‌های پروژه..."
rm -rf /opt/PythonServiceManger

print_success "سرویس با موفقیت حذف شد!"
echo
print_message "برای نصب مجدد می‌توانید از اسکریپت install.sh استفاده کنید"
print_message "فایل پشتیبان دیتابیس: ~/services.db.backup" 