from system_checks import run_system_checks
from security_checks import run_security_checks
from network_checks import run_network_checks
from report_generator import generate_report
from rich.console import Console
from rich.panel import Panel
import argparse


console = Console()

def main():
    parser = argparse.ArgumentParser(
        description="System Health & Security Checker"
    )

    # CLI flags
    parser.add_argument("--no-system", action="store_true", help="Skip system checks")
    parser.add_argument("--no-security", action="store_true", help="Skip security checks")
    parser.add_argument("--no-network", action="store_true", help="Skip network checks")
    parser.add_argument("--csv-only", action="store_true", help="Generate only CSV reports")
    parser.add_argument("--html-only", action="store_true", help="Generate only HTML report")
    parser.add_argument("--json-only", action="store_true", help="Generate only JSON report")
    parser.add_argument("--quiet", action="store_true", help="Suppress CLI output")
    parser.add_argument("--scan", type=str, help="Scan ports on a specific IP address")

    # GUI flag
    parser.add_argument("--gui", action="store_true", help="Launch the GUI")

    args = parser.parse_args()

    #GUI
    if args.gui:
        from gui import App
        app = App()
        app.mainloop()
        return

    # Normal CLI mode
    if not args.quiet:
        console.print(Panel("[bold cyan]System Health & Security Checker[/bold cyan]"))

    system = security = network = None

    # System checks
    if not args.no_system:
        if not args.quiet:
            console.print("[yellow]Running system checks...[/yellow]")
        system = run_system_checks()

    # Security checks
    if not args.no_security:
        if not args.quiet:
            console.print("[yellow]Running security checks...[/yellow]")
        security = run_security_checks()

    # Network checks
    if not args.no_network:
        if not args.quiet:
            console.print("[yellow]Running network checks...[/yellow]")
        network = run_network_checks(target_ip=args.scan)

    # Generate report
    if not args.quiet:
        console.print("[green]Generating report...[/green]")

    folder = generate_report(
        system=system,
        security=security,
        network=network,
        csv_only=args.csv_only,
        html_only=args.html_only,
        json_only=args.json_only
    )

    if not args.quiet:
        console.print(Panel(f"[bold green]Report saved to:[/bold green] {folder}"))


if __name__ == "__main__":
    main()
