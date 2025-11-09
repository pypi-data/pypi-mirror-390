# spiders/stealth/vpn_manager.py
"""
VPN helper for StealthSpider.

Currently supports NordVPN via the `nordvpn` CLI.
The manager:
 - can switch NordVPN "technology" to openvpn when required for obfuscation,
 - enable obfuscation,
 - attempt connect/disconnect with retries and timeouts,
 - queries the current connection state.

This is intentionally conservative in side-effects and logs clearly.
"""

import subprocess
import shlex
import time
from typing import Optional
import logging

logger = logging.getLogger("vpn_manager")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[VPN] %(message)s"))
    logger.addHandler(ch)


class VPNError(Exception):
    pass


class VPNManager:
    def __init__(self, provider: str = "nordvpn"):
        self.provider = provider.lower()
        if self.provider != "nordvpn":
            raise VPNError("Only 'nordvpn' provider is implemented in this manager.")
        self._last_region = None

    def _run(self, cmd: str, timeout: int = 15) -> str:
        logger.debug(f"Running: {cmd}")
        parts = shlex.split(cmd)
        try:
            out = subprocess.check_output(parts, stderr=subprocess.STDOUT, timeout=timeout)
            return out.decode("utf-8", errors="replace")
        except subprocess.CalledProcessError as e:
            logger.debug(f"Cmd failed ({cmd}): {e.output.decode(errors='replace')}")
            raise VPNError(f"Command failed: {cmd}\n{e.output.decode(errors='replace')}")
        except subprocess.TimeoutExpired as e:
            logger.debug(f"Cmd timeout ({cmd})")
            raise VPNError(f"Command timeout: {cmd}")

    # ---------- NordVPN-specific helpers ----------
    def _nordvpn_status(self) -> str:
        return self._run("nordvpn status", timeout=6)

    def _is_connected(self) -> bool:
        try:
            out = self._nordvpn_status().lower()
            return "connected" in out
        except Exception:
            return False

    def _current_country(self) -> Optional[str]:
        try:
            out = self._nordvpn_status()
            # Status output contains "Country: Hong Kong" or "City: ..."
            for line in out.splitlines():
                if line.lower().startswith("country:"):
                    return line.split(":", 1)[1].strip().lower().replace(" ", "_")
        except Exception:
            return None

    def ensure_openvpn_for_obfuscation(self) -> None:
        """
        NordVPN disallows `obfuscate on` unless technology is set to openvpn.
        Switch to openvpn if needed.
        """
        try:
            tech_out = self._run("nordvpn settings")
            # quick check: if technology is already OpenVPN, bail
            if "Technology: OpenVPN" in tech_out or "technology: OpenVPN".lower() in tech_out.lower():
                logger.debug("NordVPN technology already OpenVPN.")
                return
        except Exception:
            # settings might vary; attempt to set openvpn anyway
            logger.debug("Could not read nordvpn settings; proceeding to set technology to openvpn.")

        logger.info("Setting NordVPN technology to OpenVPN (required for obfuscation).")
        try:
            self._run("nordvpn set technology openvpn", timeout=6)
        except Exception as e:
            logger.warning(f"Could not set technology to openvpn: {e}")

    def set_obfuscation(self, value: bool) -> None:
        val = "on" if value else "off"
        logger.info(f"Setting obfuscation: {val}")
        try:
            self._run(f"nordvpn set obfuscate {val}", timeout=6)
        except VPNError as e:
            # surfacing helpful message
            msg = str(e)
            if "not available" in msg or "not installed" in msg.lower():
                logger.warning("Obfuscation not supported with current settings/provider.")
            else:
                logger.warning(f"Failed to set obfuscation: {e}")

    def set_protocol(self, protocol: str) -> None:
        protocol = protocol.lower()
        if protocol not in ("tcp", "udp"):
            raise VPNError("protocol must be 'tcp' or 'udp'")
        logger.info(f"Setting NordVPN protocol to {protocol}")
        try:
            self._run(f"nordvpn set protocol {protocol}", timeout=6)
        except Exception as e:
            logger.warning(f"Failed to set protocol: {e}")

    def connect(self, region: str, obfuscate: bool = True, protocol: str = "tcp", timeout: int = 30) -> None:
        """
        Connect to provider's region. Uses retries and attempts to enable obfuscation if requested.
        """
        region = region.replace(" ", "_")
        self._last_region = region

        # ensure protocol + obfuscation readiness
        if obfuscate:
            # NordVPN requires openvpn tech for obfuscation
            try:
                self.ensure_openvpn_for_obfuscation()
            except Exception:
                logger.debug("ensure_openvpn_for_obfuscation had an issue, continuing.")

        # set protocol
        try:
            self.set_protocol(protocol)
        except Exception:
            logger.debug("set_protocol failed; continuing.")

        # enable obfuscation if requested
        if obfuscate:
            try:
                self.set_obfuscation(True)
            except Exception:
                logger.debug("set_obfuscation failed; continuing.")

        # attempt connect with retries
        last_err = None
        for attempt in range(1, 1 + 2):
            try:
                logger.info(f"Attempting VPN connection to: {region} (attempt {attempt})")
                out = self._run(f"nordvpn connect {region}", timeout=timeout)
                logger.info(out.strip().splitlines()[-1] if out else "Connected (no output)")
                # confirm connected
                start = time.time()
                while time.time() - start < (timeout if timeout else 30):
                    if self._is_connected():
                        logger.info(f"VPN connected to {region}")
                        return
                    time.sleep(1)
                raise VPNError("Connection attempt timed out")
            except VPNError as e:
                last_err = e
                logger.warning(f"Connect attempt failed: {e}")
                # try a fallback: turn obfuscation off and try TCP again if obfuscate was on
                if obfuscate:
                    try:
                        logger.info("Falling back: disabling obfuscation and retrying.")
                        self.set_obfuscation(False)
                    except Exception:
                        pass
                time.sleep(1)

        raise VPNError(f"Failed to connect to VPN {region}. Last error: {last_err}")

    def disconnect(self, timeout: int = 10) -> None:
        """
        Disconnect vpn client.
        """
        if not self._is_connected():
            logger.info("VPN already disconnected.")
            return
        logger.info("Disconnecting VPN...")
        try:
            out = self._run("nordvpn disconnect", timeout=timeout)
            logger.info("Disconnected.")
            # small wait to ensure new interface state
            time.sleep(1)
        except Exception as e:
            logger.warning(f"Failed to cleanly disconnect VPN: {e}")

    def running_provider(self) -> str:
        return self.provider

    def last_region(self) -> Optional[str]:
        return self._last_region
