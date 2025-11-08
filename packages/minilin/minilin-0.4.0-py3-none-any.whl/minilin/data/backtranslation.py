"""
Back-translation for data augmentation
"""

import time
from typing import Optional, List
import random

from minilin.config import config
from minilin.utils import setup_logger

logger = setup_logger(__name__)


class BackTranslator:
    """
    Back-translation for text augmentation.
    
    Supports multiple translation APIs:
    - Google Translate (via googletrans)
    - DeepL API
    - Custom API
    """
    
    def __init__(self, api_type: str = "auto"):
        """
        Args:
            api_type: Translation API type ('googletrans', 'deepl', 'custom', 'auto')
        """
        self.api_type = api_type
        self.translator = None
        self._init_translator()
    
    def _init_translator(self):
        """Initialize translator based on API type."""
        if self.api_type == "auto":
            # Try to auto-detect available translator
            if self._try_googletrans():
                self.api_type = "googletrans"
            elif self._try_deepl():
                self.api_type = "deepl"
            else:
                logger.warning("No translation API available, back-translation disabled")
                self.api_type = "none"
        elif self.api_type == "googletrans":
            self._try_googletrans()
        elif self.api_type == "deepl":
            self._try_deepl()
    
    def _try_googletrans(self) -> bool:
        """Try to initialize googletrans."""
        try:
            from googletrans import Translator
            self.translator = Translator()
            logger.info("Using googletrans for back-translation")
            return True
        except ImportError:
            logger.debug("googletrans not available")
            return False
        except Exception as e:
            logger.debug(f"Failed to initialize googletrans: {e}")
            return False
    
    def _try_deepl(self) -> bool:
        """Try to initialize DeepL."""
        api_key = config.get('translation_api_key')
        if not api_key:
            logger.debug("DeepL API key not configured")
            return False
        
        try:
            import deepl
            self.translator = deepl.Translator(api_key)
            logger.info("Using DeepL for back-translation")
            return True
        except ImportError:
            logger.debug("deepl library not available")
            return False
        except Exception as e:
            logger.debug(f"Failed to initialize DeepL: {e}")
            return False
    
    def back_translate(
        self,
        text: str,
        intermediate_lang: str = "auto",
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Perform back-translation.
        
        Args:
            text: Original text
            intermediate_lang: Intermediate language ('auto' for random)
            max_retries: Maximum retry attempts
            
        Returns:
            Back-translated text or None if failed
        """
        if self.api_type == "none" or not self.translator:
            return None
        
        # Select intermediate language
        if intermediate_lang == "auto":
            intermediate_lang = random.choice(['fr', 'de', 'es', 'zh-cn', 'ja'])
        
        for attempt in range(max_retries):
            try:
                if self.api_type == "googletrans":
                    return self._back_translate_googletrans(text, intermediate_lang)
                elif self.api_type == "deepl":
                    return self._back_translate_deepl(text, intermediate_lang)
            except Exception as e:
                logger.debug(f"Back-translation attempt {attempt + 1} failed: {e}")
                time.sleep(1)  # Rate limiting
        
        return None
    
    def _back_translate_googletrans(self, text: str, intermediate_lang: str) -> str:
        """Back-translate using googletrans."""
        # Translate to intermediate language
        translated = self.translator.translate(text, dest=intermediate_lang)
        time.sleep(0.5)  # Rate limiting
        
        # Translate back to English
        back_translated = self.translator.translate(translated.text, dest='en')
        
        return back_translated.text
    
    def _back_translate_deepl(self, text: str, intermediate_lang: str) -> str:
        """Back-translate using DeepL."""
        # Map language codes
        lang_map = {
            'zh-cn': 'ZH',
            'ja': 'JA',
            'fr': 'FR',
            'de': 'DE',
            'es': 'ES'
        }
        target_lang = lang_map.get(intermediate_lang, intermediate_lang.upper())
        
        # Translate to intermediate language
        translated = self.translator.translate_text(text, target_lang=target_lang)
        
        # Translate back to English
        back_translated = self.translator.translate_text(str(translated), target_lang='EN-US')
        
        return str(back_translated)
    
    def augment_batch(
        self,
        texts: List[str],
        num_augmented: int = 1
    ) -> List[str]:
        """
        Augment a batch of texts using back-translation.
        
        Args:
            texts: List of original texts
            num_augmented: Number of augmented versions per text
            
        Returns:
            List of augmented texts
        """
        augmented = []
        
        for text in texts:
            for _ in range(num_augmented):
                aug_text = self.back_translate(text)
                if aug_text and aug_text != text:
                    augmented.append(aug_text)
        
        return augmented


# Convenience function
def back_translate_text(text: str, api_type: str = "auto") -> Optional[str]:
    """
    Quick back-translation function.
    
    Args:
        text: Text to augment
        api_type: Translation API type
        
    Returns:
        Back-translated text or None
    """
    translator = BackTranslator(api_type=api_type)
    return translator.back_translate(text)
