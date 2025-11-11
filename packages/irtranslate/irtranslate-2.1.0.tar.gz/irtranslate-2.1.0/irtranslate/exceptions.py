class TranslationError(Exception):
    """خطا در ترجمه / Translation failed"""
    pass

class NetworkError(Exception):
    """خطا در ارتباط شبکه / Network connection error"""
    pass

class EmptyTextError(Exception):
    """متن خالی است / Empty text provided"""
    pass

class AudioSaveError(Exception):
    """خطا در ذخیره فایل صوتی / Audio file save failed"""
    pass