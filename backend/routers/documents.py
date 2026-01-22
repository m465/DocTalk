from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from utils.processing import get_user_vector_store_path
from utils.processing import process_document_logic
from utils.dependencies import get_current_user
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from pydantic import BaseModel
from utils.db import supabase
from typing import List
import shutil
import os

router = APIRouter(prefix="/documents", tags=["Documents"])

class ProcessRequest(BaseModel):
    document_id: str
    chunk_size: int = 1000
    chunk_overlap: int = 200

@router.get("/")
async def list_documents(current_user: dict = Depends(get_current_user)):
    """List all documents for the logged-in user"""
    try:
        response = supabase.table("documents")\
            .select("*")\
            .eq("user_id", current_user['user_id'])\
            .execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_document(
    files: List[UploadFile] = File(...), 
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user['user_id']
    
    base_path = f"data/user_{user_id}/documents"
    
    os.makedirs(base_path, exist_ok=True)
    
    uploaded_files_info = []

    for file in files:
        file_location = f"{base_path}/{file.filename}"
        
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        doc_data = {
            "user_id": user_id,
            "filename": file.filename,
            "file_path": file_location,
            "file_size": os.path.getsize(file_location),
            "status": "uploaded"
        }
        
        try:
            response = supabase.table("documents").insert(doc_data).execute()
            uploaded_files_info.append(response.data[0])
        except Exception as e:
            # If DB insert fails, cleanup file
            os.remove(file_location)
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {"message": "Files uploaded successfully", "documents": uploaded_files_info}

@router.post("/process")
async def process_document_endpoint(
    request: ProcessRequest,
    current_user: dict = Depends(get_current_user)
):
    # 1. Verify document belongs to user
    response = supabase.table("documents")\
        .select("*")\
        .eq("id", request.document_id)\
        .eq("user_id", current_user['user_id'])\
        .execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = response.data[0]
    
    # 2. Trigger Processing
    try:
        result = await process_document_logic(
            user_id=current_user['user_id'],
            document_id=request.document_id,
            file_path=doc['file_path'],
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))        


@router.delete("/{doc_id}")
async def delete_document(doc_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user['user_id']
    
    # 1. Fetch document info to find path
    response = supabase.table("documents")\
        .select("*")\
        .eq("id", doc_id)\
        .eq("user_id", user_id)\
        .execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = response.data[0]
    
    # 2. Delete file from local disk
    if os.path.exists(doc['file_path']):
        try:
            os.remove(doc['file_path'])
        except Exception as e:
            print(f"Error deleting file: {e}")

    # 3. Delete embeddings from ChromaDB
    try:
        vector_store_path = get_user_vector_store_path(user_id)
        if os.path.exists(vector_store_path):
            embeddings = OllamaEmbeddings(model="nomic-embed-text")
            vector_store = Chroma(
                persist_directory=vector_store_path, 
                embedding_function=embeddings
            )
            vector_store._collection.delete(where={"document_id": doc_id})
    except Exception as e:
        print(f"Error deleting embeddings: {e}")

    supabase.table("documents").delete().eq("id", doc_id).execute()

    return {"message": "Document deleted successfully"}        