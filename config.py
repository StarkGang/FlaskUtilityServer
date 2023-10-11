# Copyright (C) 2023-present by FlaskUtilityServer@Github, < https://github.com/StarkGang >.
#
# This file is part of < https://github.com/Starkgang/FlaskUtilityServer > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Starkgang/FlaskUtilityServer/blob/main/LICENSE >
#
# All rights reserved.

from os import getenv
from dotenv import load_dotenv
import secrets

load_dotenv('.env')

class CONFIG(object):
    FLASK_APP_HOST: str = getenv('FLASK_APP_HOST')
    FLASK_APP_PORT: int = getenv('FLASK_APP_PORT', 8080)
    APP_NAME: str = getenv('APP_NAME', 'Local Server')
    UPLOAD_FOLDER: str = getenv('UPLOAD_FOLDER', 'uploads')
    DOWNLOAD_FOLDER: str = getenv('DOWNLOAD_FOLDER', 'downloads')
    DEBUG: bool = getenv('DEBUG', False)
    USER: str = getenv('USER', getenv('USERNAME', 'User'))
    SYSREQ_PASSWORD: str = getenv('SYSREQ_PASSWORD', 22476)
    WEATHER_API_KEY: str = getenv('WEATHER_API_KEY')
    SECRET_USERNAME: str = getenv('SECRET_USERNAME', 'admin')
    SECRET_PASSWORD: str = getenv("SECRET_PASSWORD", "password")
    SECRET_KEY: str = getenv("SKEY", secrets.choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+"))