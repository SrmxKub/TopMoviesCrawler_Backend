# 🎬 Top Movies Crawler

A simple **FastAPI Web Crawler** for fetching and searching top movies.


## 🚀 Features
- Crawl top movies with title, year, genres, and description  
- Search movies by name or genre  
- Interactive API docs at `/docs` (Swagger UI)  


## 📦 Installation

**1. Clone the repository**
```bash
git clone https://github.com/SrmxKub/top-movies-crawler.git
```

**2. Navigate into the backend folder**
```bash
cd backend
```

**3. Create and active a virtual environment**
If you already have Python 3.11+ installed, you can skip this step.
```bash
python3 -m venv venv

source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

**5. Install dependencies**
```bash
pip install -r requirements.txt
```

**6. Start the FastAPI server**
```bash
uvicorn app.main:app --reload
```


## 📡 API Endpoints
- GET  /movies/search?name=Inception&genre=Action
- POST /movies/update


## 🛠️ Tech Stack
- Python 3.11+
- FastAPI + Uvicorn
- Pydantic v2
