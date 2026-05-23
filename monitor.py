import os
import time
import json
import requests
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

DELAY = 300

def run(cmd):
    try:
        return subprocess.check_output(
            cmd,
            shell=True
        ).decode().strip()
    except:
        return "Unknown"

def get_device():
    brand = run("getprop ro.product.brand")
    model = run("getprop ro.product.model")
    android = run("getprop ro.build.version.release")

    return f"{brand} {model} (Android {android})"

def get_cpu():
    cpu = run("cat /proc/cpuinfo | grep 'Hardware' | head -n 1")

    if cpu == "":
        cpu = run("cat /proc/cpuinfo | grep 'model name' | head -n 1")

    return cpu

def get_gpu():
    gpu = run("getprop ro.hardware.egl")

    if gpu == "":
        gpu = run("getprop ro.board.platform")

    return gpu

def get_ram():
    try:
        meminfo = open('/proc/meminfo').read()

        total = int(meminfo.split('MemTotal:')[1].split('\n')[0].split()[0]) // 1024
        avail = int(meminfo.split('MemAvailable:')[1].split('\n')[0].split()[0]) // 1024

        used = total - avail

        return f"{used}MB / {total}MB"

    except:
        return "Unknown"

def get_storage():
    try:
        stat = os.statvfs('/sdcard')

        total = (stat.f_blocks * stat.f_frsize) / (1024 ** 3)
        free = (stat.f_bavail * stat.f_frsize) / (1024 ** 3)

        used = total - free

        return f"{used:.1f}GB / {total:.1f}GB"

    except:
        return "Unknown"

def get_battery():
    try:
        data = json.loads(run("termux-battery-status"))

        percent = data.get("percentage", "Unknown")
        temp = data.get("temperature", "Unknown")
        status = data.get("status", "Unknown")

        return percent, temp, status

    except:
        return "Unknown", "Unknown", "Unknown"

def get_ip():
    return run("curl -s ifconfig.me")

def get_uptime():
    try:
        uptime = open('/proc/uptime').read().split()[0]

        uptime = int(float(uptime))

        hours = uptime // 3600
        minutes = (uptime % 3600) // 60

        return f"{hours}h {minutes}m"

    except:
        return "Unknown"

def screenshot():
    os.system("screencap -p /sdcard/screen.png")

while True:

    percent, temp, status = get_battery()

    now = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")

    caption = f'''
====== THÔNG BÁO THIẾT BỊ ======

🕒 Thời gian:
{now}

📱 Tên thiết bị:
{get_device()}

🧠 CPU:
{get_cpu()}

🎮 GPU:
{get_gpu()}

💾 RAM:
{get_ram()}

📂 Bộ nhớ:
{get_storage()}

🔋 Pin:
{percent}% ({status})

🌡️ Nhiệt độ:
{temp}°C

🌐 IP Public:
{get_ip()}

⏳ Uptime:
{get_uptime()}

============ HẾT ============
'''

    screenshot()

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    try:

        with open("/sdcard/screen.png", "rb") as img:

            requests.post(
                url,
                data={
                    "chat_id": CHAT_ID,
                    "caption": caption
                },
                files={
                    "photo": img
                }
            )

        print("[OK] Đã gửi trạng thái")

    except Exception as e:
        print("[ERROR]", e)

    time.sleep(DELAY)