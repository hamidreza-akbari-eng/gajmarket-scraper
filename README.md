# Gajmarket Web Scraper
یک وب اسکرپر برای جمع‌آوری اطلاعات کتاب‌های مهندسی از وب‌سایت گاج‌مارکت با استفاده از سلنیوم و اسکرپی.

## ویژگی‌ها
- جمع‌آوری لینک‌های کتاب‌های مهندسی با سلنیوم
- استخراج جزئیات کتاب (نویسنده، تعداد صفحه و ...) با اسکرپی و Playwright
- ذخیره داده‌ها در فایل CSV

## پیش‌نیازها
- Python 3.8+
- Firefox و geckodriver
- کتابخانه‌ها: `selenium`, `scrapy`, `scrapy-playwright`, `selectolax`, `pandas`

## نصب
1. مخزن را کلون کنید:
   ```bash
   git clone https://github.com/hamidreza-akbari-eng/gajmarket-scraper.git
   cd gajmarket-scraper
