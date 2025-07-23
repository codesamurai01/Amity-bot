import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain_core.documents import Document
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Load Chroma and retriever
embedding = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-en-v1.5")
db = Chroma(persist_directory="./chroma_db", embedding_function=embedding)
retriever = db.as_retriever(search_type="similarity", k=5)

# Prompt Template
RAG_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are AmityBot, an internal support assistant. Answer clearly using the context.

Context:
{context}

Question:
{question}

Answer:"""
)

# LLM call with Groq
def call_llm(prompt: str) -> str:
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        model="mixtral-8x7b-32768"  # or "llama3-70b-8192" if preferred
    )
    return chat_completion.choices[0].message.content.strip()

# RAG chain
def get_response(query: str) -> str:
    docs: list[Document] = retriever.get_relevant_documents(query)
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = RAG_PROMPT.format(context=context, question=query)
    response = call_llm(prompt)
    return response
