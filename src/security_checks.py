import subprocess
import psutil
import json

def get_defender_status():
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-MpComputerStatus | ConvertTo-Json"],
            capture_output=True, text=True
        )
        data = result.stdout

        if not data:
            return {"error": "Unable to read Defender status"}

        # Convert JSON string to Python dict
        import json
        status = json.loads(data)

        return {
            "real_time_protection": status.get("RealTimeProtectionEnabled"),
            "antispyware_enabled": status.get("AntispywareEnabled"),
            "antivirus_enabled": status.get("AntivirusEnabled"),
            "behavior_monitor_enabled": status.get("BehaviorMonitorEnabled"),
            "full_scan_age": status.get("FullScanAge"),
            "quick_scan_age": status.get("QuickScanAge"),
            "definition_status": status.get("AMServiceEnabled")
        }

    except Exception as e:
        return {"error": str(e)}

SUSPICIOUS_KEYWORDS = [
    "mimikatz", "nc.exe", "powershell.exe -enc", "meterpreter", "cobalt"
]

def get_failed_logins():
    try:
        # Query Windows Security Log for failed login attempts (Event ID 4625)
        command = [
            "powershell",
            "-Command",
            "Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625} -MaxEvents 20 | "
            "Select-Object TimeCreated, Message | ConvertTo-Json"
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if not result.stdout:
            return {"error": "No data returned"}

        data = json.loads(result.stdout)

        # Normalize single object vs list
        if isinstance(data, dict):
            data = [data]

        failed_attempts = []
        for entry in data:
            failed_attempts.append({
                "time": entry.get("TimeCreated"),
                "message": entry.get("Message")
            })

        return failed_attempts

    except Exception as e:
        return {"error": str(e)}
    
def get_account_lockouts():
    try:
        command = [
            "powershell",
            "-Command",
            "Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4740} -MaxEvents 10 | "
            "Select-Object TimeCreated, Message | ConvertTo-Json"
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if not result.stdout:
            return []

        data = json.loads(result.stdout)

        if isinstance(data, dict):
            data = [data]

        lockouts = []
        for entry in data:
            lockouts.append({
                "time": entry.get("TimeCreated"),
                "message": entry.get("Message")
            })

        return lockouts

    except Exception as e:
        return {"error": str(e)}


def check_firewall():
    result = subprocess.run(
        ["netsh", "advfirewall", "show", "allprofiles"],
        capture_output=True, text=True
    )
    return "ON" in result.stdout

def detect_suspicious_processes():
    flagged = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmd = " ".join(proc.info['cmdline']).lower()
            for keyword in SUSPICIOUS_KEYWORDS:
                if keyword in cmd:
                    flagged.append(proc.info)
        except:
            pass
    return flagged

def run_security_checks():
    return {
        "firewall_enabled": check_firewall(),
        "suspicious_processes": detect_suspicious_processes(),
        "defender_status": get_defender_status(),
        "failed_logins": get_failed_logins(),
        "account_lockouts": get_account_lockouts()
    }


