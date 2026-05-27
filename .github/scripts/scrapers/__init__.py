from .base import BasePricingScraper  # noqa: F401
from .base_api import BaseApiPricingScraper  # noqa: F401
from .airforce import AirforceScraper
from .openrouter import OpenRouterScraper
from .swiftrouter import SwiftRouterScraper

# Scraper registry: plain_name -> scraper instance
SCRAPERS: dict = {
    "Airforce": AirforceScraper(),
    "OpenRouter": OpenRouterScraper(),
    "SwiftRouter": SwiftRouterScraper(),
}
