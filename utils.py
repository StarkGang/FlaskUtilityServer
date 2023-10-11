# Copyright (C) 2023-present by FlaskUtilityServer@Github, < https://github.com/StarkGang >.
#
# This file is part of < https://github.com/Starkgang/FlaskUtilityServer > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Starkgang/FlaskUtilityServer/blob/main/LICENSE >
#
# All rights reserved.

from subprocess import run
from logging import Logger, Formatter, INFO
from logging.handlers import RotatingFileHandler
from re import compile
from requests import get as get_url
from os import path as os_path, walk, mkdir, system as system_call
from urllib.parse import urlparse
import psutil
import platform
import psutil
from datetime import datetime
from psutil._common import bytes2human
import logging
from psutil._common import bytes2human
from datetime import datetime
from config import CONFIG
from bs4 import BeautifulSoup
from csv import reader, writer
from typing import Any, Union
from flask import Flask

logger = logging.getLogger()

def init_base(app: Flask, base_dl_path: str, upload_to: str) -> None:
    """Initialise the logger and base download path, upload path"""
    logger_setup(app)
    check_folder_exists([base_dl_path, upload_to])

def get_ipv4_address(logger: Logger) -> str:
    """Get the IPv4 Address of the machine"""
    try:
        result = run(['ipconfig'], capture_output=True, text=True)
        if result.returncode == 0:
            ipv4_pattern = compile(r'IPv4 Address[.\s]+:\s*([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)')
            if match := ipv4_pattern.search(result.stdout):
                logger.info(f"IPv4 Address found: {match.group(1)}")
                return match.group(1)
            else:
                logger.warning("IPv4 Address not found")
                return "0.0.0.0"
        else:
            logger.error("Error getting IPv4 Address")
            return "0.0.0.0"
    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}")
        return "0.0.0.0"
    

def check_folder_exists(folder_path: Union[str, list]) -> bool:
    """Check if the folder exists"""
    if isinstance(folder_path, str):
        folder_path = [folder_path]
    for folder in folder_path:
        if not os_path.isdir(folder):
            mkdir(folder)
            
def logger_setup(app: Flask) -> None:
    """Setup the logger"""
    log_formatter = Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
    log_handler = RotatingFileHandler('traceback.log', maxBytes=100000, backupCount=1)
    log_handler.setFormatter(log_formatter)
    app.logger.addHandler(log_handler)
    app.logger.setLevel(INFO)
    return 



def handle_system_opp(switch=0):
    """Handle the system opperation"""
    cmd = "shutdown /s /t 600" if switch == 1 else "shutdown /r /t 600"
    system_call(cmd)
    
def get_files_and_folders(base_dl_path: str, path: str, search_query: str='') -> list:
    """Get the files and folders in the path"""
    full_path = os_path.join(base_dl_path, path)
    files_and_folders = []
    for root, dirs, files in walk(full_path):
        if root != full_path:
            continue
        for folder in dirs:
            folder_path = os_path.relpath(os_path.join(root, folder), base_dl_path)
            if search_query in folder.lower():
                files_and_folders.append({'type': 'folder', 'name': folder_path})
        for file in files:
            file_path = os_path.relpath(os_path.join(root, file), base_dl_path)
            if search_query in file.lower():
                files_and_folders.append({'type': 'file', 'name': file_path})
    return files_and_folders
    
class COPY_UTILS:
    def __init__(self) -> None:
        pass

    def is_url_in_csv(self, url: str, csv_file: str) -> bool:
        """Check if the url is in the csv file"""
        file_exists = os_path.isfile(csv_file)
        if not file_exists: return False
        with open(csv_file, 'r') as file:
            c_reader = reader(file)
            for row in c_reader:
                if row and row[0] == url:
                    return True
        return False
    

    def request_and_return_page_name(self, url: str) -> str:
        """Request the url and return the page name"""
        try:
            response = get_url(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup.title.string
        except Exception as e:
            return "No Title Found"

    def open_and_write_url_to_file(self, url: str, page_title: str, site_name_from_url: str) -> None:
        """Open the file and write the url to the file"""
        _file = "url_stored/some.csv"
        if self.is_url_in_csv(url, _file): return 
        file_p = open(_file, "a") if os_path.isfile(_file) else open(_file, "w")
        cwriter = writer(file_p)
        if os_path.getsize(_file) == 0:
            cwriter.writerow(["url", "page_title", "site_name"])
        cwriter.writerow([url, page_title, site_name_from_url])
        return file_p.close()
    

class CONVERT_TO_RD_TIME:
    def __init__(self, sc) -> None:
        self.sc = sc

    def __call__(self) -> Any:
        """Convert the seconds to readable time"""
        seconds = self.sc % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return "%d:%02d:%02d" % (hour, minutes, seconds)
    
class BYTES_TO_OTHER_UNITS:
    def __init__(self, bytes_str) -> None:
        self.bytes_str = bytes_str 

    def __call__(self) -> Any:
        """Convert the bytes to other units"""
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if self.bytes_str < factor:
                return f"{self.bytes_str:.2f}{unit}B"
            self.bytes_str /= factor


class URL_VALIDATOR:
    def __init__(self, url) -> None:
        self.url = url

    def __call__(self) -> Any:
        """Validate the url"""
        try:
            return (urlparse(self.url)).netloc
        except ValueError:
            return False
        

def get_user_processes():
    process_attributes = ['pid', 'name', 'username', 'status', 'create_time', 'memory_percent', 'cpu_percent']
    return {
        process.pid: {
            'pid': process.info['pid'],
            'name': process.info['name'],
            'username': process.info['username'],
            'status': process.info['status'],
            'create_time': datetime.fromtimestamp(process.info['create_time']),
            'memory_percent': process.info['memory_percent'],
            'cpu_percent': process.info['cpu_percent'],
        }
        for process in psutil.process_iter(process_attributes)
        if process.info['username'] == CONFIG.USER
    }

def get_process_details(pid):
    if psutil.pid_exists(pid):
        process = psutil.Process(pid)
        process_info = process.as_dict()
        return {
            "create_time": datetime.fromtimestamp(process_info['create_time']),
            "status": process_info['status'],
            "cpu_percent": process_info['cpu_percent'],
            "name": process_info['name'],
            "memory_rss": bytes2human(process_info['memory_info'][0]),
            "memory_vms": bytes2human(process_info['memory_info'][1]),
            "exe": process_info['exe'],
            "username": process_info['username'],
            "num_threads": process_info['num_threads'],
            "memory_percent": process_info['memory_percent'],
            "pid": process_info['pid'],
            "cpu_times": process_info['cpu_times'],
        }
    return None


def get_platform_info():
    uname = platform.uname()
    boot_time = psutil.boot_time()
    if psutil.MACOS:
        os_name = 'apple'
    elif psutil.WINDOWS:
        os_name = 'windows'
    elif psutil.LINUX:
        os_name = 'linux'
    else:
        os_name = 'Unknown'

    return {
        'os_name': os_name,
        'node_name': uname.node.split('.')[0],
        'system_name': uname.system,
        'release_version': uname.release,
        'architecture': platform.architecture()[0],
        'processor_type': platform.processor(),
        'boot_time': datetime.now() - datetime.fromtimestamp(boot_time),
    }

def get_power_info():
    power_data = psutil.sensors_battery()
    if power_data.secsleft in (psutil.POWER_TIME_UNKNOWN, psutil.POWER_TIME_UNLIMITED):
        time_remaining = 'Charging / No Battery'
    else:
        time_remaining = (
            f'{str(round(psutil.sensors_battery().secsleft / 3600, 2))} hrs'
        )

    return {
        'percent': int(power_data.percent),
        'time_remaining': time_remaining,
        'power_source': 'AC Power'
        if power_data.power_plugged
        else 'Battery Power',
    }

def get_user_info():
    user_data = psutil.users()
    return {
        count: {
            'name': user.name,
            'terminal': user.terminal,
            'host': user.host,
            'started': datetime.fromtimestamp(user.started),
            'pid': user.pid,
        }
        for count, user in enumerate(user_data)
    }

def get_memory_info():
    vmemory_data = psutil.virtual_memory()
    smemory_data = psutil.swap_memory()

    return {
        'svmem_total': bytes2human(vmemory_data.total),
        'svem_percent': vmemory_data.percent,
        'smem_total': bytes2human(smemory_data.total),
        'smem_percent': smemory_data.percent,
    }

def get_disks_info():
    disk_data = {}
    disk_partitions = psutil.disk_partitions(all=False)
    for counter,partition in enumerate(disk_partitions):
        try:
            usage_data = psutil.disk_usage(partition.mountpoint)
        except Exception as e:
            logger.error(f"Couldn't read disk : {partition.mountpoint} \nError: {e}")
            continue
        disk_data[counter] = {
            'device': partition.device,
            'mounted': partition.mountpoint,
            'total': bytes2human(usage_data.total),
            'used':bytes2human(usage_data.used),
            'free':bytes2human(usage_data.free),
        }
    return disk_data

def get_network_info():
    network_data = {}
    if_addrs = psutil.net_if_addrs()
    io_counter = psutil.net_io_counters(pernic=True)

    for interface_name, interface_addresses in if_addrs.items():
        for address in interface_addresses:
            if int(address.family) == 2:
                if interface_name in io_counter:
                    io = io_counter[interface_name]
                    network_data[interface_name] = {
                        'name': interface_name,
                        'ip_address': address.address,
                        'sent_bytes': bytes2human(io.bytes_sent),
                        'received_bytes': bytes2human(io.bytes_recv),
                    }

    return network_data