import gradio as gr
import requests
import os 
from PIL import Image # 파이썬에서 이미지를 보여주기위한 모듈 

# URL은 로컬로 설정
API_URL = "http://localhost:8000"

# 책 검색 
def get_titles(keyword):
	# FastAPI에 사용할 URL
	# keyword는 x 라고 날라감
	res = requests.get(f'{API_URL}/books', params={"keyword" : keyword})
	
	# 만약 리스폰스가 200번이라면 (정상적 접속)
	if res.ok:
		# json() 으로 받아서 변환
		books = res.json()
		# 책 개수 출력
		print(f'{len(books)}권 검색됨')
		# 책 제목이 books 각 element 안에 있으면 book['책제목'] 반환
		return [book["책제목"] for book in books if "책제목" in book]

	# 만약 if 문으로 안들어갔으면 데이터를 못받아온것이다.
	print('도서 목록 불러오기 실패')
	return []


# 책 추천
def recommend_book(title, keyword):
	res = requests.get(f"{API_URL}/recommend", params = {"title" : title, "keyword" : keyword})
	# json으로 변환
	data = res.json()
	# 책 이미지 가져오기
	img_path = data.get("image")
	# 만약 img_path가 있고 os에서 경로가 존재할때 img를 열기 그렇지 않다면 None
	img = Image.open(img_path) if img_path and os.path.exists(img_path) else None
	# recommendation 가져오기, 없다면 "추천 실패"
	return data.get("recommendation", "추천 실패"), img