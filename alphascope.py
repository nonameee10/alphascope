import os
import json
import logging
from typing import List, Dict

try:
    import winreg
except ImportError:
    raise ImportError("This script requires a Windows environment to run.")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scan_registry_keys(paths: List[str]) -> Dict[str, List[str]]:
    """Scan specified registry paths for potential privacy leaks."""
    leaks = {}
    for path in paths:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey_path = os.path.join(path, subkey_name)
                        leaks.setdefault(path, []).append(subkey_path)
                        i += 1
                    except OSError:
                        break
        except FileNotFoundError:
            logging.warning(f"Registry path not found: {path}")
    return leaks

def scan_file_system(paths: List[str]) -> List[str]:
    """Scan specified file system paths for potential privacy leaks."""
    leaks = []
    for path in paths:
        if os.path.exists(path):
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith('.log') or file.endswith('.tmp'):
                        leaks.append(os.path.join(root, file))
        else:
            logging.warning(f"File system path not found: {path}")
    return leaks

def analyze_privacy_settings() -> Dict[str, bool]:
    """Analyze Windows privacy settings for potential privacy leaks."""
    # Example: Check if telemetry is enabled
    telemetry_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\DataCollection"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, telemetry_path) as key:
            telemetry_enabled, _ = winreg.QueryValueEx(key, "AllowTelemetry")
            return {"Telemetry Enabled": telemetry_enabled != 0}
    except FileNotFoundError:
        logging.warning("Telemetry settings not found.")
        return {"Telemetry Enabled": False}

def main():
    registry_paths = [
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
    ]
    file_system_paths = [
        r"C:\Users\Public\Documents",
        r"C:\ProgramData",
    ]

    logging.info("Starting AlphaScope analysis...")

    registry_leaks = scan_registry_keys(registry_paths)
    file_system_leaks = scan_file_system(file_system_paths)
    privacy_settings = analyze_privacy_settings()

    result = {
        "Registry Leaks": registry_leaks,
        "File System Leaks": file_system_leaks,
        "Privacy Settings": privacy_settings
    }

    with open("alphascope_report.json", "w") as report_file:
        json.dump(result, report_file, indent=4)

    logging.info("AlphaScope analysis completed. Report generated: alphascope_report.json")

if __name__ == "__main__":
    main()