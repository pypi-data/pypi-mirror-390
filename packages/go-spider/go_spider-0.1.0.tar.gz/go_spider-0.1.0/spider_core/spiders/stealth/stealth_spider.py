"""
StealthSpider: extends BasicSpider to perform fetches while routing
page loads through a VPN (NordVPN CLI). Important LLM calls will be
performed after disconnecting the VPN so they originate from your normal IP.

Assumptions:
 - NordVPN CLI is installed and accessible as `nordvpn`.
 - VPNManager in spiders.stealth.vpn_manager supports connect(region, obfuscate, protocol)
   and disconnect() and raises VPNError when appropriate.
"""

import asyncio
import logging
from typing import Optional

from spider_core.spiders.basic_spider import BasicSpider
from spider_core.spiders.stealth.vpn_manager import VPNManager, VPNError
from spider_core.spiders.stealth.stealth_config import (
    DEFAULT_REGION,
    DEFAULT_VPN_PROVIDER,
    REQUIRE_VPN_DEFAULT,
    DISCONNECT_BEFORE_LLM,
    RECONNECT_AFTER_LLM,
    OBFUSCATE_BY_DEFAULT,
    PROTOCOL_DEFAULT,
)

logger = logging.getLogger("stealth_spider")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[StealthSpider] %(message)s"))
    logger.addHandler(ch)


async def maybe_await(result):
    if asyncio.iscoroutine(result):
        return await result
    return result


class StealthSpider(BasicSpider):
    def __init__(
        self,
        browser_client,
        relevance_ranker,
        chunker,
        vpn_provider: str = DEFAULT_VPN_PROVIDER,
        region: str = DEFAULT_REGION,
        require_vpn: bool = REQUIRE_VPN_DEFAULT,
        disconnect_before_llm: bool = DISCONNECT_BEFORE_LLM,
        reconnect_after_llm: bool = RECONNECT_AFTER_LLM,
        obfuscate: bool = OBFUSCATE_BY_DEFAULT,
        protocol: str = PROTOCOL_DEFAULT,
    ):
        super().__init__(browser_client, relevance_ranker, chunker)
        self.vpn_provider = vpn_provider
        self.region = region
        self.require_vpn = require_vpn
        self.disconnect_before_llm = disconnect_before_llm
        self.reconnect_after_llm = reconnect_after_llm
        self.obfuscate = obfuscate
        self.protocol = protocol
        self.vpn = VPNManager(provider=vpn_provider)

    async def _ensure_vpn(self):
        if self.require_vpn:
            logger.info(f"Enforcing VPN for region: {self.region}")
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    lambda: self.vpn.connect(self.region, obfuscate=self.obfuscate, protocol=self.protocol),
                )
            except Exception as e:
                logger.error(f"Failed to establish VPN connection: {e}")
                raise VPNError(str(e))
            logger.info("VPN connected")
        else:
            logger.info("VPN not required for this fetch (require_vpn=False).")

    async def _teardown_vpn_before_llm(self):
        if self.disconnect_before_llm:
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.vpn.disconnect)
                logger.info("VPN disconnected before LLM calls as configured.")
            except Exception as e:
                logger.warning(f"Failed to disconnect VPN before LLM calls: {e}")
        else:
            logger.info("Configured to NOT disconnect before LLM calls.")

    async def _reconnect_vpn_after_llm_if_needed(self):
        if self.reconnect_after_llm and self.require_vpn:
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    lambda: self.vpn.connect(self.region, obfuscate=self.obfuscate, protocol=self.protocol),
                )
                logger.info("VPN reconnected after LLM calls.")
            except Exception as e:
                logger.warning(f"Failed to reconnect VPN after LLM calls: {e}")

    async def fetch(self, url: str):
        """
        Override pipeline to:
         - ensure VPN connected (if required)
         - render + deterministic extraction + chunking (no LLM)
         - disconnect VPN (optional) before LLM
         - run LLM-based scoring
         - optionally reconnect VPN
        """
        # 1) ensure vpn
        try:
            await self._ensure_vpn()
        except VPNError:
            if self.require_vpn:
                raise RuntimeError("StealthSpider: unable to establish VPN and VPN is required.")
            else:
                logger.warning("Could not establish VPN but continuing because require_vpn is False.")

        logger.info(f"Fetching: {url} using VPN (if connected).")

        # 2) Use BasicSpider helper to fetch without LLM (render/extract/chunk)
        try:
            page_result = await self._fetch_without_llm(url)
        except Exception as e:
            logger.warning(f"Failed to build PageResult using BasicSpider helper: {e}")
            # re-raise — we choose failure since fetch couldn't render/extract
            raise

        # 3) Disconnect VPN before doing LLM calls (if configured)
        await self._teardown_vpn_before_llm()

        # 4) Now call BasicSpider's scoring routine (which will call the LLM via ranker)
        try:
            await self._score_links_with_llm(page_result)
        except Exception as e:
            logger.warning(f"LLM ranking failed: {e}")

        # 5) Reconnect VPN after LLM if configured
        await self._reconnect_vpn_after_llm_if_needed()

        return page_result
