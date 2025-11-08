from collections import Counter
from typing import Optional
import pyperclip

# scapy imports are lazy to avoid import-time crashes for users who
# only want utils functions (or install partially).
def sniff_for_server(timeout: int = 30) -> Optional[str]:
    """
    Sniff UDP packets and return an IP:PORT string of a candidate Rocket League server.
    The heuristic: capture UDP dst ports in the typical Rocket League range and return the
    first endpoint seen at least twice.

    Returns:
        "ip:port" string or None on timeout/failure.
    """
    try:
        from scapy.all import sniff, IP, UDP
    except Exception:
        raise RuntimeError("scapy is required for sniffing (install scapy via pip)")

    RL_UDP_PORTS = range(7000, 9000)
    seen = Counter()
    best_ipport = None

    def callback(pkt):
        nonlocal best_ipport
        if IP in pkt and UDP in pkt:
            dst_ip = pkt[IP].dst
            dst_port = pkt[UDP].dport
            if dst_port in RL_UDP_PORTS:
                key = f"{dst_ip}:{dst_port}"
                seen[key] += 1
                # require seeing address twice to reduce false positives
                if seen[key] >= 2:
                    best_ipport = key
                    try:
                        pyperclip.copy(best_ipport)
                    except Exception:
                        pass
                    # don't return True (scapy stop_filter reads the packet object),
                    # we rely on stop_filter to observe best_ipport captured
                    return

    try:
        sniff(prn=callback, store=False, timeout=timeout, stop_filter=lambda x: best_ipport is not None)
    except PermissionError:
        raise RuntimeError("Insufficient permissions to sniff packets. Run as admin/root.")
    except Exception as e:
        # bubble up helpful message
        raise RuntimeError(f"Sniff error: {e}")

    return best_ipport
