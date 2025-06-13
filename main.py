import os
from dotenv import load_dotenv
from openai import OpenAI
from pymongo import MongoClient
from fastapi import FastAPI

# env 파일 읽어오기
load_dotenv()

#OpenAI, MongoDB, FastAPI 클라이언트 만들기
openai_client = OpenAI(api_key=os.getenv("API_KEY"))
mongo_client = MongoClient(os.getenv("MONGODB"))
app = FastAPI()

# DB 
db = mongo_client['book_db']
collection = db['kyobo_books']

