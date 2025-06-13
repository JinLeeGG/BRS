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
	# recommendation, img 가져오기. 없다면 "추천 실패" 반환
	return data.get("recommendation", "추천 실패"), img

# 검색, 추천 결과를 화면에 갱신
def search_and_recommend(keyword):
	# 제목 가져오기
	titles = get_titles(keyword)
	# 제목이 있다면
	if titles:
		print(f"검색어 '{keyword}'로 {len(titles)}개 책 제목 불러옴.")
		# title 업데이트
		return gr.update(choices=titles, value=titles[0])
	
	# 제목이 없다면
	print("검색어 '{keyword}' 결과 없음")
	return gr.update(choices=[], value=None)

# frontend
with gr.Blocks() as app:
	gr.Markdown("## GPT 기반 교보문고 도서 추천기")
	keyword_input = gr.Textbox(label="검색어 입력", placeholder='예: 파이썬')
	search_btn = gr.Button("도서 목록 불러오기")
	title_dropdown = gr.Dropdown(label="도서 선택")
	recommend_btn = gr.Button("GPT 추천 받기")
	output_text = gr.Textbox(label="추천 결과")
	output_img = gr.Image(label="책 이미지")

	search_btn.click(fn=search_and_recommend, inputs=keyword_input, outputs=title_dropdown)
	recommend_btn.click(fn=recommend_book, input=[title_dropdown, keyword_input], outputs=[output_text, output_img])

app.launch()
