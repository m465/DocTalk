import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from utils.db import supabase

def get_user_vector_store_path(user_id: str) -> str:
    return f"data/user_{user_id}/vectorstore"

async def process_document_logic(
    user_id: str, 
    document_id: str, 
    file_path: str, 
    chunk_size: int = 1000, 
    chunk_overlap: int = 200
):
    """
    1. Load document
    2. Split text
    3. Generate Embeddings
    4. Store in ChromaDB
    5. Update Supabase status
    """
    
    # 1. Update status to 'processing'
    supabase.table("documents").update({"status": "processing"}).eq("id", document_id).execute()

    try:
        # 2. Extract Text based on file type
        if file_path.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith(".txt"):
            loader = TextLoader(file_path)
        else:
            raise ValueError("Unsupported file type")
            
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        splits = text_splitter.split_documents(docs)

        for split in splits:
            split.metadata["user_id"] = user_id
            split.metadata["document_id"] = document_id
            split.metadata["source"] = os.path.basename(file_path)

        persist_directory = get_user_vector_store_path(user_id)
        
        embedding_function = OllamaEmbeddings(model="nomic-embed-text")
        Chroma.from_documents(
            documents=splits,
            embedding=embedding_function,
            persist_directory=persist_directory
        )

        supabase.table("documents").update({
            "status": "processed",
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "embedding_model": "ollama-nomic"
        }).eq("id", document_id).execute()
        
        return {"status": "success", "chunks_created": len(splits)}

    except Exception as e:
        supabase.table("documents").update({"status": "failed"}).eq("id", document_id).execute()
        print(f"Error processing document: {e}")
        raise e