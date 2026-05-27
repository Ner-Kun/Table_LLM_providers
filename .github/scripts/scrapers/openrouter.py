from typing import Any, Dict, Optional
from .base import BasePricingScraper, MetadataMap, PricingMap


class OpenRouterScraper(BasePricingScraper):
    """Fetch enriched pricing and metadata from OpenRouter /api/v1/models.

    OpenRouter returns per-token prices as strings; multiply by 1_000_000
    to get $/1M tokens.
    """

    RELIABILITY = "high"
    BADGE = "Live data"
    API_URL = "https://openrouter.ai/api/v1/models"
    SOURCE_URL = API_URL
    HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

    async def scrape(self) -> tuple[PricingMap, Optional[MetadataMap]]:
        data = await self.get_json(self.API_URL)
        models: PricingMap = {}
        metadata: MetadataMap = {}

        for model in data.get("data", []):
            model_id = model.get("id")
            if not model_id:
                continue

            models[model_id] = self.normalize_pricing(model)
            meta = self.normalize_metadata(model)
            if meta:
                metadata[model_id] = meta

        return models, metadata

    def normalize_pricing(self, model: Dict[str, Any]) -> Dict[str, Any]:
        pricing = model.get("pricing", {})

        return self.compact_dict(
            {
                "input": self.per_token_to_per_million(pricing.get("prompt")),
                "output": self.per_token_to_per_million(pricing.get("completion")),
                "cache_read": self.per_token_to_per_million(pricing.get("input_cache_read")),
                "cache_write": self.per_token_to_per_million(pricing.get("input_cache_write")),
                "web_search": self.per_token_to_per_million(pricing.get("web_search")),
            }
        )

    def normalize_metadata(self, model: Dict[str, Any]) -> Dict[str, Any]:
        meta: Dict[str, Any] = {}

        top_provider = model.get("top_provider", {})
        self.add_limit(
            meta,
            context=model.get("context_length"),
            output=top_provider.get("max_completion_tokens"),
        )

        architecture = model.get("architecture", {})
        self.add_modalities(
            meta,
            input_modalities=architecture.get("input_modalities"),
            output_modalities=architecture.get("output_modalities"),
        )

        pricing = model.get("pricing", {})
        supported = set(model.get("supported_parameters", []))
        if "reasoning" in supported or "include_reasoning" in supported:
            meta["reasoning"] = True
        if "tools" in supported or "tool_choice" in supported:
            meta["tool_call"] = True
        if "temperature" in supported:
            meta["temperature"] = True
        if "web_search" in pricing:
            meta["supports_web_search"] = True

        return meta
