import aiohttp
import asyncio
import requests
import hashlib
import random
import string
import os
from gtts import gTTS
import pyttsx3
from .exceptions import TranslationError, NetworkError, EmptyTextError, AudioSaveError


class UnifiedTranslator:
    """
    مترجم یکپارچه با پشتیبانی کامل از حالت‌های همزمان و ناهمزمان
    Unified translator with full sync and async support
    """

    BASE_URL = "https://translate.googleapis.com/translate_a/single"

    def __init__(
        self,
        default_dest="en",
        retries=3,
        delay=1.0,
        cache_enabled=True,
        tts_engine="gtts",
    ):
        """
        default_dest (str): زبان پیشفرض مقصد
        retries (int): تعداد تلاش مجدد
        delay (float): تاخیر بین تلاش‌ها
        cache_enabled (bool): فعالسازی کش
        tts_engine (str): موتور TTS ('gtts' یا 'pyttsx3')
        """
        self.default_dest = default_dest
        self.retries = retries
        self.delay = delay
        self.cache_enabled = cache_enabled
        self._cache = {}
        self.tts_engine = tts_engine
        self._session = None
        self._async_mode = False
        self._pyttsx3_engine = None

        if tts_engine == "pyttsx3":
            try:
                self._pyttsx3_engine = pyttsx3.init()
                self._setup_pyttsx3()
            except Exception as e:
                print(f"⚠️ خطا در راه‌اندازی pyttsx3: {e}")
                self.tts_engine = "gtts"

    def _setup_pyttsx3(self):
        if self._pyttsx3_engine:
            self._pyttsx3_engine.setProperty("rate", 150)
            self._pyttsx3_engine.setProperty("volume", 0.9)

            voices = self._pyttsx3_engine.getProperty("voices")
            for voice in voices:
                if "persian" in voice.name.lower() or "farsi" in voice.name.lower():
                    self._pyttsx3_engine.setProperty("voice", voice.id)
                    break

    async def __aenter__(self):
        self._async_mode = True
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._async_mode = False
        if self._session:
            await self._session.close()
            self._session = None

    def __enter__(self):
        self._async_mode = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._async_mode = False

    async def get_async_session(self):

        if not self._session:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close_async(self):

        if self._session:
            await self._session.close()
            self._session = None

    def close_sync(self):

        pass

    def close(self):

        if self._async_mode and self._session:
            import warnings

            warnings.warn(
                "برای بستن session ناهمزمان از await close_async() استفاده کنید",
                RuntimeWarning,
            )
        else:
            self.close_sync()

    def translate(self, text, src="auto", dest=None, return_detected_lang=False):
        """
            text (str/list): متن یا لیست متون برای ترجمه
            src (str): زبان مبدأ
            dest (str): زبان مقصد
            return_detected_lang (bool): برگرداندن زبان تشخیص داده شده

        Returns:
            str/list/dict: متن ترجمه شده
        """
        if self._async_mode:

            return self.translate_async(text, src, dest, return_detected_lang)
        else:

            return self.translate_sync(text, src, dest, return_detected_lang)

    def translate_sync(self, text, src="auto", dest=None, return_detected_lang=False):

        dest = dest or self.default_dest

        if not text:
            raise EmptyTextError("متن ورودی نمی‌تواند خالی باشد")

        if isinstance(text, list):
            return [
                self._translate_single_sync(t, src, dest, return_detected_lang)
                for t in text
            ]
        else:
            return self._translate_single_sync(text, src, dest, return_detected_lang)

    def _translate_single_sync(self, text, src, dest, return_detected_lang):

        if not text.strip():
            raise EmptyTextError("متن خالی است")

        cache_key = self._generate_cache_key(text, src, dest)
        if self.cache_enabled and cache_key in self._cache:
            return self._cache[cache_key]

        params = {"client": "gtx", "sl": src, "tl": dest, "dt": "t", "q": text}

        for attempt in range(self.retries):
            try:
                response = requests.get(
                    self.BASE_URL,
                    params=params,
                    timeout=10,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                )
                response.raise_for_status()

                data = response.json()
                translated_text = "".join(
                    [item[0] for item in data[0] if item and item[0]]
                )
                detected_lang = data[2] if len(data) > 2 else src

                result = (
                    {"translation": translated_text, "detected_lang": detected_lang}
                    if return_detected_lang
                    else translated_text
                )

                if self.cache_enabled:
                    self._cache[cache_key] = result

                return result

            except Exception as e:
                if attempt == self.retries - 1:
                    raise TranslationError(f"خطا در ترجمه: {str(e)}")
                import time

                time.sleep(self.delay)

    async def translate_async(
        self, text, src="auto", dest=None, return_detected_lang=False
    ):

        dest = dest or self.default_dest

        if not text:
            raise EmptyTextError("متن ورودی نمی‌تواند خالی باشد")

        session = await self.get_async_session()

        if isinstance(text, list):
            tasks = [
                self._translate_single_async(
                    t, src, dest, return_detected_lang, session
                )
                for t in text
            ]
            return await asyncio.gather(*tasks)
        else:
            return await self._translate_single_async(
                text, src, dest, return_detected_lang, session
            )

    async def _translate_single_async(
        self, text, src, dest, return_detected_lang, session
    ):

        if not text.strip():
            raise EmptyTextError("متن خالی است")

        cache_key = self._generate_cache_key(text, src, dest)
        if self.cache_enabled and cache_key in self._cache:
            return self._cache[cache_key]

        params = {"client": "gtx", "sl": src, "tl": dest, "dt": "t", "q": text}

        for attempt in range(self.retries):
            try:
                async with session.get(
                    self.BASE_URL,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10),
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                ) as response:
                    response.raise_for_status()
                    data = await response.json(content_type=None)

                    translated_text = "".join(
                        [item[0] for item in data[0] if item and item[0]]
                    )
                    detected_lang = data[2] if len(data) > 2 else src

                    result = (
                        {"translation": translated_text, "detected_lang": detected_lang}
                        if return_detected_lang
                        else translated_text
                    )

                    if self.cache_enabled:
                        self._cache[cache_key] = result

                    return result

            except aiohttp.ClientError as e:
                if attempt == self.retries - 1:
                    raise NetworkError(f"خطای شبکه پس از {self.retries} تلاش: {str(e)}")
                await asyncio.sleep(self.delay)
            except Exception as e:
                if attempt == self.retries - 1:
                    raise TranslationError(f"خطا در ترجمه: {str(e)}")
                await asyncio.sleep(self.delay)

    def text_to_speech(self, text, lang=None, filename=None, slow=False):

        if self._async_mode:
            return self.text_to_speech_async(text, lang, filename, slow)
        else:
            return self.text_to_speech_sync(text, lang, filename, slow)

    def text_to_speech_sync(self, text, lang=None, filename=None, slow=False):

        lang = lang or self.default_dest

        if self.tts_engine == "pyttsx3" and self._is_persian_text(text):
            return self._text_to_speech_pyttsx3_sync(text, filename)
        else:
            return self._text_to_speech_gtts_sync(text, lang, filename, slow)

    async def text_to_speech_async(self, text, lang=None, filename=None, slow=False):

        lang = lang or self.default_dest

        if self.tts_engine == "pyttsx3" and self._is_persian_text(text):
            return await self._text_to_speech_pyttsx3_async(text, filename)
        else:
            return await self._text_to_speech_gtts_async(text, lang, filename, slow)

    # ==================== SYNC TTS METHODS ====================

    def _text_to_speech_pyttsx3_sync(self, text, filename=None):

        try:
            if not filename:
                filename = f"tts_fa_{self._generate_random_string(8)}.mp3"

            filepath = os.path.join(os.getcwd(), filename)

            if self._pyttsx3_engine:
                self._pyttsx3_engine.save_to_file(text, filepath)
                self._pyttsx3_engine.runAndWait()
            else:

                return self._text_to_speech_gtts_sync(text, "fa", filename, False)

            print(f"🔊 فایل صوتی فارسی ذخیره شد: {filename}")
            return filepath

        except Exception as e:
            raise AudioSaveError(f"خطا در ذخیره فایل صوتی فارسی: {str(e)}")

    def _text_to_speech_gtts_sync(self, text, lang, filename, slow):

        try:
            lang_map = self._get_tts_lang_map()
            tts_lang = lang_map.get(lang, "en")
            tts = gTTS(text=text, lang=tts_lang, slow=slow)

            if not filename:
                filename = f"tts_{self._generate_random_string(8)}_{lang}.mp3"

            filepath = os.path.join(os.getcwd(), filename)
            tts.save(filepath)

            print(f"🔊 فایل صوتی ذخیره شد: {filename}")
            return filepath

        except Exception as e:
            raise AudioSaveError(f"خطا در ذخیره فایل صوتی: {str(e)}")

    async def _text_to_speech_pyttsx3_async(self, text, filename=None):

        try:
            if not filename:
                filename = f"tts_async_fa_{self._generate_random_string(8)}.mp3"

            filepath = os.path.join(os.getcwd(), filename)

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._save_pyttsx3_sync, text, filepath)

            print(f"🔊 فایل صوتی فارسی (Async) ذخیره شد: {filename}")
            return filepath

        except Exception as e:
            raise AudioSaveError(f"خطا در ذخیره فایل صوتی فارسی: {str(e)}")

    def _save_pyttsx3_sync(self, text, filepath):

        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 0.9)
        engine.save_to_file(text, filepath)
        engine.runAndWait()

    async def _text_to_speech_gtts_async(self, text, lang, filename, slow):

        try:
            lang_map = self._get_tts_lang_map()
            tts_lang = lang_map.get(lang, "en")

            loop = asyncio.get_event_loop()
            filepath = await loop.run_in_executor(
                None, self._save_gtts_sync, text, tts_lang, filename, slow
            )

            print(f"🔊 فایل صوتی (Async) ذخیره شد: {os.path.basename(filepath)}")
            return filepath

        except Exception as e:
            raise AudioSaveError(f"خطا در ذخیره فایل صوتی: {str(e)}")

    def _save_gtts_sync(self, text, lang, filename, slow):
        tts = gTTS(text=text, lang=lang, slow=slow)

        if not filename:
            filename = f"tts_async_{self._generate_random_string(8)}_{lang}.mp3"

        filepath = os.path.join(os.getcwd(), filename)
        tts.save(filepath)
        return filepath

    async def translate_batch_async(
        self, texts, src="auto", dest=None, return_detected_lang=False, batch_size=10
    ):

        dest = dest or self.default_dest
        session = await self.get_async_session()

        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            tasks = [
                self._translate_single_async(
                    t, src, dest, return_detected_lang, session
                )
                for t in batch
            ]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            results.extend(batch_results)

            if i + batch_size < len(texts):
                await asyncio.sleep(0.5)

        return results

    def translate_batch_sync(
        self, texts, src="auto", dest=None, return_detected_lang=False
    ):

        return self.translate_sync(texts, src, dest, return_detected_lang)

    async def translate_to_multiple_async(
        self, text, src="auto", dest_languages=None, return_detected_lang=False
    ):

        if not dest_languages:
            dest_languages = ["en", "fa", "ar", "es", "fr"]

        session = await self.get_async_session()

        tasks = {}
        for lang in dest_languages:
            tasks[lang] = self._translate_single_async(
                text, src, lang, return_detected_lang, session
            )

        results = {}
        for lang, task in tasks.items():
            try:
                results[lang] = await task
            except Exception as e:
                results[lang] = f"Error: {str(e)}"

        return results

    def translate_to_multiple_sync(
        self, text, src="auto", dest_languages=None, return_detected_lang=False
    ):

        if not dest_languages:
            dest_languages = ["en", "fa", "ar", "es", "fr"]

        results = {}
        for lang in dest_languages:
            try:
                results[lang] = self.translate_sync(
                    text, src, lang, return_detected_lang
                )
            except Exception as e:
                results[lang] = f"Error: {str(e)}"

        return results

    # ==================== HELPER METHODS ====================

    def _is_persian_text(self, text):

        persian_chars = set("ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی")
        return any(char in persian_chars for char in text)

    def _generate_cache_key(self, text, src, dest):

        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        return f"{text_hash}_{src}_{dest}"

    def _generate_random_string(self, length=8):

        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    def _get_tts_lang_map(self):

        return {
            "fa": "en",
            "en": "en",
            "ar": "ar",
            "es": "es",
            "fr": "fr",
            "de": "de",
            "it": "it",
            "ja": "ja",
            "ko": "ko",
            "zh": "zh",
            "ru": "ru",
        }

    # ==================== USER-FRIENDLY INTERFACE ====================

    def quick_translate(self, text, to_lang=None):

        return self.translate(text, dest=to_lang)

    async def quick_translate_async(self, text, to_lang=None):

        return await self.translate_async(text, dest=to_lang)

    def detect_language(self, text):

        result = self.translate(text, return_detected_lang=True)
        return result["detected_lang"] if isinstance(result, dict) else "Unknown"

    async def detect_language_async(self, text):

        result = await self.translate_async(text, return_detected_lang=True)
        return result["detected_lang"] if isinstance(result, dict) else "Unknown"

    # ==================== CACHE MANAGEMENT ====================

    def clear_cache(self):

        self._cache.clear()
        print("🧹 کش پاک شد")

    def get_cache_size(self):

        return len(self._cache)

    def get_cache_info(self):

        return {
            "size": len(self._cache),
            "enabled": self.cache_enabled,
            "keys": list(self._cache.keys())[:10],
        }

    def enable_cache(self):

        self.cache_enabled = True
        print("💾 کش فعال شد")

    def disable_cache(self):

        self.cache_enabled = False
        print("💾 کش غیرفعال شد")

    # ==================== LANGUAGE MANAGEMENT ====================

    def set_default_language(self, lang):

        self.default_dest = lang
        print(f"🌍 زبان پیشفرض تنظیم شد به: {lang}")

    def get_supported_languages(self):

        return {
            "فارسی": "fa",
            "انگلیسی": "en",
            "عربی": "ar",
            "آلمانی": "de",
            "فرانسوی": "fr",
            "اسپانیایی": "es",
            "ایتالیایی": "it",
            "روسی": "ru",
            "چینی": "zh",
            "ژاپنی": "ja",
            "کره‌ای": "ko",
            "ترکی": "tr",
            "هندی": "hi",
        }

    def get_tts_supported_languages(self):

        if self.tts_engine == "pyttsx3":
            return {"فارسی": "fa", "انگلیسی": "en"}
        else:
            return {
                "انگلیسی": "en",
                "عربی": "ar",
                "اسپانیایی": "es",
                "فرانسوی": "fr",
                "آلمانی": "de",
                "ایتالیایی": "it",
                "ژاپنی": "ja",
                "کره‌ای": "ko",
                "چینی": "zh",
                "روسی": "ru",
            }


# ==================== ALIAS FOR EASY USAGE ====================
Translator = UnifiedTranslator
