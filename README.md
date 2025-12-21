# AMITYBOT V1 – CRM-Grounded RAG Assistant

## Overview
AMITYBOT V1 is a **proof-of-concept AI assistant** built around a **CRM-grounded Retrieval-Augmented Generation (RAG)** pipeline with a **minimal yet functional Admin UI**. The system enables non-technical users to import leads, manage knowledge base articles, trigger re-indexing, and query CRM-backed data through a conversational interface.

The project is designed for **stakeholder demos, internal feedback, and iteration**, with a clear separation between backend RAG logic and frontend admin tooling.

---

## System Capabilities

### Core RAG Backend (PoC)
- FastAPI-based backend with streaming chat responses (SSE)
- CRM-grounded answers using mock lead data
- Chroma vector database for knowledge storage
- Conversational RAG chain with tool calling
- Source-grounded responses with cited excerpts
- CLI demo client for quick testing

### Admin UI (MVP)
- Next.js 14 admin dashboard
- Role-protected access (Admin / Editor)
- Global navigation sidebar:
  - Leads
  - Knowledge Base
  - Sync Logs
- Read-only leads table with server-side pagination
- Knowledge Base editor with Markdown support
- CSV-based bulk lead import
- Manual re-index trigger with toast feedback
- Sync logs visibility for re-embedding jobs

### Governance & Polish
- Inline lead editing via drawer
- RBAC using NextAuth role claims
- Zod-based form validation
- Dark mode support
- Skeleton loaders and empty states
- Audit history per lead (mock timeline)
- End-to-end smoke tests and load testing
- Demo recording and setup documentation

---

## Tech Stack

### Backend
- FastAPI
- Python
- ChromaDB (Vector Store)
- RAG pipeline (Conversational Retrieval + Tools)
- Server-Sent Events (Streaming responses)

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- shadcn/ui
- React Server Components
- DataGrid for tabular views

### Tooling
- Git mono-repo
- CLI demo client
- Zod for validation
- NextAuth for RBAC
- Load testing (parallel query simulation)

---

## Key API Endpoints

### Chat & RAG
- `POST /chat` – CRM-grounded conversational endpoint (streaming)

### Leads
- `GET /crm/leads`
- `POST /crm/leads/bulk`
- `PATCH /crm/leads/:id`

### Knowledge Base
- `POST /kb/upload`
- `POST /kb/reindex`

---

## Running the Project

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
###Admin UI
```bash
cd admin-ui
npm install
npm run dev
```

###Admin UI runs on:
http://localhost:3000
