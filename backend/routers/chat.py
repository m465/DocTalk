from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from utils.dependencies import get_current_user
import os

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    question: str
    model: str = "llama3.2"
    k: int = 5
    temperature: float = 0.7

@router.post("/query")
async def chat_query(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user['user_id']
    vector_store_path = f"data/user_{user_id}/vectorstore"

    if not os.path.exists(vector_store_path):
        raise HTTPException(status_code=400, detail="No documents processed yet.")

    try:
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        vector_store = Chroma(
            persist_directory=vector_store_path, 
            embedding_function=embeddings
        )

        retriever = vector_store.as_retriever(search_kwargs={"k": request.k})

        llm = ChatOllama(
            model="llama3.2", # Make sure you ran 'ollama pull llama3.2'
            temperature=request.temperature,
            base_url="http://localhost:11434" # Default local URL
        )

        prompt = ChatPromptTemplate.from_template("""
        Answer the user's question based ONLY on the following context. 
        If the answer is not in the context, say "I don't know".

        Context:
        {context}

        Question: 
        {input}
        """)

        document_chain = create_stuff_documents_chain(llm, prompt)
        
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        response = retrieval_chain.invoke({"input": request.question})

        sources = []
        if "context" in response:
            for doc in response["context"]:
                raw_content = doc.page_content
                clean_content = " ".join(raw_content.split())
                
                page_num = doc.metadata.get("page", 0) + 1
                
                sources.append({
                    "source": os.path.basename(doc.metadata.get("source", "Unknown")),
                    "page": page_num,
                    "content": clean_content
                })

        return {"answer": response["answer"], "sources": sources}


    except Exception as e:
        print(f"Chat Error: {e}")
        if "Connection refused" in str(e):
             raise HTTPException(status_code=500, detail="Ollama is not running. Please run 'ollama serve' or open the Ollama app.")
        raise HTTPException(status_code=500, detail=str(e))