"""rlpcap — Rocket League packet helper package."""
__version__ = "0.1.0"

from .sniffer import sniff_for_server
from .utils import get_active_network_interface, is_npcap_installed, open_npcap_install_page
