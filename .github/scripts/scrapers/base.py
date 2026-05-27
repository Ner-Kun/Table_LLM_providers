from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Iterable, Mapping, Optional, Tuple
import httpx
from rich.console import Console

console = Console()

PricingMap = Dict[str, Dict[str, Any]]
MetadataMap = Dict[str, Dict[str, Any]]


class BasePricingScraper(ABC):
    """Base scraper with common HTTP, error handling, and result formatting.

    Subclasses implement scrape() and return normalized model pricing plus
    optional metadata.

    Returns:
        {
            "badge": "Provider prices",
            "source_url": "https://...",
            "reliability": "high" | "unstable",
            "fetched_at": "2026-05-23T12:00:00+00:00",
            "models": {
                "model-id": {
                    "input": 0.1,    # $/1M prompt tokens
                    "output": 0.15,  # $/1M completion tokens
                    "cache": 0.01,   # optional $/1M cache read
                }
            },
            "metadata": {
                "model-id": { ... }
            }
        }
    """

    RELIABILITY: ClassVar[str] = "high"
    BADGE: ClassVar[str] = "Live data"
    SOURCE_URL: ClassVar[Optional[str]] = None
    TIMEOUT: ClassVar[int] = 20
    HEADERS: ClassVar[Mapping[str, str]] = {"User-Agent": "Mozilla/5.0"}

    async def fetch_pricing(self) -> Optional[Dict[str, Any]]:
        try:
            models, metadata = await self.scrape()
            if not models:
                return None
            return self.build_result(models, metadata)
        except Exception as e:
            console.print(f"[bold red]ERR[/] {self.provider_label} pricing fetch failed: {e}")
            return None

    @abstractmethod
    async def scrape(self) -> Tuple[PricingMap, Optional[MetadataMap]]:
        """Return normalized pricing and optional metadata."""

    @property
    def provider_label(self) -> str:
        name = type(self).__name__
        return name[:-7] if name.endswith("Scraper") else name

    @property
    def badge_text(self) -> str:
        return self.BADGE

    @property
    def source_url(self) -> str:
        return self.SOURCE_URL or ""

    def build_result(
        self,
        models: PricingMap,
        metadata: Optional[MetadataMap] = None,
    ) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "badge": self.badge_text,
            "source_url": self.source_url,
            "reliability": self.RELIABILITY,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "models": models,
        }
        if metadata is not None:
            result["metadata"] = metadata
        return result

    async def get_json(
        self,
        url: str,
        *,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Any:
        resp = await self.get(url, headers=headers, timeout=timeout)
        return resp.json()

    async def get_text(
        self,
        url: str,
        *,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> str:
        resp = await self.get(url, headers=headers, timeout=timeout)
        return resp.text

    async def get(
        self,
        url: str,
        *,
        headers: Optional[Mapping[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> httpx.Response:
        async with httpx.AsyncClient(timeout=timeout or self.TIMEOUT) as client:
            resp = await client.get(url, headers=self.request_headers(headers))
            resp.raise_for_status()
            return resp

    def request_headers(self, extra: Optional[Mapping[str, str]] = None) -> Dict[str, str]:
        headers = dict(self.HEADERS)
        if extra:
            headers.update(extra)
        return headers

    @staticmethod
    def compact_dict(values: Mapping[str, Any]) -> Dict[str, Any]:
        return {key: value for key, value in values.items() if value is not None}

    @staticmethod
    def first_present(source: Mapping[str, Any], keys: Iterable[str]) -> Any:
        for key in keys:
            value = source.get(key)
            if value is not None:
                return value
        return None

    @staticmethod
    def as_number(value: Any) -> Optional[float]:
        if value is None or isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return value
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @classmethod
    def cents_per_million_to_usd(cls, value: Any) -> Optional[float]:
        number = cls.as_number(value)
        return number / 100 if number is not None else None

    @classmethod
    def per_token_to_per_million(cls, value: Any) -> Optional[float]:
        number = cls.as_number(value)
        return number * 1_000_000 if number is not None else None

    @staticmethod
    def add_limit(meta: Dict[str, Any], *, context: Any = None, output: Any = None) -> None:
        if context is None and output is None:
            return
        limit = meta.setdefault("limit", {})
        if context is not None:
            limit["context"] = context
        if output is not None:
            limit["output"] = output

    @staticmethod
    def add_modalities(
        meta: Dict[str, Any],
        *,
        input_modalities: Optional[list] = None,
        output_modalities: Optional[list] = None,
        default_output: bool = True,
    ) -> None:
        if not input_modalities and not output_modalities:
            return

        modalities: Dict[str, Any] = {}
        if input_modalities:
            modalities["input"] = input_modalities
        if output_modalities:
            modalities["output"] = output_modalities
        elif default_output:
            modalities["output"] = ["text"]
        meta["modalities"] = modalities
