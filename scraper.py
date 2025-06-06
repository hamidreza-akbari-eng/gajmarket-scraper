from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selectolax.parser import HTMLParser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selectolax
import pandas as pd
import time
import scrapy
from selectolax.parser import HTMLParser


def get_links(driver):
    try:
        driver.get("https://www.gajmarket.com")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//li[@class='megamenu__item'][4]")
            )
        )

        college_books = driver.find_element(
            By.XPATH, value="//li[@class='megamenu__item'][4]"
        )
        college_books.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[@class='category-page__sub-category-item'][1]")
            )
        )

        engineering_books = driver.find_element(
            By.XPATH, value="//a[@class='category-page__sub-category-item'][1]"
        )
        engineering_books.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@class='category-page__product-list']//a")
            )
        )

        uniqe_book_links = set()
        paginates = 0
        while True:
            links = driver.find_elements(
                By.XPATH, value="//div[@class='category-page__product-list']//a"
            )
            for link in links:
                try:
                    href = link.get_attribute("href")
                    if href:
                        uniqe_book_links.add(href)

                except:
                    continue
            try:
                nextpage = driver.find_element(
                    By.XPATH,
                    value="//div[@class='category-page__pagination-next-item']//a",
                )
                nextpage.click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@class='category-page__product-list']//a")
                    )
                )
            except TimeoutException:
                print("امکان استخراج لینک های صفحه بعد وجود ندارد.")
            paginates += 1
            if paginates == 55:
                break

        return list(uniqe_book_links)
    except Exception as e:
        print(f"خطا در جمع آوری لینک ها {str(e)}")
        return []


service = Service()
driver = webdriver.Firefox(service=service)
try:
    all_links = get_links(driver)
    if not all_links:
        print("هیچ لینکی استخراج نشد")
finally:
    driver.quit()


class GajmarketBooks(scrapy.Spider):
    name = "GajmarketBot"

    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "firefox",
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 90 * 1000,
        "FEED_FORMAT": "csv",
        "FEED_URI": "informations.csv",
        "FEED_EXPORT_ENCODING": "utf-8-sig",
        "CONCURRENT_REQUESTS": 2,
        "DOWNLOAD_DELAY": 1,
    }

    def start_requests(self):
        all_urls = all_links
        for url in all_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [("wait_for_load_state", "networkidle")],
                },
            )

    def parse(self, response):

        html = HTMLParser(response.text)

        data = {"url": response.url}

        tables = html.css("table.product__specifications-table")

        if not tables:
            data["error"] = "هیچ جدولی یافت نشد"
            yield data
            return

        target_table = tables[1] if len(tables) > 1 else tables[0]

        for item in target_table.css("tr"):
            name = item.css_first("td.product__specifications-name")
            value = item.css_first("td.product__specifications-value")
            if name and value:
                field_name = name.text(strip=True).strip(":")
                field_value = value.text(strip=True)

                if field_name == "رشته":
                    data["رشته"] = field_value
                elif field_name == "ویرایش":
                    data["ویرایش"] = field_value
                elif field_name == "نویسنده":
                    data["نویسنده"] = field_value
                elif field_name == "مترجم":
                    data["مترجم"] = field_value
                elif field_name == "تعداد صفحه":
                    data["تعداد صفحه"] = field_value
                elif field_name == "قطع":
                    data["قطع"] = field_value
                elif field_name == "نوع جلد":
                    data["نوع جلد"] = field_value
                elif field_name == "وزن":
                    data["وزن"] = field_value
                elif field_name == "کد بین المللی(شابک یا ...)":
                    data["کد بین المللی(شابک یا ...)"] = field_value

        yield data
