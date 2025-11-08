# 💰 Arez Currency – کتابخانه نرخ ارز، طلا و رمزارز 🇮🇷



ویژگی‌های کلیدی:

دریافت خودکار و به‌روز نرخ‌های لحظه‌ای

پشتیبانی از ارزهای اصلی (دلار، یورو، تتر)

پشتیبانی از فلزات گرانبها (طلا، سکه)

پشتیبانی از ارزهای دیجیتال (بیت‌کوین، اتریوم)

طراحی بهینه برای استفاده‌ی برنامه‌نویسی

پاسخگویی سریع و بدون تأخیر

کاربردها:

نمایش نرخ‌ در اپلیکیشن‌های مالی

یکپارچه‌سازی با سیستم‌های تجاری

توسعه‌ی داشبوردهای اقتصادی


## مثال سریع

```python
from arez_currency import ArezCurrency
import asyncio

data = asyncio.run(ArezCurrency().get_currency_data())
print(data)

# __


# __




```
```python

import asyncio
from arez_currency import ArezCurrency

async def main():
    arez = ArezCurrency()
    data = await arez.get_currency_data()
    msg = await arez.pretty_message()
    print(msg)

    print("📊 نرخ لحظه‌ای بازار ایران:")
    for key, value in data.items():
        print(f"{key}: {value}")

asyncio.run(main())

```
## ⚙️ نصب 

```bash
 pip install --upgrade arez-currency
```

