import os
import logging
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain.prompts import PromptTemplate
from groq import Groq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import List, Tuple, Literal
from uuid import uuid4
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi import Form

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables")

client = Groq(api_key=groq_api_key)

# Load embedding model and database
try:
    logger.info("Loading vector database...")
    embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    db = Chroma(persist_directory="./chroma_db", embedding_function=embedding)
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    logger.info("Vector database loaded.")
except Exception as e:
    logger.error(f"Failed to load vector DB: {e}")
    raise

# Prompt Template
RAG_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are AmityBot, a helpful and knowledgeable assistant for Amity University. 
Your role is to provide accurate, helpful, and friendly responses to questions about the university.

Guidelines:
- Use the provided context to answer questions accurately
- If the context doesn't contain enough information, say so politely
- Be conversational and helpful
- Provide specific details when available
- If asked about something not related to Amity University, gently redirect to university-related topics

Context Information:
{context}

Question: {question}

Answer:"""
)

def call_llm(prompt: str) -> str:
    try:
        logger.info("Calling LLM...")
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are AmityBot, a helpful assistant for Amity University. Provide accurate, friendly, and informative responses."
                },
                {"role": "user", "content": prompt}
            ],
            model="compound-beta",
            temperature=0.7,
            max_tokens=1000,
            top_p=0.9
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"LLM error: {e}")
        return "Sorry, something went wrong with my response. Please try again."

def get_response(query: str, role: str) -> str:
    try:
        if not query or not query.strip():
            return "Please provide a valid question."

        query = query.strip()
        logger.info(f"Processing query: {query[:100]}...")

        docs: List[Document] = retriever.invoke(query)

        if role == "general":
            # Limit access or context depth for general users
            docs = docs[:2]  # Limit to top 2 docs
        elif role == "logged_in":
            # Logged-in users get full context
            docs = docs[:5]  # Or more access/tools

        context = "\n\n".join([doc.page_content for doc in docs])
        if len(context) > 3000:
            context = context[:3000] + "..."
        if not context:
            context = "No specific information found in the database."

        prompt = RAG_PROMPT.format(context=context, question=query)
        return call_llm(prompt)

    except Exception as e:
        logger.error(f"Error in get_response: {e}")
        return "I apologize, but I encountered an error while processing your question."


# Health check util (optional)
def health_check() -> bool:
    try:
        retriever.invoke("hello")
        call_llm("Ping.")
        return True
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False

# Session memory (in-memory only for now)
sessions = {}

class ChatRequest(BaseModel):
    query: str
    session_id: str
    chat_history: List[Tuple[str, str]]
    role: Literal["general", "logged_in"] = "general"

@router.post("/chat")
async def chat(request: ChatRequest):
    """
    RAG-based chat endpoint with session tracking and role access.
    Supports concurrency.
    """
    try:
        session_id = request.session_id or str(uuid4())
        sessions.setdefault(session_id, request.chat_history)

        response = await run_in_threadpool(get_response, request.query, request.role)

        sessions[session_id].append((request.query, response))

        return {
            "session_id": session_id,
            "result": response,
            "source_docs": []  # Could be populated with metadata later
        }
    except Exception as e:
        logger.error(f"Chat failure: {e}")
        return {
            "result": "An error occurred while processing your request.",
            "source_docs": []
        }

users = {
    "admin": "admin123",
    "student": "amity@2025"
}

@router.post("/register")
async def register(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in users:
        return JSONResponse(status_code=400, content={"message": "User already exists"})

    users[username] = password
    sessions[username] = "logged_in"
    request.session["user"] = username
    request.session["role"] = "logged_in"
    return {"message": "User registered", "role": "logged_in"}
