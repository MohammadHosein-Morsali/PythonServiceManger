from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
import subprocess
import json
import venv
import shutil
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///services.db'
app.config['UPLOAD_FOLDER'] = '/mnt/d/MohammadHosein/server manager/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
db = SQLAlchemy(app)

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'py', 'txt', 'json', 'yaml', 'yml', 'env'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(500))
    file_path = db.Column(db.String(500), nullable=False)
    framework = db.Column(db.String(50), default='python')  # python, fastapi, flask, etc
    venv_path = db.Column(db.String(500))
    requirements = db.Column(db.Text)  # JSON string of requirements
    port = db.Column(db.Integer)
    host = db.Column(db.String(100), default='0.0.0.0')
    status = db.Column(db.String(20), default='stopped')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    environment_vars = db.Column(db.Text)  # JSON string of env vars

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
        
    commands = {
        'fastapi': f"uvicorn {Path(file_path).stem}:app --host {host} --port {port}",
        'flask': f"flask run --host={host} --port={port}",
        'python': f"python {file_path}"
    }
    return commands.get(framework, f"python {file_path}")

def create_systemd_service(service, custom_command=None):
    """Create a systemd service file with enhanced configuration"""
    env_vars = json.loads(service.environment_vars or '{}')
    env_vars_str = '\n'.join([f'Environment="{k}={v}"' for k, v in env_vars.items()])
    
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
User={os.getenv('USER')}
WorkingDirectory={os.path.dirname(service.file_path)}
Environment="PATH={service.venv_path}/bin:$PATH"
{env_vars_str}
ExecStart={service.venv_path}/bin/{start_command}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
    service_file = f"/etc/systemd/system/{service.name}.service"
    try:
        with open(service_file, 'w') as f:
            f.write(service_content)
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'])
        return True
    except Exception as e:
        print(f"Error creating service: {e}")
        return False

@app.route('/')
def index():
    services = Service.query.all()
    return render_template('index.html', services=services)

@app.route('/add_service', methods=['GET', 'POST'])
def add_service():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        framework = request.form['framework']
        project_dir = request.form.get('project_dir')
        requirements = request.form.get('requirements', '').splitlines()
        port = request.form.get('port', 8000)
        host = request.form.get('host', '0.0.0.0')
        env_vars = request.form.get('environment_vars', '{}')
        custom_command = request.form.get('custom_command')
        main_file = request.form.get('main_file')

        # Create project directory
        project_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(project_dir))
        os.makedirs(project_path, exist_ok=True)

        # Handle file uploads
        uploaded_files = request.files.getlist('files')
        main_file_path = None
        
        for file in uploaded_files:
            if file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(project_path, filename)
                file.save(file_path)
                
                # If this is the main file, store its path
                if filename == main_file:
                    main_file_path = file_path

        # If no main file was uploaded but a name was provided, use it
        if not main_file_path and main_file:
            main_file_path = os.path.join(project_path, secure_filename(main_file))

        # Create virtual environment
        venv_path = os.path.join(project_path, 'venv')
        create_venv(venv_path)
        
        # Install requirements
        if requirements:
            install_requirements(venv_path, requirements)
        
        new_service = Service(
            name=name,
            description=description,
            file_path=main_file_path if main_file_path else project_path,
            framework=framework,
            venv_path=venv_path,
            requirements=json.dumps(requirements),
            port=port,
            host=host,
            status='stopped',
            environment_vars=env_vars
        )
        
        if create_systemd_service(new_service, custom_command):
            db.session.add(new_service)
            db.session.commit()
            
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

@app.route('/files')
def file_manager():
    return render_template('files.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 