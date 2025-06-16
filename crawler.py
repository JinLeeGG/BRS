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

# .env 파일에 정의된 환경 변수를 로드합니다. (주로 API 키나 비밀번호 등 민감한 정보를 저장)
load_dotenv()
# 환경 변수에서 MongoDB 연결 URI를 가져와 MongoDB 클라이언트를 생성합니다.
mongo_client = MongoClient(os.getenv("MONGODB"))
# 'book_db'라는 이름의 데이터베이스에 연결합니다. 없으면 새로 생성됩니다.
db = mongo_client['book_db']
# 데이터베이스 내에 'kyobo_books'라는 이름의 컬렉션(테이블과 유사)에 연결합니다.
collection = db['kyobo_books']


# 웹 요소에서 텍스트를 안전하게 추출하는 함수
def extract_text_safe(title, field_name, element):
    """
    BeautifulSoup으로 선택한 요소(element)가 존재하는지 확인하고,
    존재하면 텍스트를 추출하여 반환하고, 없으면 경고 메시지를 출력하고 "N/A"를 반환합니다.
    Args:
        title (str): 현재 처리 중인 책의 제목 (로그 출력용)
        field_name (str): 추출하려는 필드의 이름 (예: "저자", "가격")
        element (bs4.element.Tag): BeautifulSoup으로 선택한 웹 요소 객체
    Returns:
        str: 추출된 텍스트 또는 "N/A"
    """
    if element:
        return element.text.strip()  # 요소가 있으면 양쪽 공백을 제거한 텍스트를 반환
    else:
        print(f"'{title}' {field_name} 없음")  # 요소가 없으면 어떤 정보가 없는지 출력
        return "N/A"  # "Not Available" (정보 없음)을 의미하는 문자열 반환


# 파일명으로 사용할 수 없는 문자를 제거하는 함수
def sanitize_name(name):
    """
    문자열에서 파일명으로 사용할 수 없는 특수문자들을 밑줄(_)로 변경합니다.
    Args:
        name (str): 정리할 원본 문자열
    Returns:
        str: 특수문자가 제거된 안전한 파일명 문자열
    """
    # 정규표현식을 사용하여 파일명에 부적합한 문자(\, /, :, *, ?, ", <, >, |, 개행)를 '_'로 바꿉니다.
    return re.sub(r'[\\/:*?"<>|\n\r]', "_", name).strip()


# 이미지 URL로부터 이미지를 다운로드하여 로컬에 저장하는 함수
def save_image(image_url, folder, title):
    """
    주어진 URL의 이미지를 지정된 폴더에 저장합니다.
    파일 이름은 책 제목을 이용하여 만듭니다.
    Args:
        image_url (str): 다운로드할 이미지의 URL
        folder (str): 이미지를 저장할 폴더 경로
        title (str): 이미지 파일의 이름으로 사용할 책 제목
    Returns:
        str or None: 이미지가 성공적으로 저장된 경우 파일 경로를 반환하고, 실패 시 None을 반환합니다.
    """
    try:
        # 책 제목을 안전한 파일명으로 변환하고 .jpg 확장자를 붙입니다.
        filename = sanitize_name(title) + ".jpg"
        # 저장할 폴더와 파일명을 합쳐 전체 파일 경로를 만듭니다.
        file_path = os.path.join(folder, filename)
        # requests.get으로 이미지 URL에 GET 요청을 보냅니다. stream=True는 데이터를 한 번에 다 받지 않고 나눠서 받겠다는 의미입니다.
        response = requests.get(image_url, stream=True)
        # HTTP 요청이 실패했을 경우 (상태 코드가 4xx 또는 5xx) 예외를 발생시킵니다.
        response.raise_for_status()
        # 파일을 바이너리 쓰기 모드('wb')로 엽니다.
        with open(file_path, 'wb') as f:
            # 응답 내용을 1024바이트(1KB)씩 조각(chunk)내어 반복 처리합니다.
            for chunk in response.iter_content(1024):
                f.write(chunk)  # 각 조각을 파일에 씁니다.
        return file_path  # 저장된 파일의 경로를 반환합니다.
    except Exception as e:
        print(f"이미지 저장 실패! {e}")  # 예외 발생 시 에러 메시지를 출력합니다.
        return None  # 실패 시 None을 반환합니다.


# 교보문고 웹사이트를 크롤링하는 메인 함수
def crawl_kyobo(search_keyword, max_page=1):
    """
    주어진 검색어로 교보문고를 검색하여 지정된 페이지 수만큼 책 정보를 크롤링합니다.
    Args:
        search_keyword (str): 검색할 키워드
        max_page (int): 크롤링할 최대 페이지 수 (기본값 1)
    Returns:
        list: 크롤링된 책 정보 딕셔너리들의 리스트
    """
    # 이미지를 저장할 폴더를 지정합니다.
    folder = "images/kyobo"
    # os.makedirs를 사용하여 폴더를 생성합니다. exist_ok=True는 폴더가 이미 있어도 에러를 발생시키지 않습니다.
    os.makedirs(folder, exist_ok=True)
    # Chrome 브라우저 옵션을 설정합니다.
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 브라우저 창을 띄우지 않고 백그라운드에서 실행합니다.
    chrome_options.add_argument("--no-sandbox")  # 리눅스 시스템에서 root 계정으로 실행할 때 필요한 옵션입니다.
    chrome_options.add_argument("--disable-dev-shm-usage")  # 공유 메모리 사용을 비활성화하여 리소스 부족 문제를 방지합니다.
    # ChromeDriver를 자동으로 설치하고, 설정된 옵션으로 Chrome 브라우저를 실행합니다.
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    # 크롤링 결과를 저장할 리스트를 초기화합니다.
    results = []
    # 1페이지부터 max_page까지 반복합니다.
    for page in range(1, max_page + 1):
        # 검색어와 페이지 번호를 포함하는 URL을 생성합니다.
        # 참고: 원본 코드의 URL page 파라미터가 max_page로 고정되어 있어 현재 페이지(page)로 수정했습니다.
        url = f"https://search.kyobobook.co.kr/search?keyword={search_keyword}&page={page}"
        # Selenium driver를 사용하여 해당 URL로 이동합니다.
        driver.get(url)
        # 현재 페이지의 소스 코드를 가져와 BeautifulSoup 객체로 변환합니다.
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # CSS 선택자를 사용하여 책 목록 전체를 포함하는 요소를 선택합니다.
        books = soup.select('#shopData_list > ul > li')
        # 각 책에 대해 반복합니다.
        for book in books:
            try:
                # 책 제목, 저자, 가격 등의 정보를 CSS 선택자로 찾습니다.
                title_elem = book.select_one("div.prod_name_group")
                title = title_elem.text.strip() if title_elem else "제목없음"
                
                author = extract_text_safe(title, "저자", book.select_one("div.prod_author_info a"))
                price = extract_text_safe(title, "가격", book.select_one("span.price"))
                publisher = extract_text_safe(title, "출판사", book.select_one("div.prod_publish > a"))
                pub_date = extract_text_safe(title, "출판일", book.select_one("div.prod_publish > span.date"))
                
                # 이미지 태그(<img>)를 찾습니다.
                img_elem = book.select_one("img")
                # 이미지 태그가 존재하고 'src' 속성이 있으면 그 값을 image_url로 사용하고, 없으면 None으로 설정합니다.
                image_url = img_elem['src'] if img_elem and 'src' in img_elem.attrs else None
                print(f"이미지 URL: {image_url}")
                
                # 이미지 URL이 있으면 이미지를 저장하고, 없으면 None으로 설정합니다.
                local_image_path = save_image(image_url, folder, title) if image_url else None
                
                # 추출한 데이터를 딕셔너리 형태로 정리합니다.
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
                # MongoDB 컬렉션에 데이터를 삽입합니다.
                collection.insert_one(data)
                # 결과 리스트에도 데이터를 추가합니다.
                results.append(data)
            except Exception as e:
                # 개별 책 정보를 처리하다 에러가 발생하면 메시지를 출력하고 다음 책으로 넘어갑니다.
                print(f'[KYOBO] 처리 실패: {e}')

    # 크롤링이 끝나면 브라우저를 종료합니다.
    driver.quit()
    # 수집된 모든 결과를 반환합니다.
    return results

# 이 파일이 직접 실행될 때만 아래 코드를 실행합니다. (테스트용)
if __name__ == '__main__':
    # '파이썬'이라는 키워드로 1페이지만 크롤링을 실행하고 결과를 출력합니다.
    crawled_data = crawl_kyobo("파이썬", 1)
    print(f"총 {len(crawled_data)}개의 데이터를 수집했습니다.")
    print(crawled_data)
