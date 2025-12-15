import os
import logging
from pathlib import Path
from typing import List
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "chroma_db")
DATA_DIR = os.getenv("DATA_DIR", "data")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))  # Increased for better context
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))  # Increased overlap
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

def ensure_directories_exist():
    """Ensure required directories exist"""
    try:
        Path(DATA_DIR).mkdir(exist_ok=True)
        Path(CHROMA_DB_DIR).mkdir(exist_ok=True)
        logger.info(f"Directories ensured: {DATA_DIR}, {CHROMA_DB_DIR}")
    except Exception as e:
        logger.error(f"Error creating directories: {e}")
        raise

def load_documents() -> List[Document]:
    """Load documents from the data directory"""
    logger.info("📁 Loading documents...")
    
    # Check if data directory exists
    if not os.path.exists(DATA_DIR):
        logger.error(f"❌ Data directory '{DATA_DIR}' not found.")
        return []
    
    # Define loaders for different file types
    loaders = []
    
    # Text files
    try:
        txt_loader = DirectoryLoader(
            DATA_DIR,
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        loaders.append(("TXT", txt_loader))
    except Exception as e:
        logger.warning(f"Could not set up TXT loader: {e}")
    
    # PDF files
    try:
        pdf_loader = DirectoryLoader(
            DATA_DIR,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader
        )
        loaders.append(("PDF", pdf_loader))
    except Exception as e:
        logger.warning(f"Could not set up PDF loader: {e}")
    
    # Load documents
    docs = []
    for file_type, loader in loaders:
        try:
            loaded_docs = loader.load()
            docs.extend(loaded_docs)
            logger.info(f"📄 Loaded {len(loaded_docs)} {file_type} documents")
        except Exception as e:
            logger.error(f"Error loading {file_type} documents: {e}")
    
    logger.info(f"📄 Total documents loaded: {len(docs)}")
    
    # Log document sources
    if docs:
        sources = set()
        for doc in docs:
            if hasattr(doc, 'metadata') and 'source' in doc.metadata:
                sources.add(doc.metadata['source'])
        logger.info(f"📂 Document sources: {list(sources)}")
    
    return docs

# #EMBED_KB
def embed_kb():
    documents = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".txt"):
            loader = TextLoader(os.path.join(DATA_DIR, filename))
            documents.extend(loader.load())

    embeddings = HuggingFaceEmbeddings(model_name= EMBEDDING_MODEL)

    vectorstore = Chroma.from_documents(
        documents,
        embeddings,
        persist_directory="chroma_db"
    )
    vectorstore.persist()

def embed_kb():
    all_files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.endswith(".txt") or f.endswith(".md")]
    documents = []
    for file_path in all_files:
        loader = TextLoader(file_path)
        documents.extend(loader.load())
    vectorstore = Chroma.from_documents(documents, HuggingFaceEmbeddings(), persist_directory="chroma_db")
    vectorstore.persist()

def clean_document_content(documents: List[Document]) -> List[Document]:
    """Clean and preprocess document content"""
    logger.info("🧹 Cleaning document content...")
    
    cleaned_docs = []
    for doc in documents:
        # Clean the content
        content = doc.page_content
        
        # Remove excessive whitespace
        content = ' '.join(content.split())
        
        # Skip very short documents
        if len(content.strip()) < 50:
            logger.warning(f"Skipping short document: {content[:50]}...")
            continue
        
        # Update document content
        doc.page_content = content
        cleaned_docs.append(doc)
    
    logger.info(f"🧹 Cleaned documents: {len(cleaned_docs)} (removed {len(documents) - len(cleaned_docs)} short docs)")
    return cleaned_docs

def split_documents(documents: List[Document]) -> List[Document]:
    """Split documents into chunks"""
    logger.info("🔪 Splitting documents into chunks...")
    
    if not documents:
        logger.warning("No documents to split")
        return []
    
    try:
        # Initialize splitter with better parameters
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]  # Better separators
        )
        
        chunks = splitter.split_documents(documents)
        logger.info(f"🔢 Total chunks after splitting: {len(chunks)}")
        
        # Log chunk statistics
        if chunks:
            chunk_lengths = [len(chunk.page_content) for chunk in chunks]
            avg_length = sum(chunk_lengths) / len(chunk_lengths)
            logger.info(f"📊 Average chunk length: {avg_length:.0f} characters")
            
            # Preview first 2 chunks
            logger.info("📖 Preview of chunks:")
            for i, chunk in enumerate(chunks[:2]):
                preview = chunk.page_content[:200] + "..." if len(chunk.page_content) > 200 else chunk.page_content
                logger.info(f"--- Chunk {i+1} ---\n{preview}\n")
        
        return chunks
        
    except Exception as e:
        logger.error(f"Error splitting documents: {e}")
        return []

def initialize_embeddings():
    """Initialize the embedding model"""
    logger.info("🔐 Initializing embedding model...")
    
    try:
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        logger.info(f"✅ Embedding model '{EMBEDDING_MODEL}' initialized successfully")
        return embeddings
    except Exception as e:
        logger.error(f"❌ Failed to initialize embedding model: {e}")
        raise

def create_vectorstore(chunks: List[Document], embeddings) -> Chroma:
    """Create and persist the vector store"""
    logger.info("📦 Creating Chroma vectorstore...")
    
    try:
        # Remove existing vectorstore if it exists
        if os.path.exists(CHROMA_DB_DIR):
            import shutil
            shutil.rmtree(CHROMA_DB_DIR)
            logger.info(f"🗑️ Removed existing vectorstore at {CHROMA_DB_DIR}")
        
        # Create new vectorstore
        vectordb = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=CHROMA_DB_DIR,
        )
        
        # The new version doesn't need explicit persist() call
        logger.info(f"✅ Vectorstore created and saved to {CHROMA_DB_DIR}")
        
        # Verify the vectorstore
        collection_count = vectordb._collection.count()
        logger.info(f"📊 Vectorstore contains {collection_count} embeddings")
        
        return vectordb
        
    except Exception as e:
        logger.error(f"❌ Failed to create vectorstore: {e}")
        raise

def test_vectorstore(vectordb: Chroma):
    """Test the created vectorstore"""
    logger.info("🧪 Testing vectorstore...")
    
    try:
        # Test similarity search
        test_query = "What is Amity University?"
        results = vectordb.similarity_search(test_query, k=3)
        
        if results:
            logger.info(f"✅ Vectorstore test successful! Found {len(results)} results for test query")
            logger.info(f"📝 Sample result: {results[0].page_content[:100]}...")
        else:
            logger.warning("⚠️ Vectorstore test returned no results")
            
    except Exception as e:
        logger.error(f"❌ Vectorstore test failed: {e}")

def embed_kb():
    """Main function to embed knowledge base"""
    try:
        logger.info("🚀 Starting knowledge base embedding process...")
        
        # Ensure directories exist
        ensure_directories_exist()
        
        # Load documents
        documents = load_documents()
        if not documents:
            logger.error("❌ No documents found. Please add documents to the data directory.")
            return False
        
        # Clean documents
        documents = clean_document_content(documents)
        if not documents:
            logger.error("❌ No valid documents after cleaning.")
            return False
        
        # Split documents
        chunks = split_documents(documents)
        if not chunks:
            logger.error("⚠️ No content to embed after splitting. Exiting.")
            return False
        
        # Initialize embeddings
        embeddings = initialize_embeddings()
        
        # Create vectorstore
        vectordb = create_vectorstore(chunks, embeddings)
        
        # Test vectorstore
        test_vectorstore(vectordb)
        
        logger.info("✅ Knowledge base embedding completed successfully!")
        logger.info(f"📍 Vector database saved to: {os.path.abspath(CHROMA_DB_DIR)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Knowledge base embedding failed: {e}")
        return False

if __name__ == "__main__":
    success = embed_kb()
    if not success:
        exit(1)
