import json
import datetime
import os
import csv

def write_csv(path, headers, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

def generate_report(system, security, network, csv_only=False, html_only=False, json_only=False):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder = f"reports/{timestamp}"
    os.makedirs(folder, exist_ok=True)

    # -------------------------
    # JSON REPORT
    # -------------------------
    if not html_only and not csv_only:
        with open(f"{folder}/report.json", "w") as f:
            json.dump({
                "system": system,
                "security": security,
                "network": network
            }, f, indent=4)

    # -------------------------
    # HTML REPORT
    # -------------------------
    if not json_only and not csv_only:
        html = f"""
        <html>
        <head>
            <title>System Health Report</title>
            <style>
                body {{ font-family: Arial; padding: 20px; }}
                h1 {{ color: #333; }}
                pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>System Health & Security Report</h1>

            <h2>System</h2>
            <pre>{json.dumps(system, indent=4)}</pre>

            <h2>Security</h2>
            <pre>{json.dumps(security, indent=4)}</pre>

            <h2>Network</h2>
            <pre>{json.dumps(network, indent=4)}</pre>
        </body>
        </html>
        """

        with open(f"{folder}/report.html", "w", encoding="utf-8") as f:
            f.write(html)

    # -------------------------
    # CSV EXPORTS
    # -------------------------
    if not html_only and not json_only:

        # Top processes
        processes = system.get("top_processes", []) if system else []
        if processes:
            write_csv(
                f"{folder}/processes.csv",
                headers=["pid", "name", "cpu_percent"],
                rows=processes
            )

        # Open ports
        ports = network.get("open_ports", []) if network else []
        if ports:
            write_csv(
                f"{folder}/open_ports.csv",
                headers=["port", "service"],
                rows=ports
            )

        # Network adapters
        adapters = []
        if network and "network_adapters" in network:
            for name, info in network["network_adapters"].items():
                adapters.append({
                    "adapter": name,
                    "ipv4": info.get("ipv4"),
                    "mac": info.get("mac")
                })

        if adapters:
            write_csv(
                f"{folder}/network_adapters.csv",
                headers=["adapter", "ipv4", "mac"],
                rows=adapters
            )

    return folder
