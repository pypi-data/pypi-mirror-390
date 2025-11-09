# spiders/stealth/stealth_config.py
# Configuration defaults for StealthSpider / VPN behavior.

DEFAULT_VPN_PROVIDER = "nordvpn"
DEFAULT_REGION = "hong_kong"
REQUIRE_VPN_DEFAULT = True

# Behavior toggles
DISCONNECT_BEFORE_LLM = True      # Disconnect VPN before making LLM API calls (recommended)
RECONNECT_AFTER_LLM = False       # Reconnect VPN after LLM calls (optional)
OBFUSCATE_BY_DEFAULT = True       # Try to enable obfuscation if provider supports it
PROTOCOL_DEFAULT = "tcp"          # prefer tcp for stealthy behaviour (OpenVPN over TCP/443)
CONNECT_TIMEOUT = 30              # seconds to wait for VPN connect
DISCONNECT_TIMEOUT = 10           # seconds to wait for VPN disconnect
MAX_CONNECT_RETRIES = 2
