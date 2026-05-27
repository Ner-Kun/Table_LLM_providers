import os
from typing import Any, Dict, Optional
from .base import BasePricingScraper, MetadataMap, PricingMap


class BaseApiPricingScraper(BasePricingScraper):
    """Reusable scraper for providers serving pricing in OpenAI-compatible format.

    Expects endpoints like /v1/models returning models with fields:
        - pricepermilliontokens / output_pricepermilliontokens
        - prompt_price_per_1m / completion_price_per_1m
    """

    RELIABILITY = "high"

    def __init__(self, base_url: str, badge: str, api_key_env: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self._badge_text = badge
        self.api_key_env = api_key_env

    @property
    def badge_text(self) -> str:
        return self._badge_text

    @property
    def source_url(self) -> str:
        return self.base_url

    async def scrape(self) -> tuple[PricingMap, Optional[MetadataMap]]:
        headers: Dict[str, str] = {}
        if self.api_key_env:
            key = os.environ.get(self.api_key_env, "")
            if key:
                headers["Authorization"] = f"Bearer {key}"

        for url in self.model_urls:
            try:
                data = await self.get_json(url, headers=headers, timeout=15)
                raw = self.extract_model_list(data)
                models = self.normalize_models(raw)
                if models:
                    return models, None
            except Exception:
                continue
        return {}, None

    @property
    def model_urls(self) -> list[str]:
        return [
            f"{self.base_url}/v1/models",
            f"{self.base_url}/models",
        ]

    @staticmethod
    def extract_model_list(data: Any) -> list[Dict[str, Any]]:
        if isinstance(data, list):
            return [model for model in data if isinstance(model, dict)]
        if isinstance(data, dict):
            raw = data.get("data")
            if raw is None:
                raw = data.get("models", [])
            if isinstance(raw, list):
                return [model for model in raw if isinstance(model, dict)]
        return []

    def normalize_models(self, raw: Any) -> PricingMap:
        models: PricingMap = {}
        for model in raw:
            model_id = model.get("id")
            if not model_id:
                continue

            prices = self.normalize_model_pricing(model)
            if prices:
                models[model_id] = prices
        return models

    def normalize_model_pricing(self, model: Dict[str, Any]) -> Dict[str, Any]:
        input_price = self.cents_per_million_to_usd(model.get("pricepermilliontokens"))
        output_price = self.cents_per_million_to_usd(model.get("output_pricepermilliontokens"))

        if input_price is None:
            input_price = self.as_number(model.get("prompt_price_per_1m"))
        if output_price is None:
            output_price = self.as_number(model.get("completion_price_per_1m"))
        if output_price is None:
            output_price = input_price

        return self.compact_dict(
            {
                "input": input_price,
                "output": output_price,
            }
        )
