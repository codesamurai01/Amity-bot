import os
import uuid
import shutil
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from embed_kb import embed_kb

from pdfplumber import open as pdf_open
from PIL import Image
import pytesseract

router = APIRouter()
UPLOAD_DIR = "data"

os.makedirs(UPLOAD_DIR, exist_ok=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/kb-upload")
async def upload_kb_file(file: UploadFile = File(...)):
    try:
        filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        # Save the uploaded file
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Extract text based on file type
        ext = file.filename.lower().split(".")[-1]
        if ext in ["txt", "md"]:
            # already plain text
            extracted_text = file_path

        elif ext == "pdf":
            extracted_text = extract_text_from_pdf(file_path)

        elif ext in ["jpg", "jpeg", "png"]:
            extracted_text = extract_text_from_image(file_path)

        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        # Save extracted text to .txt file in data/ directory
        if extracted_text:
            txt_file = file_path + ".txt"
            with open(txt_file, "w") as out:
                out.write(extracted_text)
            logger.info(f"Extracted and saved to: {txt_file}")
        else:
            raise HTTPException(status_code=400, detail="No text could be extracted")

        # Re-index knowledge base
        embed_kb()
        return JSONResponse(content={"message": "File uploaded and KB reindexed."})

    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

def extract_text_from_pdf(file_path: str) -> str:
    try:
        text = ""
        with pdf_open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        return ""

def extract_text_from_image(file_path: str) -> str:
    try:
        image = Image.open(file_path)
        return pytesseract.image_to_string(image)
    except Exception as e:
        logger.error(f"Image OCR failed: {e}")
        return ""
