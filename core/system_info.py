import platform
from pathlib import Path
import psutil

def collect_system_metrics():
    memory = psutil.virtual_memory()
    disk_root = Path.home().anchor or "/"
    disk = psutil.disk_usage(disk_root)
    try:
        connections = len(psutil.net_connections(kind="inet"))
    except (psutil.AccessDenied, OSError):
        connections = 0
    return {
        "hostname": platform.node(),
        "platform": f"{platform.system()} {platform.release()}",
        "cpu_percent": psutil.cpu_percent(interval=None),
        "memory_percent": memory.percent,
        "disk_percent": disk.percent,
        "process_count": len(psutil.pids()),
        "connection_count": connections,
    }
