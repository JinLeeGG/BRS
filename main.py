import os
from dotenv import load_dotenv
from openai import OpenAI
from pymongo import MongoClient
from fastapi import FastAPI
from crawler import crawl_kyobo

# 파일 실행 
# uvicorn main:app --reload

# env 파일 읽어오기
load_dotenv()

#OpenAI, MongoDB, FastAPI 클라이언트 만들기
openai_client = OpenAI(api_key=os.getenv("API_KEY"))
mongo_client = MongoClient(os.getenv("MONGODB"))
app = FastAPI()

# DB 
db = mongo_client['book_db']
collection = db['kyobo_books']

# annotation으로 가이드 형식으로 작성함 
@app.get("/books")
def get_books(keyword: str = "파이썬") -> list[dict]:
	# 검색어가 keyword인걸 찾기 / object id 안가져오기
    books = list(collection.find({"검색어": keyword}, {"_id": 0}))
    print(f"'{keyword}' 검색 결과 개수: {len(books)}")
    if not books:
		# 만약 데이터가 없으면
        print(f"'{keyword}'에 대한 MongoDB 데이터가 없음 -> 크롤링 시작")
        crawl_kyobo(keyword, max_page=3)
        books = list(collection.find({"검색어": keyword}, {"_id": 0}))
        print(f'크롤링 후 {len(books)}건 저장됨')
    return books


@app.get("/recommend")
# 매개변수는 기본값
def recommend(title: str = None, keyword: str = "파이썬"):
	if not title:
		return {'error': 'title 파라미터가 누락되었습니다.'}
	
	books = list(collection.find({"검색어":keyword}))
	if not books:
		print(f"'{keyword}'에 대한 MongoDB 데이터가 없음 --> 크롤링 시작")