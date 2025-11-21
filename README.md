Perfect — here’s a well-structured, developer-friendly `README.md` for your **RAG Search Assistant** project.
It’s concise enough for GitHub, but detailed enough for anyone cloning or reviewing your repo to grasp the intent, structure, and setup immediately.

---

**`README.md`**

```markdown
# 🔍 RAG Search Assistant

An end-to-end **Retrieval-Augmented Generation (RAG)** prototype that demonstrates how to combine **AWS Bedrock**, **Amazon Titan Embeddings**, **Claude 3 Sonnet**, and **Pinecone** into a working search assistant.

This project forms part of the **Gradient Drift** portfolio — designed to showcase real, production-style AI architectures that bridge data pipelines, retrieval systems, and generative reasoning.

---

## 🧭 Project Overview

The RAG Search Assistant allows a user to query a knowledge base (BMW global sales dataset) through a web UI.  
It retrieves semantically relevant text chunks from a Pinecone vector database and uses a Bedrock-hosted model (Claude, Titan, or DeepSeek) to generate a grounded, context-aware answer.

---

## ⚙️ Architecture

```

User → Front-End (HTML/JS)
→ FastAPI Backend (/api/ask)
→ Titan Embeddings (via Bedrock)
→ Pinecone (vector similarity search)
→ Claude / Titan Text / DeepSeek (via Bedrock)
← Response + Retrieved Sources

```

---

## 🧩 Directory Structure

```

rag-search-assistant/
├── backend/
│   ├── main.py
│   ├── services/
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── generate.py
│   │   └── utils.py
│   ├── prompts/
│   │   └── rag_template.txt
│   ├── config/
│   │   └── settings.py
│   └── logs/
│       └── requests.jsonl
│
├── app/
│   ├── index.html
│   ├── app.js
│   └── style.css
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── pinecone/
│
├── scripts/
│   ├── chunk_csv_to_jsonl.py
│   ├── embed_chunks_bedrock.py
│   └── upload_to_pinecone.py
│
├── tests/
│   └── test_api.py
│
├── .env
├── requirements.txt
└── README.md

````

---

## 🚀 Setup & Run

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/rag-search-assistant.git
cd rag-search-assistant
````

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=bmw-rag
BEDROCK_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

### 5. Run the FastAPI Server

```bash
uvicorn backend.main:app --reload
```

Visit [http://localhost:8000](http://localhost:8000) to access the UI.

---

## 🧠 Workflow Summary

1. **User Query → Embedding:** The query is embedded using *Amazon Titan Embeddings*.
2. **Retrieval → Pinecone:** The embedding is matched against stored BMW vectors.
3. **Prompt Assembly:** Top-k chunks are injected into a structured RAG prompt.
4. **Generation → Bedrock:** Claude, Titan Text, or DeepSeek generates an answer.
5. **Response Rendered:** The grounded answer and retrieved sources are displayed.

---

## 🪵 Logging

All requests are appended to:

```
backend/logs/requests.jsonl
```

Each entry records:

```
timestamp, model, query, match_ids, scores, context_length, answer_length, latency_ms
```

---

## 🧰 Dependencies

| Component       | Library / Service                       |
| --------------- | --------------------------------------- |
| Web Framework   | FastAPI, Uvicorn                        |
| Vector Database | Pinecone                                |
| Embeddings      | Amazon Titan (via Bedrock)              |
| Models          | Claude 3 Sonnet / Titan Text / DeepSeek |
| Cloud SDK       | Boto3                                   |
| Env Management  | python-dotenv                           |
| Logging         | Loguru                                  |

---

## 🧩 Next Milestones

* ✅ Phase 1: Data Chunking + Embeddings
* 🔄 Phase 2: Retrieval + Generation (current)
* ⏳ Phase 3: Evaluation + Deployment (serverless)

---

## 📜 License

MIT License © 2025 Laurence Black — Gradient Drift / Reverie Labs

```


