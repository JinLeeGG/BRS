# Kyobo Book Recommendation System using web crawling and openAI

A toy project that crawls book information from the Kyobo bookstore website and provides AI-powered book recommendations through a web interface.

## 🚀 Features

- **Web Crawling**: Automated crawling of book data from Kyobo website using Selenium
- **Book Search**: Search for books by keyword with automatic data collection
- **AI Recommendations**: GPT-powered book recommendations based on user preferences
- **Web Interface**: User-friendly Gradio interface for easy interaction
- **REST API**: FastAPI backend with RESTful endpoints
- **Data Persistence**: MongoDB storage for crawled book information
- **Image Handling**: Automatic book cover image download and display

## 🛠 Tech Stack

- **Backend**: FastAPI
- **Frontend**: Gradio
- **Database**: MongoDB
- **Web Crawling**: Selenium + BeautifulSoup
- **AI Integration**: OpenAI GPT API
- **Image Processing**: PIL (Pillow)
- **Environment Management**: python-dotenv

## 📋 Prerequisites

- Python 3.7+
- MongoDB instance (local or cloud)
- OpenAI API key
- Chrome browser (for Selenium WebDriver)

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Kyobo-book-recommender
   ```

2. **Install dependencies**
   ```bash
   pip install fastapi uvicorn openai pymongo python-dotenv selenium webdriver-manager beautifulsoup4 gradio pillow requests
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   API_KEY=your_openai_api_key_here
   MONGODB=your_mongodb_connection_string_here
   ```

4. **Ensure MongoDB is running**
   - The application will automatically create a database named `book_db` with collection `kyobo_books`

## 🚀 Usage

### Method 1: Full Application (Recommended)

1. **Start the FastAPI backend**
   ```bash
   uvicorn main:app --reload
   ```

2. **Launch the Gradio interface** (in a new terminal)
   ```bash
   python gradio_app.py
   ```

3. **Access the web interface**
   - Open your browser and go to the Gradio interface URL (usually displayed in terminal)
   - Enter a search keyword (e.g., "파이썬")
   - Click "도서 목록 불러오기" to fetch books
   - Select a book from the dropdown
   - Click "GPT 추천 받기" to get AI recommendations

### Method 2: API Only

Start the FastAPI server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## 📡 API Endpoints

### 1. Get Books by Keyword

**Endpoint**: `GET /books`

**Parameters**:
- `keyword` (optional, default: "파이썬"): Search term for books

**Example**:
```bash
curl "http://localhost:8000/books?keyword=파이썬"
```

**Response**: List of book objects with details like title, author, price, publisher, etc.

### 2. Get Book Recommendations

**Endpoint**: `GET /recommend`

**Parameters**:
- `title` (required): Book title to base recommendations on
- `keyword` (optional, default: "파이썬"): Search context

**Example**:
```bash
curl "http://localhost:8000/recommend?title=파이썬 프로그래밍&keyword=파이썬"
```

## 📁 Project Structure

```
├── main.py              # FastAPI application with API endpoints
├── crawler.py           # Kyobo website crawler using Selenium
├── gradio_app.py        # Gradio web interface
├── .env                 # Environment variables (API keys, DB connection)
├── images/              # Directory for downloaded book cover images
│   └── kyobo/          # Subdirectory for image storage
└── README.md           # This file
```

## 🏗 System Architecture

The system follows a multi-layered architecture with clear separation of concerns:

```
┌─────────────┐    HTTP Requests   ┌─────────────┐    OpenAI API   ┌─────────────┐
│   Gradio    │◄──────────────────►│   FastAPI   │◄───────────────►│   GPT API   │
│  Frontend   │                    │   Backend   │                 │             │
└─────────────┘                    └─────────────┘                 └─────────────┘
                                           │
                                           │ MongoDB Operations
                                           ▼
                                   ┌─────────────┐    Selenium     ┌─────────────┐
                                   │   MongoDB   │                 │    Web      │
                                   │  Database   │◄───────────────►│  Crawler    │
                                   └─────────────┘                 └─────────────┘
```

### Component Interactions

1. **Gradio Frontend** ↔ **FastAPI Backend**
   - User interactions through web interface
   - HTTP requests for book search and recommendations
   - Real-time data updates and image display

2. **FastAPI Backend** ↔ **GPT API**
   - AI-powered book recommendation requests
   - Natural language processing for personalized suggestions

3. **FastAPI Backend** ↔ **MongoDB Database**
   - Book data storage and retrieval
   - Query optimization for fast searches
   - Automatic data validation

4. **Web Crawler** ↔ **MongoDB Database**
   - Automated data collection from Kyobo
   - Data parsing and storage
   - Image download and local storage

### Data Flow

1. **User Search Request**: User enters keyword in Gradio interface
2. **API Call**: Gradio sends HTTP request to FastAPI `/books` endpoint
3. **Database Query**: FastAPI queries MongoDB for existing data
4. **Auto-Crawling**: If no data exists, triggers Kyobo crawler
5. **Data Storage**: Crawler saves book information and images to MongoDB
6. **Response**: FastAPI returns book list to Gradio interface
7. **Recommendation**: User selects book and requests GPT recommendation
8. **AI Processing**: FastAPI calls OpenAI API for personalized suggestions
9. **Result Display**: Recommendation and book image shown in Gradio interface

## 🔧 Key Components

### main.py
- FastAPI application setup
- MongoDB connection and operations
- API endpoints for book search and recommendations
- Integration with crawler when data is not available

### crawler.py
- Selenium-based web scraping of Kyobo bookstore
- BeautifulSoup for HTML parsing
- Image downloading and local storage
- Data sanitization and MongoDB insertion

### gradio_app.py
- User-friendly web interface
- Real-time book search and selection
- AI recommendation display with book images
- Integration with FastAPI backend

## 🗄 Database Schema

Books are stored in MongoDB with the following structure:
```json
{
  "검색어": "파이썬",
  "책제목": "파이썬 프로그래밍",
  "저자": "저자명",
  "가격": "25,000원",
  "출판사": "출판사명",
  "출판일": "2024-01-01",
  "이미지저장경로": "/path/to/image.jpg",
  "판매사이트명": "Kyobo"
}
```

## ⚙️ Configuration

### Crawler Settings
- Default crawling: 3 pages per search
- Headless Chrome browser for better performance
- Automatic image download and storage
- Error handling for missing data

### API Settings
- Default search keyword: "파이썬"
- Automatic crawling when data is unavailable
- RESTful API design with proper error handling

## 🚨 Important Notes

- This is a **toy project** for educational purposes
- Respect the website's robots.txt and terms of service
- Use appropriate delays between requests to avoid overwhelming the server
- The crawler uses headless Chrome, so ensure Chrome is installed on your system

## 🐛 Troubleshooting

1. **ChromeDriver Issues**: The project uses `webdriver-manager` to automatically manage ChromeDriver
2. **MongoDB Connection**: Ensure your MongoDB connection string in `.env` is correct
3. **OpenAI API**: Verify your API key is valid and has sufficient credits
4. **Image Loading**: Check that the `images/kyobo/` directory has proper write permissions

## 📝 License

This project is for educational purposes only. Please respect the terms of service of the websites being crawled.

## 🤝 Contributing

This is a toy project, but feel free to fork and experiment with the code for your own learning purposes!
