from collections import Counter
from typing import Optional
import pyperclip

# module-level vars people can use
IP = None
PORT = None
IPPORT = None

def sniff_for_server(timeout: int = 30) -> Optional[dict]:
    """
    Sniff Rocket League UDP traffic and extract the server IP:PORT.
    Returns a dict with keys: IP, PORT, IPPORT.
    Also sets rlpcap.IP, rlpcap.PORT, rlpcap.IPPORT for quick global access.
    """
    global IP, PORT, IPPORT

    try:
        from scapy.all import sniff, IP as IPLayer, UDP
    except Exception:
        raise RuntimeError("Scapy is required. Run: pip install scapy")

    from rlpcap.utils import get_active_network_interface, is_process_running

    RL_UDP_PORTS = range(7000, 9000)
    seen = Counter()
    iface = get_active_network_interface()

    if not iface or not is_process_running("rocketleague.exe"):
        return None

    result = None

    def callback(pkt):
        nonlocal result
        if IPLayer in pkt and UDP in pkt:
            dst_ip = pkt[IPLayer].dst
            dst_port = pkt[UDP].dport
            if dst_port in RL_UDP_PORTS:
                key = f"{dst_ip}:{dst_port}"
                seen[key] += 1
                if seen[key] >= 2:
                    result = {"IP": dst_ip, "PORT": str(dst_port), "IPPORT": key}
                    try:
                        pyperclip.copy(key)
                    except Exception:
                        pass

    try:
        sniff(prn=callback, store=False, timeout=timeout, stop_filter=lambda _: result is not None)
    except PermissionError:
        raise RuntimeError("Run this script as admin/root.")
    except Exception as e:
        raise RuntimeError(f"Sniff error: {e}")

    if result:
        IP = result["IP"]
        PORT = result["PORT"]
        IPPORT = result["IPPORT"]

    return result
