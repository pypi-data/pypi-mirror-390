from irtranslate import Translator
import asyncio

# نمونه سینک
translator = Translator()

# ترجمه لیست
texts = ["سلام", "خداحافظ", "متشکرم"]
results = translator.translate(texts, dest="en")
print(results)

# ترجمه به چند زبان
multi_results = translator.translate_to_multiple_sync("سلام", ['en', 'ar', 'es'])
print(multi_results)

# تبدیل متن به صوت
translator.text_to_speech("Hello world", lang="en", filename="test.mp3")

# نمونه ایسینک
async def main():
    async with Translator() as translator:
        # ترجمه لیست
        texts = ["صبح بخیر", "عصر بخیر", "شب بخیر"]
        results = await translator.translate(texts, dest="en")
        print(results)
        
        # ترجمه به چند زبان
        multi_results = await translator.translate_to_multiple_async("درود", ['en', 'fr', 'de'])
        print(multi_results)
        
        # تبدیل متن به صوت
        await translator.text_to_speech("This is a test", lang="en", filename="test_async.mp3")

asyncio.run(main())