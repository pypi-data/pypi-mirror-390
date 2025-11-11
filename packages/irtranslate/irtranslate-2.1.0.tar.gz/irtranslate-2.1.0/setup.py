from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="irtranslate",
    version="2.1.0",
    author="Ali Shirgol",
    author_email="ali.shirgol.coder@gmail.com",
    description="کتابخانه ترجمه پیشرفته با پشتیبانی کامل از فارسی و حالت‌های همزمان/ناهمزمان / Advanced Persian translation library with full sync/async support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alishirgol/irtranslate",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.1",
        "aiohttp>=3.8.0",
        "gTTS>=2.3.2",
        "pyttsx3>=2.90"
    ],
    extras_require={
        'full': [
            "pyttsx3>=2.90",
            "aiohttp>=3.8.0"
        ],
        'basic': [
            "requests>=2.25.1",
            "gTTS>=2.3.2"
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "Natural Language :: Persian",
        "Natural Language :: English",
        "Natural Language :: Arabic",
        "Natural Language :: Spanish", 
        "Natural Language :: French",
        "Natural Language :: German",
        "Natural Language :: Russian",
        "Natural Language :: Chinese",
        "Natural Language :: Japanese",
        "Natural Language :: Korean",
    ],
    keywords=[
        "translation", 
        "translator", 
        "persian", 
        "farsi", 
        "async", 
        "sync",
        "text-to-speech",
        "tts",
        "google-translate",
        "multilingual"
    ],
    project_urls={
        "Documentation": "https://github.com/alishirgol/irtranslate/wiki",
        "Source": "https://github.com/alishirgol/irtranslate",
        "Bug Reports": "https://github.com/alishirgol/irtranslate/issues",
    },
)