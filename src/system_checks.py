import psutil
import platform
import datetime

def get_uptime():
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    now = datetime.datetime.now()
    return str(now - boot_time)

def get_top_processes(limit=5):
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            processes.append(proc.info)
        except:
            pass
    processes = sorted(processes, key=lambda p: p['cpu_percent'], reverse=True)
    return processes[:limit]

def run_system_checks():
    return {
        "os": platform.platform(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory()._asdict(),
        "disk": psutil.disk_usage('/')._asdict(),
        "uptime": get_uptime(),
        "top_processes": get_top_processes()
    }
