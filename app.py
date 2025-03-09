from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
import os
import subprocess
import json
import venv
import shutil
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()  # کلید تصادفی برای امنیت بیشتر
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///services.db'
app.config['UPLOAD_FOLDER'] = os.path.expanduser('~/servermanager/uploads')  # تغییر مسیر به پوشه کاربر
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# خواندن پسورد از فایل کانفیگ
config_file = os.path.join(os.path.dirname(__file__), 'config.json')
if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
        app.config['ADMIN_PASSWORD'] = config.get('password', '123456')
else:
    app.config['ADMIN_PASSWORD'] = '123456'  # پسورد پیش‌فرض

# تنظیمات چند زبانه
TRANSLATIONS = {}
for lang in ['fa', 'en']:
    translation_file = os.path.join(os.path.dirname(__file__), f'translations/{lang}.json')
    if os.path.exists(translation_file):
        with open(translation_file, 'r', encoding='utf-8') as f:
            TRANSLATIONS[lang] = json.load(f)

def get_text(key, lang=None):
    """Get translated text for the given key"""
    if not lang:
        lang = session.get('lang', 'fa')
    
    # Split the key by dots (e.g., "login.title" -> ["login", "title"])
    parts = key.split('.')
    value = TRANSLATIONS.get(lang, {})
    
    # Navigate through nested dictionary
    for part in parts:
        value = value.get(part, '')
    
    return value or key

app.jinja_env.globals.update(get_text=get_text)

db = SQLAlchemy(app)

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'py', 'txt', 'json', 'yaml', 'yml', 'env'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(500))
    directory_path = db.Column(db.String(500), nullable=False)
    file_path = db.Column(db.String(500))  # مسیر فایل اصلی
    main_file = db.Column(db.String(500))
    framework = db.Column(db.String(50), default='python')
    custom_command = db.Column(db.String(500))
    status = db.Column(db.String(20), default='stopped')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    port = db.Column(db.Integer, default=8000)  # پورت سرویس
    host = db.Column(db.String(50), default='0.0.0.0')  # هاست سرویس
    venv_path = db.Column(db.String(500))  # مسیر محیط مجازی
    requirements = db.Column(db.Text)  # وابستگی‌ها به صورت JSON
    environment_vars = db.Column(db.Text)  # متغیرهای محیطی به صورت JSON

with app.app_context():
    db.create_all()

def create_venv(path):
    """Create a virtual environment at the specified path"""
    venv.create(path, with_pip=True)

def install_requirements(venv_path, requirements):
    """Install requirements in the virtual environment"""
    pip_path = os.path.join(venv_path, 'bin', 'pip')
    for req in requirements:
        try:
            subprocess.run([pip_path, 'install', req], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error installing {req}: {e}")

def get_framework_start_command(framework, file_path, host, port, custom_command=None):
    """Get the start command based on the framework"""
    if framework == 'custom' and custom_command:
        return custom_command

    file_name = os.path.basename(file_path)
    module_name = Path(file_name).stem
        
    commands = {
        'fastapi': f"-m uvicorn {module_name}:app --host {host} --port {port}",
        'flask': f"-m flask run --host={host} --port={port}",
        'python': f"{file_name}"
    }
    return commands.get(framework, file_name)

def create_systemd_service(service, custom_command=None):
    """Create a systemd service file with enhanced configuration"""
    env_vars = json.loads(service.environment_vars or '{}')
    env_vars_str = '\n'.join([f'Environment="{k}={v}"' for k, v in env_vars.items()])
    
    # Get absolute paths
    work_dir = os.path.abspath(os.path.dirname(service.file_path))
    
    # Determine Python executable
    if service.venv_path:
        python_path = os.path.join(service.venv_path, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(service.venv_path, 'bin', 'python')
        env_path = f"{service.venv_path}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    else:
        python_path = 'python3'  # Use system Python
        env_path = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    
    start_command = get_framework_start_command(
        service.framework, 
        service.file_path,
        service.host,
        service.port,
        custom_command
    )

    service_content = f"""[Unit]
Description={service.description}
After=network.target

[Service]
Type=simple
User={os.getenv('USER', os.getenv('USERNAME'))}
WorkingDirectory={work_dir}
Environment="PATH={env_path}"
Environment="PYTHONPATH={work_dir}"
{env_vars_str}
ExecStart={python_path} {start_command}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
    service_file = f"/etc/systemd/system/{service.name}.service"
    try:
        # Write service content to a temporary file
        temp_file = f"/tmp/{service.name}.service"
        with open(temp_file, 'w') as f:
            f.write(service_content)
        
        print(f"Service content:\n{service_content}")  # Debug print
        
        # Move the file to systemd directory using sudo
        subprocess.run(['sudo', 'mv', temp_file, service_file], check=True)
        # Set correct permissions
        subprocess.run(['sudo', 'chmod', '644', service_file], check=True)
        # Reload systemd
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
        return True
    except Exception as e:
        print(f"Error creating service: {e}")
        return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            return redirect(url_for('index'))
        flash('Invalid password!', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    services = Service.query.all()
    return render_template('index.html', services=services)

@app.route('/terminal')
@login_required
def terminal():
    return render_template('terminal.html')

@app.route('/execute_command', methods=['POST'])
@login_required
def execute_command():
    command = request.form.get('command')
    try:
        result = subprocess.run(command.split(), capture_output=True, text=True)
        return jsonify({
            'output': result.stdout,
            'error': result.stderr
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/file_manager')
@login_required
def file_manager():
    path = request.args.get('path', '/')
    try:
        items = []
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            items.append({
                'name': item,
                'path': full_path,
                'type': 'directory' if os.path.isdir(full_path) else 'file',
                'size': os.path.getsize(full_path) if os.path.isfile(full_path) else 0
            })
        return render_template('file_manager.html', items=items, current_path=path)
    except Exception as e:
        flash(f'Error accessing path: {str(e)}', 'error')
        return redirect(url_for('file_manager', path='/'))

@app.route('/copy_path')
@login_required
def copy_path():
    path = request.args.get('path')
    return jsonify({'path': path})

@app.route('/add_service', methods=['GET', 'POST'])
@login_required
def add_service():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        directory_path = request.form['directory_path']
        framework = request.form['framework']
        custom_command = request.form.get('custom_command')
        main_file = request.files.get('main_file')
        additional_files = request.files.getlist('additional_files')

        # Validate directory
        if not os.path.exists(directory_path):
            try:
                os.makedirs(directory_path)
            except Exception as e:
                flash(f'Error creating directory: {str(e)}', 'error')
                return redirect(url_for('add_service'))

        # Check if directory is already in use
        if Service.query.filter_by(directory_path=directory_path).first():
            flash('This directory is already in use by another service!', 'error')
            return redirect(url_for('add_service'))

        # Save main file if provided
        main_file_path = None
        if main_file:
            filename = secure_filename(main_file.filename)
            main_file_path = os.path.join(directory_path, filename)
            main_file.save(main_file_path)

        # Save additional files
        for file in additional_files:
            if file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(directory_path, filename)
                file.save(file_path)

        new_service = Service(
            name=name,
            description=description,
            directory_path=directory_path,
            file_path=main_file_path if main_file_path else None,
            framework=framework,
            custom_command=custom_command
        )

        try:
            db.session.add(new_service)
            db.session.commit()
            flash('Service created successfully!', 'success')
        except Exception as e:
            flash(f'Error creating service: {str(e)}', 'error')

        return redirect(url_for('index'))

    return render_template('add_service.html')

@app.route('/service/<int:service_id>/<action>')
def manage_service(service_id, action):
    service = Service.query.get_or_404(service_id)
    
    if action in ['start', 'stop', 'restart']:
        try:
            subprocess.run(['sudo', 'systemctl', action, f"{service.name}.service"])
            service.status = 'running' if action != 'stop' else 'stopped'
            db.session.commit()
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return redirect(url_for('index'))

@app.route('/edit_service/<int:service_id>', methods=['GET', 'POST'])
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    
    if request.method == 'POST':
        service.description = request.form['description']
        service.file_path = request.form['file_path']
        service.framework = request.form['framework']
        service.port = request.form.get('port', 8000)
        service.host = request.form.get('host', '0.0.0.0')
        
        new_requirements = request.form.get('requirements', '').splitlines()
        if new_requirements != json.loads(service.requirements or '[]'):
            service.requirements = json.dumps(new_requirements)
            install_requirements(service.venv_path, new_requirements)
        
        service.environment_vars = request.form.get('environment_vars', '{}')
        
        if create_systemd_service(service):
            db.session.commit()
            
        return redirect(url_for('index'))
    
    return render_template('edit_service.html', service=service)

@app.route('/delete_service/<int:service_id>')
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    
    try:
        # Stop and disable the service
        subprocess.run(['sudo', 'systemctl', 'stop', f"{service.name}.service"])
        subprocess.run(['sudo', 'systemctl', 'disable', f"{service.name}.service"])
        # Remove service file
        os.remove(f"/etc/systemd/system/{service.name}.service")
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'])
        
        # Remove virtual environment if exists
        if service.venv_path and os.path.exists(service.venv_path):
            shutil.rmtree(service.venv_path)
        
        db.session.delete(service)
        db.session.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
    return redirect(url_for('index'))

@app.route('/service/<int:service_id>/logs')
def view_logs(service_id):
    service = Service.query.get_or_404(service_id)
    try:
        result = subprocess.run(['journalctl', '-u', f"{service.name}.service", '-n', '100', '--no-pager'],
                              capture_output=True, text=True)
        logs = result.stdout
        return render_template('logs.html', service=service, logs=logs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/create_directory', methods=['POST'])
def create_directory():
    try:
        directory = request.form.get('directory')
        if directory:
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(directory))
            os.makedirs(full_path, exist_ok=True)
            return jsonify({'success': True, 'path': full_path})
        return jsonify({'error': 'No directory name provided'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload_file', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        directory = request.form.get('directory', '')
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_path = app.config['UPLOAD_FOLDER']
            
            if directory:
                upload_path = os.path.join(upload_path, secure_filename(directory))
                os.makedirs(upload_path, exist_ok=True)
                
            file_path = os.path.join(upload_path, filename)
            file.save(file_path)
            return jsonify({
                'success': True,
                'path': file_path,
                'filename': filename
            })
            
        return jsonify({'error': 'File type not allowed'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/list_files')
def list_files():
    try:
        directory = request.args.get('directory', '')
        base_path = app.config['UPLOAD_FOLDER']
        
        if directory:
            base_path = os.path.join(base_path, secure_filename(directory))
            
        if not os.path.exists(base_path):
            return jsonify({'error': 'Directory not found'}), 404
            
        files = []
        directories = []
        
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if os.path.isfile(item_path):
                files.append({
                    'name': item,
                    'path': item_path,
                    'size': os.path.getsize(item_path),
                    'type': 'file'
                })
            else:
                directories.append({
                    'name': item,
                    'path': item_path,
                    'type': 'directory'
                })
                
        return jsonify({
            'current_path': base_path,
            'directories': directories,
            'files': files
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/language/<lang>')
def set_language(lang):
    """Set the user's preferred language"""
    if lang in TRANSLATIONS:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 