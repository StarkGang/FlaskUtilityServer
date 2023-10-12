# Copyright (C) -present by FlaskUtilityServer@Github, < https://github.com/StarkGang >.
#
# This file is part of < https://github.com/Starkgang/FlaskUtilityServer > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Starkgang/FlaskUtilityServer/blob/main/LICENSE >
#
# All rights reserved.

import base64
from flask import Flask, render_template, request, make_response, send_file, jsonify, session, redirect, url_for
from os import path as os_path
from werkzeug.utils import secure_filename
from time import time_ns
from pyperclip import copy as copy_to_clipboard
from PIL import ImageGrab
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
socketio = SocketIO(app)
excluded_paths = ['/static', '/favicon.ico', '/login', '/login_page', '/templates', '/static/img', '/matrix']


@app.errorhandler(Exception)
def handle_error(error):
    """
Handles the error raised by the Flask application.

The function prints the error message, retrieves the error code from the error object (defaulting to 500 if not available), and converts the error object to a string for error details. It then renders the 'error.html' template with the error code and error details.

Args:
    error: The error object.

Returns:
    The rendered template.
"""
    error_code = getattr(error, 'code', 500)
    error_details = str(error)
    return render_template('error.html', error_code=error_code, error_details=error_details)

@app.before_request
def before_request():
    """
Executes the before_request function for a Flask application.

The function checks if the 'username' key is not present in the session and if the request endpoint is not one of the excluded paths. If both conditions are met, it redirects the user to the '/login_page' endpoint.

Args:
    None

Returns:
    Redirects to page
"""

    if 'username' not in session and request.endpoint not in ['login', 'login_page'] and not any(request.path.startswith(path) for path in excluded_paths):
        return redirect('/login_page')
    


@app.route('/matrix')
def matrix():
    """
Renders the 'matrix.html' template with a speed value of 50.

Args:
    None

Returns:
    The rendered template.
"""

    return render_template('matrix.html', speed=50)


@app.route('/ss')
def ss():
    """
Renders the 'screenshot.html' template.

Args:
    None

Returns:
    The rendered template.
"""

    return render_template('screenshot.html')


@app.route('/screenshot', methods=['POST'])
def capture_screenshot():
    """
Captures a screenshot and returns it as a base64-encoded image.

The function uses the `ImageGrab.grab()` function from the `PIL` library to capture a screenshot. If an exception occurs during the capture, it returns a JSON response with an error message. Otherwise, it saves the screenshot as a PNG image in memory, converts it to base64 encoding, and returns a JSON response with the base64-encoded image.

Args:
    None

Returns:
    A JSON response containing the base64-encoded image.
"""
    try:
        screenshot = ImageGrab.grab()
    except Exception:
        return jsonify(error='Unable to capture screenshot')
    img_io = io.BytesIO()
    screenshot.save(img_io, format='PNG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.read()).decode('utf-8')
    return jsonify(img_base64=img_base64)



@app.route('/terminal')
def terminal():
    """
Renders the 'sio.html' template.

Args:
    None

Returns:
    The rendered template.
"""

    return render_template('sio.html')

@app.route('/login_page/')
def login_page():
    """
Handles the login process for the '/login' endpoint.

The function checks if the 'username' key is already present in the session. If it is, the user is redirected to the root URL '/'. Otherwise, the function retrieves the 'username' and 'password' values from the request form. If the provided username matches the valid username and the provided password matches the hashed password, the user is authenticated by adding the 'username' key to the session and returning a JSON response with a 'success' value of True. Otherwise, a JSON response with an 'error' message is returned.

Args:
    None

Returns:
    A JSON response indicating the success or failure of the login process.
"""

    if 'username' in session:
        return redirect("/")
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_p():
    """
Handles the login process for the '/login' endpoint.

The function checks if the 'username' key is already present in the session. If it is, the user is redirected to the root URL '/'. Otherwise, the function retrieves the 'username' and 'password' values from the request form. If the provided username matches the valid username and the provided password matches the hashed password, the user is authenticated by adding the 'username' key to the session and returning a JSON response with a 'success' value of True. Otherwise, a JSON response with an 'error' message is returned.

Args:
    None

Returns:
    A JSON response indicating the success or failure of the login process.
"""

    if 'username' in session:
        return redirect("/")
    username = request.form.get('username')
    password = request.form.get('password')
    if username == valid_username and sha256_crypt.verify(password, hashed_password):
        session['username'] = username
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Invalid credentials'})


@socketio.on('execute_code')
def execute_code(data):
    """
Executes the code provided by the client.

The function first checks if the user is not logged in and the current endpoint is not 'login' or 'login_page', and the request path does not start with any of the excluded paths. If these conditions are met, the user is redirected to the '/login_page' endpoint. Otherwise, the function retrieves the code from the 'data' parameter and initializes a UTILS object. It then executes different commands based on the prefix of the code. If the code starts with 'weather', it calls the 'get_weather' method of the UTILS object. If the code starts with 'neofetch', it calls the 'neofetch' method of the UTILS object. Otherwise, it runs the command using the 'run_command' function and captures the output and error. The function then constructs a response string by decoding the output and error, and emits the response to the client using the 'socketio.emit' function.

Args:
    data (dict): A dictionary containing the code provided by the client.

Returns:
    None
"""

    if 'username' not in session and request.endpoint not in ['login', 'login_page'] and not any(request.path.startswith(path) for path in excluded_paths):
        return redirect('/login_page')
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
    """
Renders the 'si.html' template with system information.

The function retrieves various system information using helper functions and stores them in a context dictionary. The context dictionary includes information about the platform, power, user, memory, disks, and network. The function then renders the 'si.html' template with the context as a parameter.

Args:
    None

Returns:
    The rendered template with system information.
"""

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
    """
Serves the favicon.ico file.

The function returns the favicon.ico file located at './static/img/nicon.png' with the mimetype 'image/png'.

Args:
    None

Returns:
    The favicon.ico file as a response.
"""

    return send_file('./static/img/nicon.png', mimetype='image/png')

@app.route('/')
@app.route('/index/')
def home():
    return render_template('index.html')

@app.route("/sysreq/", methods=['POST'])
def sysreq():
    password = int(request.form.get('password'))
    if password == CONFIG.SYSREQ_PASSWORD:
        handle_system_opp(1)
    else:
        return "Error"
    return "shutting down"

@app.route('/copy', methods=['GET'])
def copy():
    return render_template('copy.html')

         
@app.route('/copy', methods=['POST'])
def submit():
    copy_text = request.form.get('copy_text')
    copy_utils = COPY_UTILS()
    if valid := URL_VALIDATOR(copy_text)():
        copy_utils.open_and_write_url_to_file(copy_text, copy_utils.request_and_return_page_name(copy_text), valid)
    app.logger.info(f'Copied! \nInput: {copy_text}')
    copy_to_clipboard(copy_text)
    return "Copied!"

@app.route('/upload')
def index():
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
    search_query = request.args.get('search', '').lower()
    path = request.args.get('path', '')
    files_and_folders = get_files_and_folders(base_dl_path, path, search_query)
    return render_template('files.html', files=files_and_folders, search_query=search_query, current_path=path)

@app.route('/download/<path:filename>')
def download(filename):
    file_path = os_path.join(base_dl_path, filename)
    return send_file(file_path, as_attachment=True)

@app.route('/folder')
def load_folder_content():
    folder_path = request.args.get('path', '')
    files_and_folders = get_files_and_folders(base_dl_path, folder_path)
    return render_template('folder_content.html', files=files_and_folders)


if __name__ == '__main__':
    ipv4_add = CONFIG.FLASK_APP_HOST or get_ipv4_address(logger=app.logger)
    app.logger.info(f'Server started! \nUsing Host : {ipv4_add} and Port : {CONFIG.FLASK_APP_PORT} \nTime : {CONVERT_TO_RD_TIME(time_ns())()}')
    app.run(host=ipv4_add, port=CONFIG.FLASK_APP_PORT, debug=CONFIG.DEBUG)
