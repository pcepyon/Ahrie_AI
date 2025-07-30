"""Web scrapers for gathering medical and review data."""

from .youtube_scraper import YouTubeScraper
from .medical_scraper import MedicalInfoScraper

__all__ = ["YouTubeScraper", "MedicalInfoScraper"]