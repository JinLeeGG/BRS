import os
import re
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
load_dotenv()
mongo_client = MongoClient(os.getenv("MONGODB"))
db = mongo_client['book_db']
collection = db['kyobo_books']
def extract_text_safe(title, field_name, element):
    if element:
        return element.text.strip()
    else:
        print(f"'{title}' {field_name} 없음")
        return "N/A"
def sanitize_name(name):
    return re.sub(r'[\\/:*?"<>|\n\r]', "_", name).strip()
def save_image(image_url, folder, title):
    # try:
    #     filename = sanitize_name(title) + ".jpg"
    #     file_path = os.path.join(folder, filename)
    #     response = requests.get(image_url, stream=True)
    pass
def crawl_kyobo(search_keyword, max_page=1):
    folder = "images/kyobo"
    os.makedirs(folder, exist_ok=True)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    results = []
    for page in range(1, max_page + 1):
        url = f"https://search.kyobobook.co.kr/search?keyword={search_keyword}&page={max_page}"
        driver.get(url)
        soup = BeautifulSoup(driver.page_source)
        books = soup.select('#shopData_list > ul > li')
        for book in books:
            title_elem = book.select_one("div.prod_name_group")
            title = title_elem.text.strip() if title_elem else "제목없음"
            author = extract_text_safe(title, "저자", book.select_one("div.prod_author_info a"))
            price = extract_text_safe(title, "가격", book.select_one("span.price"))
            publisher = extract_text_safe(title, "출판사", book.select_one("div.prod_publish > a"))
            pub_date = extract_text_safe(title, "출판일", book.select_one("div.prod_publish > span.date"))
            print(sanitize_name(title))
            print(sanitize_name(author))
            print(sanitize_name(price))
            print(sanitize_name(publisher))
            print(sanitize_name(pub_date))
            img_elem = book.select_one("img")
            image_url = img_elem['src'] if img_elem and 'src' in img_elem.attrs else None
            print(image_url)
            # local_image_path = save_image(image_url, folder, title) if image_url else None
    driver.quit()
    return results
crawl_kyobo("파이썬")