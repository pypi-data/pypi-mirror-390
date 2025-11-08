import os
import socket
import platform
import webbrowser
import urllib.request
import tempfile
import subprocess
from typing import Optional

NPCAP_URL = "https://npcap.com/dist/npcap-1.84.exe"

# ---------- Network Helpers ----------

def get_active_network_interface() -> Optional[str]:
    """
    Return the interface name used for outbound traffic, or None on failure.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
    except Exception:
        return None

    try:
        import psutil
        for iface, addrs in psutil.net_if_addrs().items():
            for a in addrs:
                if getattr(a, "family", None) == socket.AF_INET and a.address == local_ip:
                    return iface
    except Exception:
        pass

    return None


# ---------- Npcap Helpers ----------

def _exists_in_system_dirs(filenames):
    """Search common system dirs for any of these filenames."""
    paths = []
    if platform.system() == "Windows":
        win = os.environ.get("WINDIR", r"C:\Windows")
        paths.extend([os.path.join(win, "System32"), os.path.join(win, "SysWOW64")])
    else:
        paths.extend(["/usr/lib", "/usr/local/lib"])
    for d in paths:
        for f in filenames:
            if os.path.exists(os.path.join(d, f)):
                return True
    return False


def is_npcap_installed() -> bool:
    """
    Best-effort detection for Npcap/WinPcap.
    Checks DLLs on Windows or libpcap on *nix.
    """
    sysname = platform.system()
    if sysname == "Windows":
        return _exists_in_system_dirs(["wpcap.dll", "Packet.dll", "NpcapShim.dll"])
    else:
        return _exists_in_system_dirs(["libpcap.so", "libpcap.dylib", "libpcap.so.1"])


def open_npcap_install_page():
    """Open the official Npcap download page."""
    url = "https://nmap.org/npcap/"
    try:
        webbrowser.open(url, new=2)
    except Exception:
        print("Please visit:", url)


# ---------- Installer Functions ----------

def download_npcap_installer(dest_path=None):
    """
    Download the official Npcap installer (npcap-1.84.exe) to temp or custom path.
    Returns the path of the downloaded file, or None on error.
    """
    if platform.system() != "Windows":
        raise OSError("Npcap installer is only for Windows.")

    if dest_path is None:
        dest_path = os.path.join(tempfile.gettempdir(), "npcap-1.84.exe")

    print(f"Downloading Npcap installer to: {dest_path}")
    try:
        urllib.request.urlretrieve(NPCAP_URL, dest_path)
        print("✅ Download complete.")
        return dest_path
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None


def run_npcap_installer(installer_path):
    """
    Ask the user before running the Npcap installer (.exe).
    """
    if not os.path.exists(installer_path):
        print("Installer not found:", installer_path)
        return False

    confirm = input("Run Npcap installer now? (y/N): ").strip().lower()
    if confirm == "y":
        try:
            print("Launching installer...")
            subprocess.Popen([installer_path], shell=True)
            return True
        except Exception as e:
            print(f"❌ Could not start installer: {e}")
            return False
    else:
        print("Installer saved at:", installer_path)
        return False


def install_npcap_interactive():
    """
    Helper that downloads and (optionally) runs the Npcap installer.
    """
    installer = download_npcap_installer()
    if installer:
        run_npcap_installer(installer)
