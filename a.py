import os
from pymongo import MongoClient
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

#selenum의 없는 기능을 구현하기위해서 사용 
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


load_dotenv()

mongo_client = MongoClient(os.getenv("MONGODB"))
# DB 
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


def crawl_kyobo(search_keyword, max_page=1):
	# 이미지 저장용 폴더
	folder = "images/kyobo"
	# 경로가 없으면 만들고 있으면 놔두기
	os.makedirs(folder, exist_ok=True)

	# driver 세팅 (chrome)
	# 창 안띄우는 옵션 - 버전 충돌 방지용
	chrome_options = Options()
	chrome_options.add_argument("--headless")
	chrome_options.add_argument("--no-sandbox")
	chrome_options.add_argument("--disable-dev-shm-usage")
	driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) 

	results = []
	for page in range(1, max_page + 1):
		# https://search.kyobobook.co.kr/search?keyword=%ED%8C%8C%EC%9D%B4%EC%8D%AC&target=total&gbCode=TOT&page=1
		# 키워드, 맥스페이지 제거
		url = f"https://search.kyobobook.co.kr/search?keyword={search_keyword}&page={max_page}"
		driver.get(url)
		soup = BeautifulSoup(driver.page_source)
		# #shopData_list > ul > li:nth-child(1) > div.prod_area.horizontal
		books = soup.select("shopData_list > ul > li")

		for book in books:
			# css 함수를 이용해서 제목 찾기
			title_elem = book.select_one("div.prod_name_group")
			# 타이틀이 존재하면 공백 빼서 저장, 없으면 "제목없음"
			title = title_elem.text.strip() if title_elem else "제목없음"
			author = extract_text_safe(title, "저자", book.select_one("div.prod_author_info a"))			# <div> 바로 밑이 아닌 여러개가 겁친뒤 다음 <a> 를 말한다.
			price = extract_text_safe(title, "가격", book.select_one("span.price"))
			publisher = extract_text_safe(title, "출판사", book.select_one("div.prod_publish > a"))			# > 는 <div> 바로 밑에 있는 <a>를 말한다.
			pub_date = extract_text_safe(title, "출판일", book.select_one("div.prod_publish > span.date"))
			print(sanitize_name(title))
			print(sanitize_name(author))
			print(sanitize_name(price))
			print(sanitize_name(publisher))
			print(sanitize_name(pub_date))
	
	driver.quit()
	return results


crawl_kyobo("파이썬")