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
    try:
        filename = sanitize_name(title) + ".jpg"
        file_path = os.path.join(folder, filename)
        response = requests.get(image_url, stream=True)
        # 요청이 실패했을 경우(4XX, 5XX) 예외를 발생
        # 다운로드 진행하기 전에 서버 응답이 정상인지 확인하는 안전 장치
        response.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(1024): # 1024바이트씩 반복해서 읽음
                f.write(chunk)
        return file_path
    except Exception as e:
        print(f"이미지 저장 실패! {e}")
        return None
    

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
            try:
                title_elem = book.select_one("div.prod_name_group")
                title = title_elem.text.strip() if title_elem else "제목없음"
                author = extract_text_safe(title, "저자", book.select_one("div.prod_author_info a"))
                price = extract_text_safe(title, "가격", book.select_one("span.price"))
                publisher = extract_text_safe(title, "출판사", book.select_one("div.prod_publish > a"))
                pub_date = extract_text_safe(title, "출판일", book.select_one("div.prod_publish > span.date"))
                # print(sanitize_name(title))
                # print(sanitize_name(author))
                # print(sanitize_name(price))
                # print(sanitize_name(publisher))
                # print(sanitize_name(pub_date))
                img_elem = book.select_one("img")
                image_url = img_elem['src'] if img_elem and 'src' in img_elem.attrs else None
                print(image_url)
                local_image_path = save_image(image_url, folder, title) if image_url else None
                data = {
                    "검색어": search_keyword,
                    "책제목": title,
                    "저자": author,
                    "가격": price,
                    "출판사": publisher,
                    "출판일": pub_date,
                    "이미지저장경로": local_image_path,
                    "판매사이트명": "Kyobo"
                }
                collection.insert_one(data)
                results.append(data)
            except Exception as e:
                print(f'[KYOBO] 처리 실패: {e}')
                

				
    driver.quit()
    return results