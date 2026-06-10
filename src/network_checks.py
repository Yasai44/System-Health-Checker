import psutil
import socket
import subprocess



def get_network_adapters():
    adapters = {}

    for interface, addrs in psutil.net_if_addrs().items():
        adapter_info = {
            "ipv4": None,
            "mac": None
        }

        for addr in addrs:
            if addr.family == socket.AF_INET:
                adapter_info["ipv4"] = addr.address
            elif addr.family == psutil.AF_LINK:
                adapter_info["mac"] = addr.address

        adapters[interface] = adapter_info

    return adapters

def get_gateway_and_dns():
    try:
        # Default gateway
        gateways = psutil.net_if_stats()
        gws = psutil.net_if_addrs()

        # DNS servers (Windows)
        result = subprocess.run(
            ["powershell", "-Command", "Get-DnsClientServerAddress | ConvertTo-Json"],
            capture_output=True, text=True
        )

        import json
        dns_data = json.loads(result.stdout)

        dns_servers = []
        if isinstance(dns_data, list):
            for entry in dns_data:
                if entry.get("ServerAddresses"):
                    dns_servers.extend(entry["ServerAddresses"])

        return {
            "dns_servers": dns_servers
        }

    except Exception as e:
        return {"error": str(e)}


def ping_test(host="8.8.8.8"):
    try:
        result = subprocess.run(
            ["ping", "-n", "1", host],
            capture_output=True, text=True
        )
        return "TTL=" in result.stdout
    except:
        return False

def dns_resolution_test(domain="google.com"):
    try:
        socket.gethostbyname(domain)
        return True
    except:
        return False

def run_network_checks(target_ip=None):
    return {
        "ping_google_dns": ping_test(),
        "dns_resolution": dns_resolution_test(),
        "open_ports": scan_ports(target_ip) if target_ip else scan_ports(),
        "network_adapters": get_network_adapters(),
        "dns_info": get_gateway_and_dns()
    }

COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    135: "RPC",
    139: "NetBIOS",
    143: "IMAP",
    389: "LDAP",
    443: "HTTPS",
    445: "SMB",
    587: "SMTP TLS",
    3306: "MySQL",
    3389: "RDP",
    8080: "HTTP Proxy"
}


def scan_ports(target_ip="127.0.0.1"):
    common_ports = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        135: "RPC",
        139: "NetBIOS",
        143: "IMAP",
        443: "HTTPS",
        445: "SMB",
        3306: "MySQL",
        3389: "RDP",
        8080: "HTTP-ALT"
    }

    open_ports = []

    for port, service in common_ports.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((target_ip, port))
            if result == 0:
                open_ports.append({"port": port, "service": service})
            sock.close()
        except:
            pass

    return open_ports
