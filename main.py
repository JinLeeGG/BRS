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

# 필요없는내용 제거(enter, \, 공백) 및 정렬
def normalize(text):
	return text.replace("\n", "").replace("\r", "").strip().lower()

# 책 추천 받기
@app.get("/recommend")
# 매개변수는 기본값
def recommend(title: str = None, keyword: str = "파이썬"):
	# 만약 타이틀이 존재하지 않으면
	if not title:
		return {'error': 'title 파라미터가 누락되었습니다.'}
	
	books = list(collection.find({"검색어":keyword}))
	if not books:
		print(f"'{keyword}'에 대한 MongoDB 데이터가 없음 --> 크롤링 시작")
		crawl_kyobo(keyword, max_page=3)
		books = list(collection.find({"검색어" : keyword}))
	
	# 책 제목을 키로 가져와서 데이터 전처리 후 저장
	book = next((b for b in books if normalize(b.get("책제목", "")) == normalize(title)), None)
	
	# 만약 이 제목을 가진 책을 못찾았으면
	if not book:
		print("유사한 제목을 가진 책을 찾지 못했습니다.")
		return {"message": "책을 찾을 수 없습니다."}

	# LLM에 검색할 내용을 담은 프롬프트 
	prompt = f"""
		책 제목: {book['책제목']}
		저자: {book['저자']}
		설명: {book['출판사']}에서 출간된 책입니다.
		위 책과 비슷한 주제나 스타일을 가진 추천 도서 3권을 제안해줘. 각 추천에는 간단한 이유도 포함해줘."""
	
	try:
		response = openai_client.chat.completions.create(
			model="gpt-4",
			messages=[
				{"role": "system", "content" : "당신은 전문 서평가입니다."},
				{"role": "user", "content" : prompt}
			]
		)
		print("GPT 응답 수신 완료")
		content = response.choices[0].message.content	
		return {
			"recommendation" : content,
			"image" : book.get("이미지저장경로", None)
		}
	except Exception as e:
		print(f"GPT 추천 실패: {e}")
		return {"error":str(e)}
