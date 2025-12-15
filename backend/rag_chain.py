import os
import re
import logging
from typing import Generator, Dict, Any
from dotenv import load_dotenv
from crm_client import get_lead_status  # Import from your existing file
from langchain_chroma import Chroma  # Updated import
from langchain_huggingface import HuggingFaceEmbeddings  # Updated import
from groq import Groq  # Use official Groq client instead of requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "chroma_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

# Validate API key
if not GROQ_API_KEY:
    logger.error("GROQ_API_KEY not found in environment variables")
    raise ValueError("GROQ_API_KEY is required")

# Initialize Groq client
try:
    groq_client = Groq(api_key=GROQ_API_KEY)
    logger.info("Groq client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    raise

# Initialize embeddings and vectorstore
try:
    logger.info("Initializing vectorstore...")
    embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embedding_function
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    logger.info("Vectorstore initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize vectorstore: {e}")
    vectorstore = None
    retriever = None

def extract_lead_id(question: str) -> str:
    """Extract lead ID from question using regex"""
    patterns = [
        r"lead\s*#?(\d+)",
        r"#(\d+)",
        r"id\s*#?(\d+)",
        r"(\d{3,})"  # Any number with 3+ digits
    ]
    
    question_lower = question.lower()
    for pattern in patterns:
        match = re.search(pattern, question_lower)
        if match:
            return match.group(1)
    return None

def handle_lead_query(question: str) -> Generator[str, None, None]:
    """Handle lead status queries"""
    lead_id = extract_lead_id(question)
    
    if not lead_id:
        yield "I couldn't find a lead ID in your question. Please provide a lead ID like 'lead #123' or just '123'.\n"
        return
    
    try:
        logger.info(f"Retrieving lead status for ID: {lead_id}")
        lead_info = get_lead_status(lead_id)
        
        if lead_info.get("error"):
            yield f"❌ {lead_info.get('message', 'Lead not found')}\n"
            return
        
        # Format lead information nicely
        response = f"📋 **Lead Information for #{lead_id}**\n\n"
        response += f"👤 **Name:** {lead_info.get('name', 'N/A')}\n"
        response += f"📊 **Status:** {lead_info.get('status', 'N/A')}\n"
        
        if lead_info.get('email'):
            response += f"📧 **Email:** {lead_info.get('email')}\n"
        
        if lead_info.get('phone'):
            response += f"📱 **Phone:** {lead_info.get('phone')}\n"
        
        if lead_info.get('course_interest'):
            response += f"🎓 **Course Interest:** {lead_info.get('course_interest')}\n"
        
        if lead_info.get('assigned_counselor'):
            response += f"👨‍💼 **Assigned Counselor:** {lead_info.get('assigned_counselor')}\n"
        
        if lead_info.get('last_contact'):
            response += f"📅 **Last Contact:** {lead_info.get('last_contact')}\n"
        
        if lead_info.get('notes'):
            response += f"📝 **Notes:** {lead_info.get('notes')}\n"
        
        yield response
        
    except Exception as e:
        logger.error(f"Error handling lead query: {e}")
        yield f"❌ An error occurred while retrieving lead information: {str(e)}\n"

def get_context_from_vectorstore(question: str) -> str:
    """Retrieve relevant context from vectorstore"""
    if not retriever:
        logger.warning("Vectorstore not available")
        return "Sorry, the knowledge base is not available at the moment."
    
    try:
        logger.info(f"Searching vectorstore for: {question[:50]}...")
        docs = retriever.invoke(question)  # Updated method name
        
        if not docs:
            logger.warning("No relevant documents found")
            return "No relevant information found in the knowledge base."
        
        # Combine top documents
        context = "\n\n".join([doc.page_content for doc in docs[:3]])
        logger.info(f"Retrieved {len(docs)} documents for context")
        
        return context
        
    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        return "Error retrieving information from knowledge base."

def call_groq_streaming(prompt: str) -> Generator[str, None, None]:
    """Call Groq API with streaming response"""
    try:
        logger.info("Making streaming call to Groq API...")
        
        # Create chat completion with streaming
        stream = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": """You are AmityBot, a helpful and knowledgeable assistant for Amity University. 
                    Provide accurate, friendly, and informative responses. Use the context provided to answer questions accurately.
                    If you don't have enough information, say so politely."""
                },
                {"role": "user", "content": prompt}
            ],
            model=GROQ_MODEL,
            temperature=0.7,
            max_tokens=1000,
            stream=True
        )
        
        # Stream the response
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
                
        logger.info("Groq API call completed successfully")
        
    except Exception as e:
        logger.error(f"Error calling Groq API: {e}")
        yield f"❌ Sorry, I encountered an error while processing your request: {str(e)}"

def is_lead_related_query(question: str) -> bool:
    """Check if the question is related to lead status"""
    lead_keywords = [
        "lead", "leads", "status", "customer", "prospect", 
        "enquiry", "inquiry", "application", "student id",
        "registration", "admission"
    ]
    
    question_lower = question.lower()
    
    # Check for lead keywords AND numbers (potential lead IDs)
    has_keyword = any(keyword in question_lower for keyword in lead_keywords)
    has_number = bool(re.search(r'\d+', question))
    
    return has_keyword and has_number

def ask_question(question: str) -> Generator[str, None, None]:
    """
    Main function to handle questions with RAG and lead status functionality
    
    Args:
        question (str): User's question
        
    Yields:
        str: Streaming response chunks
    """
    try:
        # Validate input
        if not question or not question.strip():
            yield "Please provide a valid question.\n"
            return
        
        question = question.strip()
        logger.info(f"Processing question: {question[:100]}...")
        
        # Handle lead-related queries
        if is_lead_related_query(question):
            logger.info("Detected lead-related query")
            yield from handle_lead_query(question)
            return
        
        # Handle general queries with RAG
        logger.info("Processing general query with RAG")
        
        # Get context from vectorstore
        context = get_context_from_vectorstore(question)
        
        # Compose enhanced prompt
        prompt = f"""You are AmityBot, a helpful assistant for Amity University. Use the context below to answer the user's question accurately and helpfully.

Context from Knowledge Base:
{context}

User Question: {question}

Instructions:
- Provide a clear and helpful answer based on the context
- If the context doesn't contain enough information, acknowledge this
- Be conversational and friendly
- Focus on being helpful to students and prospective students

Answer:"""
        
        # Stream response from Groq
        yield from call_groq_streaming(prompt)
        
    except Exception as e:
        logger.error(f"Error in ask_question: {e}")
        yield f"❌ I apologize, but I encountered an error while processing your question. Please try again or contact support if the issue persists."

def health_check() -> Dict[str, Any]:
    """Check the health of all components"""
    status = {
        "groq_client": False,
        "vectorstore": False,
        "overall": False
    }
    
    try:
        # Test Groq client
        test_response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": "Hello"}],
            model=GROQ_MODEL,
            max_tokens=10
        )
        status["groq_client"] = bool(test_response.choices[0].message.content)
        
    except Exception as e:
        logger.error(f"Groq client health check failed: {e}")
    
    try:
        # Test vectorstore
        if retriever:
            test_docs = retriever.invoke("test")
            status["vectorstore"] = True
        
    except Exception as e:
        logger.error(f"Vectorstore health check failed: {e}")
    
    status["overall"] = status["groq_client"] and status["vectorstore"]
    return status

# Example usage and testing
if __name__ == "__main__":
    # Test the system
    print("Testing RAG Chain...")
    
    # Test health check
    health = health_check()
    print(f"Health Check: {health}")
    
    # Test general query
    print("\n--- Testing General Query ---")
    for chunk in ask_question("What is Amity University?"):
        print(chunk, end="")
    
    # Test lead query
    print("\n\n--- Testing Lead Query ---")
    for chunk in ask_question("What is the status of lead #123?"):
        print(chunk, end="")
    
    print("\n\nTesting completed!")
