"""Translation manager for multi-language support."""

import json
import os
from typing import Dict, Any, Optional, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class TranslationManager:
    """
    Manager for handling translations and internationalization.
    """
    
    def __init__(self, locale_dir: Optional[str] = None):
        """
        Initialize the translation manager.
        
        Args:
            locale_dir: Directory containing translation files
        """
        if locale_dir is None:
            locale_dir = Path(__file__).parent / "locales"
        
        self.locale_dir = Path(locale_dir)
        self.translations: Dict[str, Dict[str, str]] = {}
        self.default_language = "en"
        self.supported_languages = ["en", "ar", "ko"]
        
        # Load all translations
        self._load_translations()
    
    def _load_translations(self) -> None:
        """Load all translation files from the locale directory."""
        for lang in self.supported_languages:
            file_path = self.locale_dir / f"{lang}.json"
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.translations[lang] = json.load(f)
                    logger.info(f"Loaded translations for {lang}")
                except Exception as e:
                    logger.error(f"Error loading translations for {lang}: {str(e)}")
                    self.translations[lang] = {}
            else:
                logger.warning(f"Translation file not found: {file_path}")
                self.translations[lang] = {}
    
    def translate(self, key: str, language: str = "en", **kwargs) -> str:
        """
        Get translated text for a given key.
        
        Args:
            key: Translation key
            language: Target language code
            **kwargs: Variables to format in the translation
            
        Returns:
            Translated text
        """
        # Validate language
        if language not in self.supported_languages:
            language = self.default_language
        
        # Get translation
        translations = self.translations.get(language, {})
        text = translations.get(key, "")
        
        # Fallback to default language if not found
        if not text and language != self.default_language:
            text = self.translations.get(self.default_language, {}).get(key, "")
        
        # If still not found, return the key
        if not text:
            logger.warning(f"Translation not found for key: {key}")
            return key
        
        # Format with provided variables
        try:
            if kwargs:
                text = text.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing format variable in translation: {str(e)}")
        
        return text
    
    def get_language_name(self, language_code: str) -> str:
        """
        Get the name of a language in its own language.
        
        Args:
            language_code: Language code
            
        Returns:
            Language name
        """
        language_names = {
            "en": "English",
            "ar": "العربية",
            "ko": "한국어"
        }
        
        return language_names.get(language_code, language_code)
    
    def is_rtl(self, language_code: str) -> bool:
        """
        Check if a language is right-to-left.
        
        Args:
            language_code: Language code
            
        Returns:
            True if RTL language
        """
        rtl_languages = ["ar", "he", "fa", "ur"]
        return language_code in rtl_languages
    
    def format_number(self, number: float, language: str = "en") -> str:
        """
        Format number according to language conventions.
        
        Args:
            number: Number to format
            language: Language code
            
        Returns:
            Formatted number string
        """
        # Arabic uses Eastern Arabic numerals
        if language == "ar":
            arabic_numerals = "٠١٢٣٤٥٦٧٨٩"
            result = str(number)
            for i, digit in enumerate("0123456789"):
                result = result.replace(digit, arabic_numerals[i])
            return result
        
        # Korean and English use standard numerals
        return f"{number:,}"
    
    def format_currency(self, amount: float, currency: str = "USD", language: str = "en") -> str:
        """
        Format currency according to language conventions.
        
        Args:
            amount: Amount to format
            currency: Currency code
            language: Language code
            
        Returns:
            Formatted currency string
        """
        currency_symbols = {
            "USD": "$",
            "KRW": "₩",
            "SAR": "ر.س",
            "AED": "د.إ"
        }
        
        symbol = currency_symbols.get(currency, currency)
        
        # Format based on language
        if language == "ar":
            # Arabic format: number + symbol
            return f"{self.format_number(amount, language)} {symbol}"
        elif language == "ko":
            # Korean format: symbol + number
            return f"{symbol}{self.format_number(amount, language)}"
        else:
            # English format: symbol + number
            return f"{symbol}{self.format_number(amount, language)}"
    
    def get_direction(self, language: str = "en") -> str:
        """
        Get text direction for HTML/CSS.
        
        Args:
            language: Language code
            
        Returns:
            'rtl' or 'ltr'
        """
        return "rtl" if self.is_rtl(language) else "ltr"
    
    def reload_translations(self) -> None:
        """Reload all translation files."""
        self._load_translations()
        logger.info("Translations reloaded")
    
    def get_available_keys(self, language: str = "en") -> List[str]:
        """
        Get all available translation keys for a language.
        
        Args:
            language: Language code
            
        Returns:
            List of translation keys
        """
        return list(self.translations.get(language, {}).keys())
    
    def add_translation(self, key: str, translations: Dict[str, str]) -> None:
        """
        Add a new translation dynamically.
        
        Args:
            key: Translation key
            translations: Dictionary of language code to translation
        """
        for lang, text in translations.items():
            if lang in self.supported_languages:
                if lang not in self.translations:
                    self.translations[lang] = {}
                self.translations[lang][key] = text
                logger.info(f"Added translation for {key} in {lang}")
    
    def export_missing_translations(self) -> Dict[str, List[str]]:
        """
        Find and export missing translations across languages.
        
        Returns:
            Dictionary of language to missing keys
        """
        # Get all unique keys across all languages
        all_keys = set()
        for translations in self.translations.values():
            all_keys.update(translations.keys())
        
        # Find missing keys for each language
        missing = {}
        for lang in self.supported_languages:
            lang_keys = set(self.translations.get(lang, {}).keys())
            missing_keys = list(all_keys - lang_keys)
            if missing_keys:
                missing[lang] = missing_keys
        
        return missing