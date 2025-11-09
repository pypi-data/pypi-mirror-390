import asyncio
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import aiohttp
from bs4 import BeautifulSoup

_LOGGER = logging.getLogger("wellandcanalbridges")


BRIDGE_PAGES: Dict[str, str] = {
    "BridgeSCT": "https://seaway-greatlakes.com/bridgestatus/detailsnai?key=BridgeSCT",
    "BridgePC": "https://seaway-greatlakes.com/bridgestatus/detailsnai?key=BridgePC",
}

STATUS_CODE_MAP: Dict[str, int] = {
    "available": 1,
    "raising soon": 2,
    "raised": 3,
    "unavailable": 4,
}

CACHE_TTL = timedelta(seconds=60)
MAX_FAILURE_DURATION = timedelta(minutes=5)

@dataclass
class CacheEntry:
    data: Optional[List[Dict[str, str]]] = None
    fetched_at: Optional[datetime] = None
    failure_started: Optional[datetime] = None


class WellandCanalBridges:
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        """Initialize the bridge status client."""

        self._session = session or aiohttp.ClientSession()
        self._owns_session = session is None
        now = datetime.utcnow()
        self._cache: Dict[str, CacheEntry] = {}
        for key in BRIDGE_PAGES:
            self._cache[key] = CacheEntry()
        self._locks: Dict[str, asyncio.Lock] = {
            key: asyncio.Lock() for key in BRIDGE_PAGES
        }
        self._last_updated: Optional[datetime] = None
        _LOGGER.debug("WellandCanalBridges client initialized at %s", now.isoformat())

    async def close(self) -> None:
        """Close the underlying HTTP session if owned."""

        if self._owns_session and not self._session.closed:
            await self._session.close()

    async def get_bridge_status(self, bridge_id: Optional[str] = None) -> Dict[str, List[Dict[str, str]]]:
        """Return the bridge status payload.

        If bridge_id is provided, only the matching bridge entry is returned.
        """

        bridges: List[Dict[str, str]] = []

        for page_key, page_url in BRIDGE_PAGES.items():
            page_data, fetched_at = await self._ensure_page_data(page_key, page_url)
            for bridge in page_data:
                bridge_copy = dict(bridge)
                bridge_copy["last_updated"] = fetched_at.isoformat() if fetched_at else None
                bridges.append(bridge_copy)

        if bridge_id is not None:
            target = str(bridge_id).lower()
            if not target.startswith("bridge_"):
                target = f"bridge_{target}"
            bridges = [bridge for bridge in bridges if bridge["id"].lower() == target]

        return {"bridges": bridges}

    async def _ensure_page_data(
        self, page_key: str, page_url: str
    ) -> Tuple[List[Dict[str, str]], Optional[datetime]]:
        """Return cached data, refreshing as needed with resiliency rules."""

        async with self._locks[page_key]:
            cache_entry = self._cache[page_key]
            now = datetime.utcnow()

            if cache_entry.failure_started and now - cache_entry.failure_started > MAX_FAILURE_DURATION:
                raise RuntimeError(
                    f"Bridge status data for {page_key} unavailable for more than {MAX_FAILURE_DURATION}."
                )

            data_available = cache_entry.data is not None
            cache_age = (
                now - cache_entry.fetched_at
                if cache_entry.fetched_at is not None
                else None
            )

            should_fetch = (
                not data_available
                or (cache_age is not None and cache_age >= CACHE_TTL)
                or cache_entry.failure_started is not None
            )

            if should_fetch:
                fetch_success = await self._fetch_and_update_cache(page_key, page_url)
                if not fetch_success:
                    if not data_available:
                        raise RuntimeError(f"Unable to retrieve bridge status data for {page_key}.")
                    if cache_entry.failure_started is None:
                        cache_entry.failure_started = now
                    elif now - cache_entry.failure_started > MAX_FAILURE_DURATION:
                        raise RuntimeError(
                            f"Bridge status data for {page_key} unavailable for more than {MAX_FAILURE_DURATION}."
                        )

            data = cache_entry.data or []
            return data, cache_entry.fetched_at

    async def _fetch_and_update_cache(self, page_key: str, page_url: str) -> bool:
        """Fetch a page and update cache entry. Returns True on success."""

        cache_entry = self._cache[page_key]
        try:
            async with self._session.get(page_url) as response:
                response.raise_for_status()
                html = await response.text()
        except Exception as exc:  # noqa: BLE001
            _LOGGER.warning("Failed to fetch %s: %s", page_key, exc)
            return False

        try:
            bridges = self._parse_bridge_page(html)
        except Exception as exc:  # noqa: BLE001
            _LOGGER.error("Failed to parse bridge data for %s: %s", page_key, exc)
            return False

        now = datetime.utcnow()
        cache_entry.data = bridges
        cache_entry.fetched_at = now
        cache_entry.failure_started = None
        self._last_updated = now
        return True

    @staticmethod
    def _parse_bridge_page(html: str) -> List[Dict[str, str]]:
        """Parse bridge entries from the HTML payload."""

        soup = BeautifulSoup(html, "html.parser")
        bridge_tables = soup.find_all(id="grey_box")
        bridges: List[Dict[str, str]] = []

        for table in bridge_tables:
            name_element = table.find("span", class_="lgtextblack")
            status_element = table.find("span", id="status")

            if name_element is None or status_element is None:
                continue

            full_name = name_element.get_text(strip=True)
            status_text = status_element.get_text(strip=True)
            name, nickname = WellandCanalBridges._extract_name_and_nickname(full_name)
            status_code = WellandCanalBridges._determine_status_code(status_text)

            bridges.append(
                {
                    "id": nickname.replace(" ", "_").lower(),
                    "name": name,
                    "nickname": nickname,
                    "status": status_text,
                    "status_code": status_code,
                }
            )

        return bridges

    @staticmethod
    def _extract_name_and_nickname(full_name: str) -> (str, str):
        """Split the full bridge name into name and nickname."""

        match = re.match(r"^(?P<name>.*?)\s*\((?P<nickname>Bridge[^)]*)\)$", full_name)
        if not match:
            _LOGGER.warning("Unable to parse bridge nickname from '%s'", full_name)
            cleaned = full_name.strip()
            return cleaned, cleaned

        return match.group("name").strip(), match.group("nickname").strip()

    @staticmethod
    def _determine_status_code(status_text: str) -> int:
        """Map textual status into a numeric status code."""

        normalized_text = status_text.lower()
        if "raising soon" in normalized_text:
            return STATUS_CODE_MAP["raising soon"]
        if "raised" in normalized_text:
            return STATUS_CODE_MAP["raised"]
        if "unavailable" in normalized_text and "raising" in normalized_text:
            return STATUS_CODE_MAP["raised"]

        base_status = status_text.split("(")[0].strip().lower()
        status_code = STATUS_CODE_MAP.get(base_status)
        if status_code is None:
            _LOGGER.warning("Unknown bridge status '%s', defaulting to 'Unavailable'", status_text)
            status_code = STATUS_CODE_MAP["unavailable"]
        return status_code
