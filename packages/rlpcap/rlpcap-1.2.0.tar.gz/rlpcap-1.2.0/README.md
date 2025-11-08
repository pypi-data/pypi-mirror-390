# 🚀 RLPCAP

**RLPCAP** — A lightweight Rocket League packet sniffer for discovering in-game server IP addresses.  
Designed for simplicity, speed, and easy customization.

---

## 📦 Installation

> Requires **Python 3.8+** and **Npcap** (Windows) or **libpcap** (Linux/macOS).
`pip install rlpcap`

---

## Example of Usage
```py
from rlpcap.sniffer import sniff_for_server, IP, PORT, IPPORT

result = sniff_for_server()
if result:
    print(f"Server IP: {IP}")
    print(f"Port: {PORT}")
    print(f"Full Address: {IPPORT}")
```
**Output**

```yaml
Server IP: 3.144.53.113
Port: 7804
Full Address: 3.144.53.113:7804
```