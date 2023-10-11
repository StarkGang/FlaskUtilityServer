# Copyright (C) -present by FlaskUtilityServer@Github, < https://github.com/StarkGang >.
#
# This file is part of < https://github.com/Starkgang/FlaskUtilityServer > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Starkgang/FlaskUtilityServer/blob/main/LICENSE >
#
# All rights reserved.

from flask import Flask, render_template, request, make_response, send_file, jsonify, session, redirect, url_for
from os import path as os_path
from werkzeug.utils import secure_filename
from time import time_ns
from pyperclip import copy as copy_to_clipboard
import subprocess
from config import CONFIG
from flask_socketio import SocketIO
from term_utils import UTILS
from passlib.hash import sha256_crypt
from utils import *

app = Flask(CONFIG.APP_NAME, template_folder='templates', static_folder='static')
base_dl_path = CONFIG.DOWNLOAD_FOLDER
upload_to = CONFIG.UPLOAD_FOLDER
app.secret_key = CONFIG.SECRET_KEY
valid_username = CONFIG.SECRET_USERNAME
hashed_password = sha256_crypt.hash(CONFIG.SECRET_PASSWORD)


excluded_paths = ['/static', '/favicon.ico', '/login', '/login_page', '/templates', '/static/img']

@app.before_request
def before_request():
    if 'username' not in session and request.endpoint not in ['login', 'login_page'] and not any(request.path.startswith(path) for path in excluded_paths):
        return redirect(url_for('login_page'))

socketio = SocketIO(app)

init_base(app, base_dl_path, upload_to)

@app.route('/terminal')
def terminal():
    return render_template('sio.html')

@app.route('/login_page/')
def login_page():
    if 'username' in session:
        return redirect("/")
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_p():
    if 'username' in session:
        return redirect("/")
    username = request.form.get('username')
    password = request.form.get('password')
    if username == valid_username and sha256_crypt.verify(password, hashed_password):
        session['username'] = username
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Invalid credentials'})


def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output, error

@socketio.on('execute_code')
def execute_code(data):
    if 'username' not in session and request.endpoint not in ['login', 'login_page'] and not any(request.path.startswith(path) for path in excluded_paths):
        return redirect(url_for('login_page'))
    command = data['code']
    utils = UTILS()
    to_return = ""
    if command.startswith("weather"):
        to_return += utils.get_weather(command.split(" ")[1])
    elif command.startswith("neofetch"):
        to_return += utils.neofetch()
    else:
        output, error = run_command(command)
        if not output:
            to_return += error.decode('utf-8')
        to_return += output.decode('utf-8')
    socketio.emit('execution_result', {'result': to_return})


@app.route('/sys_info')
def si():
    context = {
        'platform_info': get_platform_info(),
        'power_info': get_power_info(),
        'user_info': get_user_info(),
        'memory_info': get_memory_info(),
        'disk_info': get_disks_info(),
        'network_info': get_network_info(),
    }
    return render_template("si.html", context=context)

@app.route('/favicon.ico')
def favicon():
    return send_file('./static/img/nicon.png', mimetype='image/png')

@app.route('/')
@app.route('/index/')
def home():
    app.logger.info(f'Index page loaded by IP : {request.remote_addr}')
    return render_template('index.html')

@app.route("/sysreq/", methods=['POST'])
def sysreq():
    app.logger.info(f'Sysreq page loaded by IP : {request.remote_addr}')
    password = int(request.form.get('password'))
    if password == CONFIG.SYSREQ_PASSWORD:
        handle_system_opp(1)
    else:
        return "Error"
    return "shutting down"

@app.route('/copy', methods=['GET'])
def copy():
    app.logger.info(f'Copy page loaded by IP : {request.remote_addr}')
    return render_template('copy.html')

         
@app.route('/copy', methods=['POST'])
def submit():
    app.logger.info(f'Copy Submit page loaded by IP : {request.remote_addr}')
    copy_text = request.form.get('copy_text')
    copy_utils = COPY_UTILS()
    if valid := URL_VALIDATOR(copy_text)():
        copy_utils.open_and_write_url_to_file(copy_text, copy_utils.request_and_return_page_name(copy_text), valid)
    app.logger.info(f'Copied! \nInput: {copy_text}')
    copy_to_clipboard(copy_text)
    return "Copied!"

@app.route('/upload')
def index():
    app.logger.info(f'Upload page loaded by IP : {request.remote_addr}')
    return render_template('upload.html',
                           page_name='Main',
                           project_name="pydrop")


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    save_path = os_path.join(upload_to, secure_filename(file.filename))
    current_chunk = int(request.form['dzchunkindex'])
    if os_path.exists(save_path) and current_chunk == 0:
        return make_response(('File already exists', 400))
    try:
        with open(save_path, 'ab') as f:
            f.seek(int(request.form['dzchunkbyteoffset']))
            f.write(file.stream.read())
    except OSError:
        app.logger.error('Could not write to file')
        return make_response(("Not sure why,"
                              " but we couldn't write the file to disk", 500))

    total_chunks = int(request.form['dztotalchunkcount'])
    if current_chunk + 1 == total_chunks:
        if os_path.getsize(save_path) != int(request.form['dztotalfilesize']):
            app.logger.error(f"File {file.filename} was completed, "
                      f"but has a size mismatch."
                      f"Was {os_path.getsize(save_path)} but we"
                      f" expected {request.form['dztotalfilesize']} ")
            return make_response(('Size mismatch', 500))
        else:
            app.logger.info(f'File {file.filename} has been uploaded successfully')
    return "Chunk upload successful"


@app.route('/files/')
def files():
    app.logger.info(f'Files page loaded by IP : {request.remote_addr}')
    search_query = request.args.get('search', '').lower()
    path = request.args.get('path', '')
    files_and_folders = get_files_and_folders(base_dl_path, path, search_query)
    return render_template('files.html', files=files_and_folders, search_query=search_query, current_path=path)

@app.route('/download/<path:filename>')
def download(filename):
    app.logger.info(f'Download page loaded by IP : {request.remote_addr}')
    file_path = os_path.join(base_dl_path, filename)
    return send_file(file_path, as_attachment=True)

@app.route('/folder')
def load_folder_content():
    app.logger.info(f'Folder page loaded by IP : {request.remote_addr}')
    folder_path = request.args.get('path', '')
    files_and_folders = get_files_and_folders(base_dl_path, folder_path)
    return render_template('folder_content.html', files=files_and_folders)


if __name__ == '__main__':
    ipv4_add = CONFIG.FLASK_APP_HOST or get_ipv4_address(logger=app.logger)
    app.logger.info(f'Server started! \nUsing Host : {ipv4_add} and Port : {CONFIG.FLASK_APP_PORT} \nTime : {CONVERT_TO_RD_TIME(time_ns())()}')
    app.run(host=ipv4_add, port=CONFIG.FLASK_APP_PORT, debug=CONFIG.DEBUG)
