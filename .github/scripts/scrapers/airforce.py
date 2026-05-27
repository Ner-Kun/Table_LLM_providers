from typing import Any, Dict, Optional
from .base import BasePricingScraper, MetadataMap, PricingMap


class AirforceScraper(BasePricingScraper):
    """Fetches pricing + metadata from Airforce public API.

    Airforce returns pricing in pricepermilliontokens (integer cents).
    Conversion: value / 100 = $/1M tokens.
    """

    RELIABILITY = "high"
    BADGE = "Live data"
    SOURCE_URL = "https://api.airforce"
    API_URL = "https://api.airforce/v1/models"

    async def scrape(self) -> tuple[PricingMap, Optional[MetadataMap]]:
        data = await self.get_json(self.API_URL, timeout=15)
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
        input_price = model.get("pricepermilliontokens")
        output_price = model.get("output_pricepermilliontokens", input_price)
        cache_price = model.get("cache_read_pricepermilliontokens")

        return self.compact_dict(
            {
                "input": self.cents_per_million_to_usd(input_price),
                "output": self.cents_per_million_to_usd(output_price),
                "multiplier": model.get("multiplier"),
                "cache": self.cents_per_million_to_usd(cache_price),
            }
        )

    def normalize_metadata(self, model: Dict[str, Any]) -> Dict[str, Any]:
        meta = self.compact_dict(
            {
                "tier": model.get("tier"),
                "tool_call": True if model.get("supports_tools") else None,
                "reasoning": True if model.get("supports_reasoning") else None,
                "supports_web_search": True if model.get("supports_web_search") else None,
            }
        )

        input_modalities = self.get_input_modalities(model, meta)
        self.add_modalities(
            meta,
            input_modalities=input_modalities,
            output_modalities=model.get("output_modalities"),
        )
        self.add_limit(
            meta,
            context=model.get("context_length"),
            output=model.get("max_output_tokens"),
        )

        supported_params = model.get("supported_parameters", [])
        if supported_params and "temperature" in supported_params:
            meta["temperature"] = True

        return meta

    @staticmethod
    def get_input_modalities(model: Dict[str, Any], meta: Dict[str, Any]) -> list:
        if model.get("input_modalities"):
            return model["input_modalities"]

        modalities = []
        if model.get("supports_vision"):
            modalities.append("image")
            meta["attachment"] = True
        if model.get("supports_audio_input"):
            modalities.append("audio")
        if model.get("supports_video_input"):
            modalities.append("video")
        if model.get("supports_documents"):
            modalities.append("document")
        if not modalities and any(
            model.get(flag)
            for flag in (
                "supports_vision",
                "supports_audio_input",
                "supports_video_input",
                "supports_documents",
            )
        ):
            modalities.append("text")
        return modalities
