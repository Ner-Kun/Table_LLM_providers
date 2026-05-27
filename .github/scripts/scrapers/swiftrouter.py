import json
import re
from typing import Any, Dict, Optional
from .base import BasePricingScraper, MetadataMap, PricingMap


class SwiftRouterScraper(BasePricingScraper):
    """Fetches pricing by scraping the JS bundle from swiftrouter.com/models.
    """

    RELIABILITY = "unstable"
    BADGE = "Live data (verify)"
    SOURCE_URL: str = "https://swiftrouter.com/models"
    BASE_URL = "https://swiftrouter.com"
    BUNDLE_RE = re.compile(r'<script[^\u003e]*src="(/assets/index-[^"]+\.js)"')
    JSON_PARSE_RE = re.compile(r"JSON\.parse\('([^']+)'\)")

    async def scrape(self) -> tuple[PricingMap, Optional[MetadataMap]]:
        data = await self.fetch_bundle_models()
        models: PricingMap = {}
        metadata: MetadataMap = {}

        for model in data:
            model_id = model.get("id")
            if not model_id:
                continue

            models[model_id] = self.normalize_pricing(model)
            meta = self.normalize_metadata(model)
            if meta:
                metadata[model_id] = meta

        return models, metadata

    async def fetch_bundle_models(self) -> list[Dict[str, Any]]:
        html = await self.get_text(self.SOURCE_URL)
        js_path = self.extract_js_path(html)
        js = await self.get_text(f"{self.BASE_URL}{js_path}")
        return self.extract_models_from_bundle(js)

    def extract_js_path(self, html: str) -> str:
        match = self.BUNDLE_RE.search(html)
        if not match:
            raise ValueError("JS bundle path not found in HTML")
        return match.group(1)

    def extract_models_from_bundle(self, js: str) -> list[Dict[str, Any]]:
        json_match = self.JSON_PARSE_RE.search(js)
        if not json_match:
            raise ValueError("JSON.parse data not found in JS bundle")

        data = json.loads(json_match.group(1))
        if not isinstance(data, list):
            raise ValueError("JSON.parse payload is not a model list")
        return [model for model in data if isinstance(model, dict)]

    def normalize_pricing(self, model: Dict[str, Any]) -> Dict[str, Any]:
        return self.compact_dict(
            {
                "input": self.as_number(model.get("prompt_price_per_1m")),
                "output": self.as_number(model.get("completion_price_per_1m")),
                "cache": self.as_number(model.get("cache_price_per_1m")),
            }
        )

    def normalize_metadata(self, model: Dict[str, Any]) -> Dict[str, Any]:
        discount = model.get("discount")
        meta = self.compact_dict(
            {
                "featured": True if model.get("featured") else None,
                "discount": discount if isinstance(discount, dict) else None,
                "tool_call": True if model.get("supports_tools") else None,
                "reasoning": True if model.get("supports_reasoning") else None,
                "code_specialized": True if model.get("code_specialized") else None,
                "supports_web_search": True if model.get("supports_web_search") else None,
            }
        )

        self.add_limit(
            meta,
            context=model.get("context_length"),
            output=model.get("max_completion_tokens"),
        )
        self.add_modalities(meta, input_modalities=model.get("input_modalities"))
        return meta
