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

def crawl_kyobo(search_keyword, max_page=1):
	# 이미지 저장용 폴더
	folder = "images/kyobo"
	# 경로가 없으면 만들고 있으면 놔두기
	os.makedirs(folder, exist_ok=True)
	
	# https://search.kyobobook.co.kr/search?keyword=%ED%8C%8C%EC%9D%B4%EC%8D%AC&target=total&gbCode=TOT&page=1
	# 키워드, 맥스페이지 제거
	url = f"https://search.kyobobook.co.kr/search?keyword={search_keyword}&page={max_page}"
	driver.get(url)

