import customtkinter as ctk
import os
import threading

from system_checks import run_system_checks
from security_checks import run_security_checks
from network_checks import run_network_checks
from report_generator import generate_report


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("System Health & Security Checker")
        self.geometry("750x550")

        # Title
        self.label = ctk.CTkLabel(self, text="System Health Checker", font=("Arial", 26))
        self.label.pack(pady=15)

        # IP Entry
        self.scan_ip_entry = ctk.CTkEntry(self, placeholder_text="Scan IP (optional)", width=320)
        self.scan_ip_entry.pack(pady=10)

        # Run Button
        self.run_button = ctk.CTkButton(self, text="Run Checks", command=self.start_checks_thread)
        self.run_button.pack(pady=10)

        # Progress Bar
        self.progress = ctk.CTkProgressBar(self, width=500)
        self.progress.pack(pady=10)
        self.progress.set(0)

        # Output Box
        self.output_box = ctk.CTkTextbox(self, width=650, height=300)
        self.output_box.pack(pady=10)

        # Open Folder Button (hidden until report is generated)
        self.open_button = ctk.CTkButton(self, text="Open Report Folder", command=self.open_folder)
        self.open_button.pack(pady=5)
        self.open_button.configure(state="disabled")

        self.report_folder = None

    # Run checks in a separate thread so GUI doesn't freeze
    def start_checks_thread(self):
        thread = threading.Thread(target=self.run_checks)
        thread.start()

    def run_checks(self):
        self.output_box.delete("1.0", "end")
        self.output_box.insert("end", "Running checks...\n\n")
        self.progress.set(0.05)

        ip = self.scan_ip_entry.get().strip()
        ip = ip if ip else None

        # System checks
        self.output_box.insert("end", "Running system checks...\n")
        self.output_box.update()
        system = run_system_checks()
        self.progress.set(0.35)

        # Security checks
        self.output_box.insert("end", "Running security checks...\n")
        self.output_box.update()
        security = run_security_checks()
        self.progress.set(0.65)

        # Network checks
        self.output_box.insert("end", "Running network checks...\n")
        self.output_box.update()
        network = run_network_checks(target_ip=ip)
        self.progress.set(0.85)

        # Save report
        self.output_box.insert("end", "\nGenerating report...\n")
        self.output_box.update()
        folder = generate_report(system, security, network)
        self.report_folder = os.path.abspath(folder)


        self.progress.set(1.0)

        # Display results
        self.output_box.insert("end", "\n✔ System checks complete\n")
        self.output_box.insert("end", "✔ Security checks complete\n")
        self.output_box.insert("end", "✔ Network checks complete\n\n")
        self.output_box.insert("end", f"Report saved to:\n{folder}\n")

        # Enable "Open Folder" button
        self.open_button.configure(state="normal")

    def open_folder(self):
        if self.report_folder and os.path.exists(self.report_folder):
            os.startfile(self.report_folder)


if __name__ == "__main__":
    app = App()
    app.mainloop()
