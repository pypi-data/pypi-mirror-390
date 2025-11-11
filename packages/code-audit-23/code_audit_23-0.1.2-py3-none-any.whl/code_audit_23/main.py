import os
import subprocess
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

# Allow running both as package and script
if __package__ is None or __package__ == "":
    # Running as script (e.g. python main.py)
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from logger import logger
    from sonarqube_cli import run_sonarqube_scan
    from trivy_cli import run_trivy_scan
else:
    # Running as installed package
    from .logger import logger
    from .sonarqube_cli import run_sonarqube_scan
    from .trivy_cli import run_trivy_scan

# Load environment variables from .env file
load_dotenv()

# Default SonarQube configuration
SONAR_HOST_URL = os.getenv("SONAR_HOST_URL", "https://sonarqube.brainstation-23.xyz")
SONAR_LOGIN = os.getenv("SONAR_LOGIN", "sqa_eb118830887767100489ecfc4b55e42a134bf2cb")


def ensure_reports_dir():
    """Ensure the reports directory exists"""
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    return reports_dir


def get_sonarqube_credentials():
    """Prompt user for SonarQube credentials if not in environment"""
    click.echo(
        click.style("\n🔑 SonarQube Configuration Required", fg="yellow", bold=True)
    )
    click.echo(click.style("-" * 40, fg="bright_black"))
    sonar_url = click.prompt(
        click.style(
            "Enter SonarQube URL (e.g., http://localhost:9000)", fg="bright_cyan"
        ),
        type=str,
    )
    sonar_token = click.prompt(
        click.style("Enter SonarQube Token (will be hidden)", fg="bright_cyan"),
        hide_input=True,
    )
    click.echo(click.style("✅ Credentials saved for this session\n", fg="green"))
    return sonar_url, sonar_token


def show_welcome_banner():
    """Display welcome banner with ASCII art"""
    banner = """
     ██████╗ ██████╗ ██████╗ ███████╗    █████╗ ██╗   ██╗██████╗ ██╗████████╗    ██████╗ ██████╗ 
    ██╔════╝██╔═══██╗██╔══██╗██╔════╝   ██╔══██╗██║   ██║██╔══██╗██║╚══██╔══╝    ╚════██╗╚════██╗
    ██║     ██║   ██║██║  ██║█████╗     ███████║██║   ██║██║  ██║██║   ██║        █████╔╝ █████╔╝
    ██║     ██║   ██║██║  ██║██╔══╝     ██╔══██║██║   ██║██║  ██║██║   ██║       ██╔═══╝  ╚═══██╗
    ╚██████╗╚██████╔╝██████╔╝███████╗   ██║  ██║╚██████╔╝██████╔╝██║   ██║      ███████╗██████╔╝
     ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝   ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝      ╚══════╝╚═════╝ 
    """
    click.echo(click.style(banner, fg="bright_cyan"))
    click.echo(
        click.style(
            " " * 25 + "🚀  Code Quality & Security Scanner  🚀\n",
            fg="bright_white",
            bold=True,
        )
    )
    click.echo(click.style(" " * 30 + "Version 1.0.0\n", fg="bright_black"))

    # Ensure reports directory exists
    ensure_reports_dir()


def show_menu():
    """Display main interactive menu"""
    click.echo(click.style("\n" + "═" * 80, fg="bright_blue"))
    click.echo(
        click.style(
            " " * 22 + "🔍  CODE AUDIT 23 MENU  🔍", fg="bright_cyan", bold=True
        )
    )
    click.echo(click.style("═" * 80 + "\n", fg="bright_blue"))

    menu_items = [
        (
            "1",
            "Quick Scan (SonarQube + Gitleaks + Trivy)",
            "Run all security scans in sequence",
        ),
        (
            "2",
            "Trivy Scan",
            "Scan for vulnerabilities in dependencies and container images",
        ),
        ("3", "SonarQube Scan", "Analyze code quality and security issues"),
        ("q", "Quit", "Exit the application"),
    ]

    for num, title, desc in menu_items:
        click.echo(
            click.style(f"  [{num}] ", fg="bright_green", bold=True)
            + click.style(f"{title}", fg="white", bold=True)
        )
        click.echo(click.style(f"      {desc}", fg="bright_black"))
        # click.echo()

    click.echo(click.style("─" * 80, fg="bright_blue"))


def prompt_choice():
    """Prompt user for menu selection with validation"""
    while True:
        choice = (
            click.prompt(
                click.style("\nSelect an option", fg="bright_yellow"),
                type=str,
                default="1",
                show_default=False,
            )
            .strip()
            .lower()
        )

        if choice in ["1", "2", "3", "4", "q", "quit"]:
            return choice
        click.echo(
            click.style(
                "❌ Invalid choice. Please select 1, 2, 3, or q to quit.", fg="red"
            )
        )


def main():
    """Interactive entrypoint for Audit Scanner"""
    # Clear screen and show welcome banner
    click.clear()
    show_welcome_banner()

    # Initialize SonarQube credentials
    global SONAR_HOST_URL, SONAR_LOGIN
    sonar_credentials_provided = bool(SONAR_HOST_URL and SONAR_LOGIN)

    while True:
        try:
            show_menu()
            choice = prompt_choice()
            # click.clear()

            # Handle quit option
            if choice.lower() in ["q", "quit"]:
                click.echo(
                    click.style(
                        "\n👋 Thank you for using Code Audit 23. Goodbye!\n",
                        fg="bright_blue",
                        bold=True,
                    )
                )
                break

            # Run Trivy scan for Quick Scan or Trivy only
            if choice in ["1", "2"]:
                if choice == "1":
                    click.echo("\n" + "─" * 80)
                report_path = "reports/trivy.sarif"
                click.echo(
                    click.style(
                        f"🔍 Starting Trivy Vulnerability Scan... (Report will be saved to {report_path})",
                        fg="bright_cyan",
                        bold=True,
                    )
                )
                # subprocess.run([
                #     "trivy",
                #     "repository",
                #     "--format", "sarif",
                #     "--output", report_path,
                #     "."
                # ], check=True)
                run_trivy_scan(report_path)
                if choice == "2":
                    click.echo(
                        click.style(
                            f"\n✅ Trivy Scan completed successfully! Report saved to {report_path}",
                            fg="bright_green",
                            bold=True,
                        )
                    )

            # Run SonarQube scan for Quick Scan or SonarQube only
            if choice in ["1", "3"]:
                if choice == "1":
                    click.echo("\n" + "─" * 80)
                click.echo(
                    click.style(
                        "🚀 Starting SonarQube Scan...", fg="bright_cyan", bold=True
                    )
                )
                try:
                    # Get credentials if not already provided
                    if not sonar_credentials_provided:
                        SONAR_HOST_URL, SONAR_LOGIN = get_sonarqube_credentials()
                        sonar_credentials_provided = True

                    run_sonarqube_scan(
                        sonar_url=SONAR_HOST_URL,
                        token=SONAR_LOGIN,
                        project_key=None,
                        sources=".",
                    )
                except Exception as e:
                    logger.error(f"SonarQube scan failed: {e}")
                    click.echo(
                        click.style(f"❌ SonarQube scan failed: {str(e)}", fg="red")
                    )
                    if click.confirm(
                        click.style(
                            "Do you want to update SonarQube credentials?", fg="yellow"
                        )
                    ):
                        sonar_url, sonar_token = get_sonarqube_credentials()
                        SONAR_HOST_URL = sonar_url
                        SONAR_LOGIN = sonar_token
                        # Retry the scan with new credentials
                        run_sonarqube_scan(
                            sonar_url=SONAR_HOST_URL,
                            token=SONAR_LOGIN,
                            project_key=None,
                            sources=".",
                        )
                if choice == "3":
                    click.echo(
                        click.style(
                            "\n✅ SonarQube Scan completed successfully!",
                            fg="bright_green",
                            bold=True,
                        )
                    )

            # Show completion message for Quick Scan
            if choice == "1":
                click.echo("\n" + "=" * 80)
                click.echo(
                    click.style(
                        "✅ Quick Scan completed successfully!",
                        fg="bright_green",
                        bold=True,
                    )
                )
                click.echo(click.style("=" * 80 + "\n", fg="bright_green"))

            # # Ask if user wants to perform another scan
            # click.echo("\n" + "─" * 80)
            # if not click.confirm(click.style("Would you like to perform another scan?", fg='bright_yellow')):
            #     click.echo(click.style("\n👋 Thank you for using Code Audit 23. Goodbye!\n", fg='bright_blue', bold=True))
            #     break

            # click.clear()
            # show_welcome_banner()

        except Exception as e:
            logger.error(f"Scan failed: {e}")
            click.echo(click.style("\n❌ An error occurred during the scan.", fg="red"))
            if not click.confirm(
                click.style("Would you like to try again?", fg="yellow")
            ):
                click.echo(
                    click.style(
                        "\n👋 Thank you for using Code Audit 23. Goodbye!\n",
                        fg="bright_blue",
                        bold=True,
                    )
                )
                break
            # click.clear()
            # show_welcome_banner()


if __name__ == "__main__":
    main()
