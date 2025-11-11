import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import tarfile
import time
import urllib.request
import zipfile
from pathlib import Path

import click

try:
    from .logger import logger
except ImportError:
    from logger import logger

# Cache folder for downloaded JRE
CACHE_DIR = Path.home() / ".audit_scan"
JRE_DIR = CACHE_DIR / "jre"
JRE_DIR.mkdir(parents=True, exist_ok=True)


def find_java():
    """Check system java or JAVA_HOME"""
    logger.debug("Looking for Java installation")
    java_path = shutil.which("java")
    if java_path:
        logger.debug(f"Found Java at: {java_path}")
        return java_path

    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        java_bin = Path(java_home) / "bin" / ("java.exe" if os.name == "nt" else "java")
        if java_bin.exists():
            logger.debug(f"Found Java in JAVA_HOME: {java_bin}")
            return str(java_bin)

    logger.warning("Java not found in PATH or JAVA_HOME")
    return None


def download_jre():
    """Download minimal JRE into cache folder"""
    system = platform.system().lower()
    dest = None

    # Get the machine architecture (e.g., 'x86_64', 'arm64')
    arch = platform.machine()
    os = (
        "macos"
        if system == "darwin"
        else ("windows" if system == "windows" else "linux")
    )
    ext = "zip" if system != "linux" else "tar.gz"
    zulu_url = f"https://api.azul.com/zulu/download/community/v1.0/bundles/latest?os={os}&arch={arch}&ext={ext}&bundle_type=jre&java_version=17"
    try:
        with urllib.request.urlopen(zulu_url) as r:
            data = json.load(r)
            url = data["url"]
    except Exception as exc:
        error_msg = f"Failed to fetch JRE metadata: {exc}"
        logger.exception(error_msg)
        raise RuntimeError(error_msg) from exc

    if "windows" in system:
        dest = CACHE_DIR / "jre.zip"
    elif "darwin" in system:
        dest = CACHE_DIR / "jre.zip"
    else:  # linux
        dest = CACHE_DIR / "jre.tar.gz"

    try:
        print(f"🌐 Downloading JRE from {url} ...")
        urllib.request.urlretrieve(url, dest)
    except Exception as exc:
        error_msg = f"Failed to download JRE archive: {exc}"
        logger.exception(error_msg)
        raise RuntimeError(error_msg) from exc

    try:
        # Extract
        if dest.suffix == ".zip":
            with zipfile.ZipFile(dest, "r") as zip_ref:
                zip_ref.extractall(JRE_DIR)
        else:
            with tarfile.open(dest, "r:gz") as tar_ref:
                tar_ref.extractall(JRE_DIR)
    except Exception as exc:
        error_msg = f"Failed to extract JRE archive: {exc}"
        logger.exception(error_msg)
        raise RuntimeError(error_msg) from exc
    finally:
        if dest.exists():
            try:
                dest.unlink()
            except Exception as unlink_exc:
                logger.warning(
                    f"Could not remove temporary JRE archive {dest}: {unlink_exc}"
                )

    # Ensure the extracted java binaries are executable (particularly for zip archives)
    try:
        for jre_root in sorted([d for d in JRE_DIR.iterdir() if d.is_dir()]):
            bin_dir = jre_root / "bin"
            if bin_dir.exists():
                for binary in bin_dir.iterdir():
                    if binary.is_file():
                        current_mode = binary.stat().st_mode
                        binary.chmod(
                            current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                        )
    except Exception as exc:
        error_msg = f"Failed to set executable permissions on JRE binaries: {exc}"
        logger.exception(error_msg)
        raise RuntimeError(error_msg) from exc

    print(f"✅ JRE installed to {JRE_DIR}")


def get_jre_bin():
    """Return path to java binary"""
    java_bin = find_java()
    if java_bin:
        return java_bin

    # Download and find inside extracted folder
    java_filename = "java.exe" if os.name == "nt" else "java"
    subdirs = [
        d
        for d in JRE_DIR.iterdir()
        if d.is_dir() and (d / "bin" / java_filename).exists()
    ]
    if not subdirs:
        download_jre()
        subdirs = [
            d
            for d in JRE_DIR.iterdir()
            if d.is_dir() and (d / "bin" / java_filename).exists()
        ]
    if not subdirs:
        raise RuntimeError("JRE download failed or empty.")
    java_bin = subdirs[0] / "bin" / java_filename
    if not java_bin.exists():
        raise RuntimeError(f"Java binary not found in {java_bin}")
    return str(java_bin)


def get_scanner_path():
    """Return path to sonar-scanner bundled folder"""
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent

    # Assume a 'sonar-scanner' folder is next to CLI
    scanner_bin = (
        base_path
        / "sonar-scanner"
        / "bin"
        / ("sonar-scanner.bat" if os.name == "nt" else "sonar-scanner")
    )
    if not scanner_bin.exists():
        raise FileNotFoundError(f"SonarScanner binary not found: {scanner_bin}")
    return scanner_bin


def run_sonarqube_scan(sonar_url, token, project_key, sources):
    project_root = Path(sources).resolve()
    if not project_root.exists():
        click.echo("❌ Source directory not found.")
        sys.exit(1)

    project_name = project_root.name
    project_key = project_key or project_name
    click.echo(f"🔍 Starting SonarQube scan for project: {project_key}")

    # Create temporary sonar-project.properties if not exists
    temp_props = None
    props_file = project_root / "sonar-project.properties"
    if not props_file.exists():
        temp_props = props_file
        temp_props.write_text(
            f"""
sonar.projectKey={project_key}
sonar.projectName={project_name}
sonar.sources={sources}
        """.strip()
        )
        click.echo("📝 Created temporary sonar-project.properties")

    # Get scanner and Java paths
    scanner_bin = get_scanner_path()
    java_bin = get_jre_bin()
    java_home = str(Path(java_bin).parent.parent)

    env = os.environ.copy()
    env["JAVA_HOME"] = java_home
    env["PATH"] = f"{Path(java_bin).parent}:{env.get('PATH', '')}"

    # # Ensure URL and token are properly formatted
    # sonar_url = sonar_url or SONAR_HOST_URL
    # token = token or SONAR_LOGIN

    # if not sonar_url or sonar_url == SONAR_HOST_URL:
    #     click.echo(f"⚠️  Using default SonarQube URL: {SONAR_HOST_URL}")
    if not token:
        error_msg = "No SonarQube token provided. Please set SONAR_LOGIN in your .env file or use --token"
        logger.error(error_msg)
        click.echo(f"❌ {error_msg}")
        sys.exit(1)

    env["SONAR_HOST_URL"] = sonar_url.rstrip("/")
    env["SONAR_TOKEN"] = token.strip()
    logger.debug("SonarQube configuration verified")

    # Prepare SARIF report paths
    reports_dir = project_root / "reports"

    # Check which report files exist
    report_files = [
        "gitleaks.sarif",
        "trivy.sarif",
        "bandit.sarif",
        "eslint.sarif",
        "checkov.sarif",
    ]

    # Find existing report files
    existing_reports = [f for f in report_files if (reports_dir / f).exists()]

    # Build sonar-scanner command
    scanner_cmd = [str(scanner_bin), "-Dsonar.verbose=false"]
    # scanner_cmd = [str(scanner_bin)]

    # Add SARIF reports if any exist
    if existing_reports:
        sarif_paths = [f"reports/{report}" for report in existing_reports]
        sarif_arg = "-Dsonar.sarifReportPaths=" + ",".join(sarif_paths)
        scanner_cmd.append(sarif_arg)
        click.echo(f"📊 Including SARIF reports: {', '.join(existing_reports)}")

    click.echo("🚀 Starting SonarScanner...")
    try:
        # Start the subprocess and stream logs in real-time
        process = subprocess.Popen(
            scanner_cmd,
            cwd=project_root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        click.echo("🔍 Scanning code (streaming Sonar logs)...")
        streamed_output = []
        assert process.stdout is not None
        for line in process.stdout:
            streamed_output.append(line)
            click.echo(line.rstrip())

        process.wait()

        # Check the return code
        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode, process.args, output="".join(streamed_output)
            )
        click.echo("✅ Sonar scan completed successfully!")
        click.echo(f"👉 View results: {sonar_url}/dashboard?id={project_key}")

    except subprocess.CalledProcessError as e:
        error_msg = f"Sonar scan failed with exit code {e.returncode}"
        logger.error(error_msg)
        click.echo("❌ Sonar scan failed!")
        click.echo(f"Exit code: {e.returncode}")
        sys.exit(1)

    except Exception as e:
        error_msg = f"Unexpected error during Sonar scan: {str(e)}"
        logger.exception(error_msg)
        click.echo(f"❌ {error_msg}")
        sys.exit(1)

    finally:
        if temp_props and temp_props.exists():
            temp_props.unlink()
            click.echo("🧹 Cleaned up temporary sonar-project.properties")
