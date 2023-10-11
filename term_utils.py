# Copyright (C) 2023-present by FlaskUtilityServer@Github, < https://github.com/StarkGang >.
#
# This file is part of < https://github.com/Starkgang/FlaskUtilityServer > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/Starkgang/FlaskUtilityServer/blob/main/LICENSE >
#
# All rights reserved.

import requests
from config import CONFIG
import psutil

class UTILS:
    def __init__(self) -> None:
        self.weather_api_url =  "http://api.weatherapi.com/v1/current.json"
        self.weather_api_key = CONFIG.WEATHER_API_KEY

    def neofetch(self):
        cpu_info = f"CPU: {psutil.cpu_percent(interval=1)}% utilization"
        mem_info = psutil.virtual_memory()
        mem_info_str = f"Memory: {mem_info.percent}% used ({round(mem_info.used / (1024 ** 3), 2)} GB used of {round(mem_info.total / (1024 ** 3), 2)} GB)"
        disk_info = psutil.disk_usage('/')
        disk_info_str = f"Disk: {disk_info.percent}% used ({round(disk_info.used / (1024 ** 3), 2)} GB used of {round(disk_info.total / (1024 ** 3), 2)} GB)"
        net_info = psutil.net_if_addrs()
        net_info_str = "Network:"
        for interface, addresses in net_info.items():
            for address in addresses:
                if address.family == psutil.AF_LINK:
                    net_info_str += f"\n  {interface}: {address.address}"
        return f"Neofetch Information:\n{cpu_info}\n{mem_info_str}\n{disk_info_str}\n{net_info_str}"

    def get_weather(self, city):
        out = ""
        params = {'key': self.weather_api_key, 'q': city}
        response = requests.get(self.weather_api_url, params=params)
        data = response.json()
        if response.status_code == 200:
            out += f"""Weather Details for {data['location']['name']}, {data['location']['country']}:\n
Temperature: {data.get('current').get('temp_c')}°C
Feels Like: {data.get('current').get('feelslike_c')}°C
Condition: {data.get('current').get('condition').get('text')}
Wind Speed: {data.get('current').get('wind_kph')} km/h
Wind Direction: {data.get('current').get('wind_dir')}
Condition: {data.get('current').get('condition').get('text')}
Humidity: {data.get('current').get('humidity')}%
Cloud: {data.get('current').get('cloud')}%"""
        else:
            out += f"Error: {data['error']['message']}"
        return out


