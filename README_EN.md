# Python Service Manager

A web-based interface for managing Python systemd services. This application allows you to manage systemd services for your Python applications through an intuitive web interface.

![Dashboard](screenshots/dashboard.png)

## Features
- Manage systemd services through web interface
- Secure authentication system
- Web-based terminal for command execution
- File management and project upload
- Support for various frameworks (Python, FastAPI, Flask)
- Custom command execution
- Service log viewing
- Automated updates and uninstallation

## Quick Installation
For quick and automated installation:
```bash
wget https://raw.githubusercontent.com/MohammadHosein-Morsali/PythonServiceManger/main/install.sh
chmod +x install.sh
sudo ./install.sh
```

![Installation](screenshots/install.png)

The installation script will ask for:
1. System username
2. Desired management panel password
3. Desired port (default: 5000)

The script automatically:
- Installs prerequisites
- Installs project in `/opt/PythonServiceManger`
- Creates Python virtual environment
- Sets up required permissions
- Creates and enables systemd service
- Configures firewall

## Automatic Updates
To update to the latest version:
```bash
wget https://raw.githubusercontent.com/MohammadHosein-Morsali/PythonServiceManger/main/update.sh
chmod +x update.sh
sudo ./update.sh
```

![Update](screenshots/update.png)

The update script:
- Updates code from repository
- Installs new dependencies
- Backs up database
- Restarts service

## Complete Uninstallation
To completely remove the service:
```bash
wget https://raw.githubusercontent.com/MohammadHosein-Morsali/PythonServiceManger/main/uninstall.sh
chmod +x uninstall.sh
sudo ./uninstall.sh
```

The uninstall script:
- Stops and disables service
- Backs up database
- Removes all files and permissions

## Manual Installation
If you prefer manual installation:

1. Install prerequisites:
```bash
sudo apt update
sudo apt install python3-pip python3-venv git
```

2. Clone project:
```bash
cd /opt
sudo git clone https://github.com/MohammadHosein-Morsali/PythonServiceManger.git
cd PythonServiceManger
```

3. Create virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. Set up permissions:
```bash
sudo groupadd -f systemd-service
sudo usermod -a -G systemd-service $USER
```

5. Configure sudo access:
```bash
sudo tee /etc/sudoers.d/service-manager << EOF
%systemd-service ALL=(ALL) NOPASSWD: /bin/systemctl
%systemd-service ALL=(ALL) NOPASSWD: /bin/journalctl
%systemd-service ALL=(ALL) NOPASSWD: /bin/chmod
%systemd-service ALL=(ALL) NOPASSWD: /bin/mv
EOF
sudo chmod 440 /etc/sudoers.d/service-manager
```

## Usage

1. **Login to Panel**:
   - Visit `http://SERVER_IP:5000`
   - Enter configured password

![Login](screenshots/login.png)

2. **Service Management**:
   - Create new services
   - Start/Stop/Restart services
   - View status and logs

![Services](screenshots/services.png)

3. **File Management**:
   - Upload projects
   - Edit configuration files
   - Manage permissions

![File Manager](screenshots/file-manager.png)

4. **Web Terminal**:
   - Execute system commands
   - View real-time output

![Terminal](screenshots/terminal.png)

## Practical Examples

1. **Telegram Bot**:
```python
# bot.py
import telebot

bot = telebot.TeleBot("YOUR_TOKEN")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Welcome")

bot.polling()
```

2. **FastAPI Service**:
```python
# api.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World!"}
```

## Troubleshooting

1. **Permission Errors**:
   - Check `systemd-service` group membership
   - Verify sudo permissions
   - Check file ownership

2. **Service Errors**:
   - Check logs: `journalctl -u service-manager -f`
   - Check status: `systemctl status service-manager`
   - Check port: `netstat -tulpn | grep 5000`

3. **Upload Issues**:
   - Check folder permissions
   - Check file size limits

## Security Notes
1. Change default password
2. Configure firewall
3. Use HTTPS
4. Limit sudo access

## Project Structure
```
PythonServiceManger/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── install.sh         # Installation script
├── update.sh          # Update script
├── uninstall.sh       # Uninstall script
└── static/            # Static files
```

## Contributing
1. Fork the project
2. Create feature branch
3. Submit Pull Request

## License
This project is licensed under the MIT License. 