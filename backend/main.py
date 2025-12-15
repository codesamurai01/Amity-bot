from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel, validator
from chat import get_response
import logging
from chat import router as chat_router
from embed_kb import embed_kb
import uuid
import kb_upload
from fastapi import Form

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Amity Bot API",
    description="Chat API for Amity University Bot",
    version="1.0.0"
)
app.include_router(chat_router)
app.include_router(kb_upload.router)

# Middleware
app.add_middleware(SessionMiddleware, secret_key="super-secret-key")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key="super-secret-key")

class ChatRequest(BaseModel):
    query: str

    @validator('query')
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        if len(v.strip()) > 1000:
            raise ValueError('Query too long (max 1000 characters)')
        return v.strip()

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

class ErrorResponse(BaseModel):
    detail: str
    status: str = "error"

def get_user_role(request: Request) -> str:
    return request.headers.get("X-User-Role", "general")

@app.get("/")
async def root():
    return {"message": "Amity Bot API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Amity Bot API",
        "version": "1.0.0"
    }

@app.post("/chat", response_model=ChatResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def chat_endpoint(request: Request, body: ChatRequest):
    try:
        session_id = request.session.get("session_id")
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session["session_id"] = session_id

        role = get_user_role(request)
        logger.info(f"Received query from role={role}: {body.query[:100]}...")

        answer = get_response(body.query, role=role)

        if not answer:
            raise HTTPException(status_code=500, detail="Failed to generate response")

        return ChatResponse(response=answer)

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error. Please try again later.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

users_db = {
    "admin": {"username": "admin", "password": "admin", "role": "logged_in"},
}
@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = users_db.get(username)
    if user and user["password"] == password:
        request.session["user"] = {"username": username, "role": user["role"]}
        return {"message": "Login successful", "role": user["role"]}
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/reindex")
async def reindex_kb():
    """
    Triggers re-embedding of the knowledge base (KB).
    Calls embed_kb.py via subprocess or directly via function.
    """
    try:
        # Option 1: Call the function directly if it's fast and safe
        embed_kb()
        return JSONResponse(content={"status": "success", "message": "Reindexing complete"})

        # OR Option 2: Call as a subprocess (if it's a heavy, blocking task)
        # result = subprocess.run(["python3", "embed_kb.py"], check=True, capture_output=True, text=True)
        # return JSONResponse(content={"status": "success", "output": result.stdout})

    except Exception as e:
        logger.error(f"Reindexing failed: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/check-session")
async def check_session(request: Request):
    user = request.session.get("user")
    role = user.get("role") if user else "general"
    return {"role": role}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
