from .translator import Translator, UnifiedTranslator
from .exceptions import TranslationError, NetworkError, EmptyTextError, AudioSaveError

__version__ = "2.1.0"
__author__ = "Ali Shirgol"
__all__ = [
    'Translator', 
    'UnifiedTranslator', 
    'TranslationError', 
    'NetworkError', 
    'EmptyTextError', 
    'AudioSaveError'
]