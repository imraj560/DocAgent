# DocAgent — Multi-Agent Document Intelligence System

DocAgent is an AI-powered document question-answering system that allows users to upload documents and ask natural-language questions about their content.

The system combines **hybrid retrieval (BM25 + vector search)** with a **multi-agent LangGraph workflow** to improve answer relevance, generation, and verification.

Users can upload documents through the React frontend, ask questions, and receive answers generated strictly from the retrieved document context.

---

## 🚀 Features

- 📄 Upload and process documents 
- 🔎 Hybrid document retrieval using:
  - BM25 keyword search
  - Chroma vector similarity search
- 🧠 Multi-agent workflow powered by LangGraph
- 🎯 Relevance checking before answer generation
- ✍️ AI-powered answer generation
- ✅ Independent answer verification
- 🔄 Re-research loop when verification fails
- 📊 Token usage tracking
- 💰 LLM cost awareness
- 🔐 File validation and API security considerations
- ⚡ FastAPI backend
- ⚛️ React frontend
- ☁️ Deployable architecture using Netlify + Railway

---

# 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │     React UI        │
                    │      Netlify        │
                    └──────────┬──────────┘
                               │
                               │ HTTP / REST API
                               ▼
                    ┌─────────────────────┐
                    │     FastAPI API     │
                    │      Railway        │
                    └──────────┬──────────┘
                               │
                     ┌─────────┴─────────┐
                     │                   │
                     ▼                   ▼
              Document Upload       User Question
                     │                   │
                     ▼                   ▼
             Document Processor    Hybrid Retriever
                                         │
                              ┌──────────┴──────────┐
                              │                     │
                              ▼                     ▼
                           BM25                Chroma
                       Keyword Search       Vector Search
                              │                     │
                              └──────────┬──────────┘
                                         │
                                         ▼
                                Ensemble Retriever
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │   LangGraph         │
                              │   Agent Workflow    │
                              └──────────┬──────────┘
                                         │
                              ┌──────────┼──────────┐
                              ▼          ▼          ▼
                        Relevance    Research   Verification
                          Agent       Agent        Agent
                              │          │          │
                              └──────────┴──────────┘
                                         │
                                         ▼
                                   Final Answer
