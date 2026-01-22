# 🤖 DocTalk AI

**DocTalk AI** is a full-stack, multi-user RAG (Retrieval-Augmented Generation) application that allows users to securely upload documents and chat with them using AI. 

It is designed for **privacy and cost-efficiency**, utilizing **local LLMs (Ollama)** for processing and chat, meaning no API costs.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B)
![Ollama](https://img.shields.io/badge/AI-Ollama%20(Local)-000000)
![Supabase](https://img.shields.io/badge/Database-Supabase-3ECF8E)

## 🚀 Features

*   **🔐 Secure Authentication:** JWT-based Signup/Login with Argon2 password hashing.
*   **📂 Document Management:** Upload, view, and delete PDF/TXT files.
*   **🧠 Local AI Processing:** Uses **Ollama** (`nomic-embed-text` for embedding, `llama3.2` for chat).
*   **💾 Vector Search:** Each user has an isolated local ChromaDB vector store.
*   **📊 Professional UI:** Modern Streamlit dashboard with metric cards and custom navigation.
*   **💬 Citation Support:** Chat responses include exact page numbers and source citations.

---

## 🛠️ Tech Stack

*   **Frontend:** Streamlit, Custom CSS
*   **Backend:** FastAPI, Pydantic
*   **Database:** Supabase (PostgreSQL)
*   **Vector Store:** ChromaDB (Local persistence)
*   **AI/LLM orchestration:** LangChain
*   **Model Provider:** Ollama (Local)

---

## ⚙️ Setup Instructions

### 1. Prerequisites
*   **Python 3.11** (Recommended)
*   **Ollama** installed and running locally ([Download here](https://ollama.com)).
*   A **Supabase** project (Free tier).

### 2. Database Setup (Supabase)
Go to your Supabase SQL Editor and run these commands:

```sql
-- Enable UUIDs
create extension if not exists "uuid-ossp";

-- 1. Users Table
create table users (
  id uuid primary key default uuid_generate_v4(),
  email text unique not null,
  password_hash text not null,
  full_name text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 2. Documents Table
create table documents (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid references users(id) not null,
  filename text not null,
  file_path text not null,
  file_size integer,
  status text default 'uploaded',
  chunk_size integer,
  chunk_overlap integer,
  embedding_model text,
  uploaded_at timestamp with time zone default timezone('utc'::text, now()) not null,
  processed_at timestamp with time zone
);


### 3. Installation

Clone the repository:
```bash
git clone https://github.com/your-username/doctalk-ai.git
cd doctalk-ai
```

Create and activate a virtual environment:
```bash
# Windows
py -3.11 -m venv venv
.\venv\Scripts\activate

# Mac/Linux
python3.11 -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r backend/requirements.txt
pip install streamlit extra-streamlit-components
```

### 4. Setup Ollama Models
Run these commands in your terminal to download the required local models:
```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```
*Ensure Ollama is running in the background.*

### 5. Environment Variables
Create a `.env` file inside the `root/` folder:

```ini
# backend/.env

# Database (Supabase)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Security
SECRET_KEY=generate-a-random-secret-string-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## ▶️ How to Run

You need to run the Backend and Frontend in **two separate terminals**.

**Terminal 1: Backend**
```bash
# Make sure venv is active
uvicorn backend.main:app --reload
```
*Backend runs at: http://127.0.0.1:8000*

**Terminal 2: Frontend**
```bash
# Make sure venv is active
cd frontend
streamlit run home.py
```
*Frontend runs at: http://localhost:8501*

---

## 📸 Screenshots

*(You can add screenshots here later by dragging images into your GitHub issue/readme editor)*

## 🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License
[MIT](https://choosealicense.com/licenses/mit/)
```

### How to Push to GitHub
1.  Initialize Repo: `git init`
2.  Add files: `git add .`
3.  Commit: `git commit -m "Changing you made in DocTalk AI"`
4.  Link Repo: `git remote add origin https://github.com/m465/DocTalk.git`
5.  Push: `git push -u origin master`