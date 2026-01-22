from fastapi import FastAPI
from routers import auth, documents, chat
import os

app = FastAPI(title="Multi-User RAG API")

os.makedirs("data", exist_ok=True)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)

@app.get("/")
def read_root():
    return {"status": "API is running"}