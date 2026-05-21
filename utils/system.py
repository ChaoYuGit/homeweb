import platform
import shutil
from datetime import datetime

import psutil


def get_system_info():
    cpu_percent = psutil.cpu_percent(interval=0.5)
    cpu_count = psutil.cpu_count()
    mem = psutil.virtual_memory()
    disk = shutil.disk_usage("/")
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    now = datetime.now()
    uptime_delta = now - boot_time
    days = uptime_delta.days
    hours, remainder = divmod(uptime_delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    net = psutil.net_io_counters()

    return {
        "cpu_percent": cpu_percent,
        "cpu_count": cpu_count,
        "memory_total": mem.total,
        "memory_used": mem.used,
        "memory_percent": mem.percent,
        "disk_total": disk.total,
        "disk_used": disk.used,
        "disk_free": disk.free,
        "disk_percent": round(disk.used / disk.total * 100, 1),
        "uptime_days": days,
        "uptime_hours": hours,
        "uptime_minutes": minutes,
        "net_bytes_sent": net.bytes_sent,
        "net_bytes_recv": net.bytes_recv,
        "hostname": platform.node(),
    }
