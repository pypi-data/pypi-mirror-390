# arez_currency/core.py
import aiohttp
import asyncio
import re
from datetime import datetime
from pytz import timezone
import jdatetime
import logging
from logging.handlers import RotatingFileHandler
import os
import json


class ArezCurrency:
    """
    کتابخانه‌ای برای دریافت نرخ لحظه‌ای ارز، طلا و رمزارز از منابع ایرانی 🇮🇷

    ویژگی‌ها:
    ----------
    - دریافت داده‌ها به‌صورت async
    - تاریخ شمسی (جلالی)
    - خروجی JSON-friendly برای استفاده در ربات‌ها و وب‌اپ‌ها
    - طراحی سبک و قابل‌گسترش
    """

    def __init__(self, log_dir: str = "logs", source_url: str = None):
        """راه‌اندازی کلاس"""
        self.url = source_url or 'https://www.iranjib.ir/showgroup/23/realtime_price/'
        self.logger = self._setup_logger(log_dir)
        self.logger.info("ArezCurrency initialized successfully ✅")

    # ----------------------------- Logger Setup -----------------------------

    def _setup_logger(self, log_dir: str):
        """راه‌اندازی سیستم ثبت گزارش‌ها"""
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "arez_currency.log")

        logger = logging.getLogger("ArezCurrency")
        logger.setLevel(logging.INFO)

        log_format = "%(asctime)s - [%(levelname)s] - %(message)s"
        handler = RotatingFileHandler(
            log_file, maxBytes=1_000_000, backupCount=5, encoding='utf-8'
        )
        handler.setFormatter(logging.Formatter(log_format))

        if not logger.handlers:
            logger.addHandler(handler)

        return logger

    # ----------------------------- Time Handling -----------------------------

    async def _get_jalali_time(self) -> str:
        """دریافت تاریخ و ساعت فعلی به وقت تهران (شمسی)"""
        tehran_tz = timezone('Asia/Tehran')
        tehran_time = datetime.now(tehran_tz)
        jalali_datetime = jdatetime.datetime.fromgregorian(datetime=tehran_time)
        return jalali_datetime.strftime("%Y/%m/%d %H:%M:%S")

    # ----------------------------- Data Fetch -----------------------------

    async def _fetch_html(self) -> str:
        """دریافت HTML صفحه منبع"""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                if response.status != 200:
                    raise Exception(f"خطا در اتصال به منبع داده ({response.status})")
                return await response.text()

    # ----------------------------- Main Method -----------------------------

    async def get_currency_data(self, as_json: bool = False) -> dict:
        """
        دریافت نرخ لحظه‌ای ارز، طلا و رمزارزها 🇮🇷

        پارامترها:
        -----------
        - as_json (bool): اگر True باشد، خروجی به‌صورت JSON برمی‌گردد.

        خروجی:
        -------
        dict یا JSON شامل:
        - date, gold_mesghal, gold_18, gold_24, new_coin, old_coin, half_coin,
          tether, dollar, euro, btc, eth
        """
        try:
            html = await self._fetch_html()
            persian_date = await self._get_jalali_time()

            # استخراج قیمت‌ها از HTML
            prices = re.findall(r'<span class="lastprice">(.*?)<\/span>', html)

            # اندیس‌های مورد نظر برای داده‌ها
            selected_indices = [4, 8, 12, 20, 25, 30, 49, 57, 67, 81, 85]
            labels = [
                "gold_mesghal", "gold_18", "gold_24",
                "new_coin", "old_coin", "half_coin",
                "tether", "dollar", "euro", "btc", "eth"
            ]

            # تبدیل به دیکشنری
            data = {
                "date": persian_date,
                **{
                    labels[i]: prices[idx] if idx < len(prices) else "ندارد"
                    for i, idx in enumerate(selected_indices)
                }
            }

            # لاگ موفقیت
            self.logger.info("✅ Data fetched successfully")

            # خروجی JSON برای ربات‌ها یا APIها
            if as_json:
                return json.dumps(data, ensure_ascii=False, indent=2)
            return data

        except Exception as e:
            self.logger.error(f"❌ Error fetching data: {e}")
            error_data = {
                "status": "error",
                "message": "خطا در دریافت اطلاعات",
                "details": str(e)
            }
            return json.dumps(error_data, ensure_ascii=False) if as_json else error_data

    # ----------------------------- Helper for Bots -----------------------------

    async def pretty_message(self) -> str:
        """
        برگرداندن خروجی زیبا برای نمایش در ربات‌ها یا پیام‌ها 💬
        """
        data = await self.get_currency_data()
        msg = (
            f"📅 تاریخ: {data['date']}\n\n"
            f"🏆 طلا و سکه:\n"
            f"  • مثقال طلا: {data['gold_mesghal']}\n"
            f"  • طلای ۱۸ عیار: {data['gold_18']}\n"
            f"  • طلای ۲۴ عیار: {data['gold_24']}\n"
            f"  • سکه جدید: {data['new_coin']}\n"
            f"  • سکه قدیم: {data['old_coin']}\n"
            f"  • نیم‌سکه: {data['half_coin']}\n\n"
            f"💵 ارزها:\n"
            f"  • دلار: {data['dollar']}\n"
            f"  • یورو: {data['euro']}\n"
            f"  • تتر: {data['tether']}\n\n"
            f"💠 رمزارزها:\n"
            f"  • بیت‌کوین: {data['btc']}\n"
            f"  • اتریوم: {data['eth']}\n"
        )
        return msg



