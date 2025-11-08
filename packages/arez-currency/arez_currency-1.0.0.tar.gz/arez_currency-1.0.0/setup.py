# setup.py
from setuptools import setup, find_packages
from pathlib import Path

# مسیر فایل README.md برای long_description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="arez_currency",
    version="1.0.0",
    author="AmirhosseinPython",
    author_email="amirhossinpython03@gmail.com",
    description="A simple asynchronous currency, gold, and crypto price fetcher for the Iranian market.",
    long_description=long_description,
    long_description_content_type="text/markdown",  # مهم برای PyPI
    url="https://github.com/amirhossinpython/arez_currency",  # لینک گیت‌هاب (در آینده)
    project_urls={
        "Source": "https://github.com/amirhossinpython/arez_currency",
        "Tracker": "https://github.com/amirhossinpython/arez_currency/issues",
    },
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "aiohttp>=3.8.0",
        "jdatetime>=3.6.0",
        "pytz>=2023.0"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "Natural Language :: Persian",
    ],
    keywords=[
        "currency", "exchange", "forex", "crypto", "Iran", "gold", "arez_currency", "asyncio"
    ],
)
