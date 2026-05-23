import os
import time
import json
import shutil
import socket
import requests
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DELAY = int(os.getenv("DELAY", "200"))

SCREEN_PATH = os.path.expanduser("~/screen.png")


def run(cmd):
    try:
        return subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.DEVNULL,
            timeout=10
        ).decode(errors="ignore").strip()
    except:
        return "Unknown"


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=20)
        print("[SEND MESSAGE]", r.text)
        return r.ok
    except Exception as e:
        print("[ERROR SEND MESSAGE]", e)
        return False


def send_photo(caption):
    if not os.path.exists(SCREEN_PATH):
        print("[WARN] Không thấy ảnh chụp màn hình")
        send_message("⚠️ Không chụp được màn hình, gửi trạng thái dạng text.")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    try:
        with open(SCREEN_PATH, "rb") as img:
            r = requests.post(
                url,
                data={"chat_id": CHAT_ID, "caption": caption},
                files={"photo": img},
                timeout=60
            )

        print("[SEND PHOTO]", r.text)
        return r.ok

    except Exception as e:
        print("[ERROR SEND PHOTO]", e)
        return False


def get_device():
    brand = run("getprop ro.product.brand")
    model = run("getprop ro.product.model")
    android = run("getprop ro.build.version.release")
    sdk = run("getprop ro.build.version.sdk")
    return f"{brand} {model} | Android {android} SDK {sdk}"


def get_cpu():
    hardware = run("grep -m1 'Hardware' /proc/cpuinfo | cut -d ':' -f2")
    processor = run("grep -m1 'Processor' /proc/cpuinfo | cut -d ':' -f2")
    chipset = run("getprop ro.board.platform")

    if hardware != "Unknown" and hardware:
        return hardware.strip()
    if processor != "Unknown" and processor:
        return processor.strip()
    return chipset


def get_gpu():
    gpu = run("getprop ro.hardware.egl")
    if gpu == "Unknown" or not gpu:
        gpu = run("getprop ro.board.platform")
    return gpu


def get_ram():
    try:
        meminfo = open("/proc/meminfo").read()
        total = int(meminfo.split("MemTotal:")[1].split("\n")[0].split()[0]) // 1024
        avail = int(meminfo.split("MemAvailable:")[1].split("\n")[0].split()[0]) // 1024
        used = total - avail
        percent = used * 100 / total
        return f"{used}MB / {total}MB ({percent:.1f}%)"
    except:
        return "Unknown"


def get_storage():
    try:
        path = "/sdcard" if os.path.exists("/sdcard") else os.path.expanduser("~")
        total, used, free = shutil.disk_usage(path)
        total_gb = total / 1024**3
        used_gb = used / 1024**3
        free_gb = free / 1024**3
        return f"{used_gb:.1f}GB / {total_gb:.1f}GB | Trống {free_gb:.1f}GB"
    except:
        return "Unknown"


def get_battery():
    try:
        data = json.loads(run("termux-battery-status"))
        percent = data.get("percentage", "Unknown")
        temp = data.get("temperature", "Unknown")
        status = data.get("status", "Unknown")
        health = data.get("health", "Unknown")
        plugged = data.get("plugged", "Unknown")
        return f"{percent}% | {status} | {health} | Sạc: {plugged}", f"{temp}°C"
    except:
        return "Unknown", "Unknown"


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return run("ip route get 8.8.8.8 | awk '{print $7; exit}'")


def get_public_ip():
    ip = run("curl -s --max-time 8 ifconfig.me")
    return ip if ip else "Unknown"


def get_uptime():
    try:
        uptime = int(float(open("/proc/uptime").read().split()[0]))
        days = uptime // 86400
        hours = (uptime % 86400) // 3600
        minutes = (uptime % 3600) // 60
        return f"{days}d {hours}h {minutes}m"
    except:
        return "Unknown"


def get_load():
    try:
        return open("/proc/loadavg").read().strip()
    except:
        return "Unknown"


def screenshot():
    print("[INFO] Đang chụp màn hình...")
    os.system(f"screencap -p {SCREEN_PATH}")
    return os.path.exists(SCREEN_PATH)


def build_report():
    battery, temp = get_battery()
    now = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")

    return f"""====== THÔNG BÁO THIẾT BỊ ======

🕒 Thời gian:
{now}

📱 Tên thiết bị:
{get_device()}

🧠 CPU:
{get_cpu()}

🎮 GPU:
{get_gpu()}

📊 Load:
{get_load()}

💾 RAM:
{get_ram()}

📂 Bộ nhớ:
{get_storage()}

🔋 Pin:
{battery}

🌡️ Nhiệt độ:
{temp}

🌐 IP Local:
{get_local_ip()}

🌍 IP Public:
{get_public_ip()}

⏳ Uptime:
{get_uptime()}

🔁 Chu kỳ gửi:
{DELAY} giây

============ HẾT ============"""


def check_config():
    if not BOT_TOKEN or not CHAT_ID:
        print("[ERROR] Thiếu BOT_TOKEN hoặc CHAT_ID trong .env")
        exit()

    if ":" not in BOT_TOKEN:
        print("[ERROR] BOT_TOKEN sai format, token Telegram phải có dấu ':'")
        exit()


print("===================================")
print(" Android Monitor Bot đang khởi động ")
print("===================================")

send_message("✅ Android Monitor đã khởi động thành công!")

while True:
    print("[INFO] Đang lấy thông tin thiết bị...")
    check_config()

    report = build_report()
    ok_screen = screenshot()

    if ok_screen:
        send_photo(report)
    else:
        send_message(report)

    print(f"[OK] Xong. Đợi {DELAY} giây...")
    time.sleep(DELAY)