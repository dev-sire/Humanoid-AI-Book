# Quick Start Guide: RAG Chatbot Integration

**Feature**: 011-rag-chatbot-integration
**Date**: 2025-12-01
**Estimated Setup Time**: 2-3 hours (including external service signups)

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [External Service Setup](#external-service-setup)
3. [Backend Setup](#backend-setup)
4. [Frontend Integration](#frontend-integration)
5. [Running Locally](#running-locally)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Python 3.9+**: Check with `python --version` or `python3 --version`
- **Node.js 18+**: Check with `node --version`
- **npm or yarn**: Check with `npm --version` or `yarn --version`
- **Git**: Check with `git --version`
- **UV Package Manager**: Install with `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Required Accounts (Free Tiers)

- **OpenAI**: API access for embeddings and chat completions
- **Qdrant Cloud**: Free tier vector database (1GB storage)
- **Neon**: Free tier serverless Postgres (0.5GB storage)
- **Railway or Render**: Free tier cloud hosting for FastAPI backend

### Estimated Costs

- **OpenAI API**: ~$5-10/month for 1000 queries (moderate usage)
- **Qdrant Cloud**: $0 (free tier sufficient)
- **Neon**: $0 (free tier sufficient)
- **Hosting**: $0 (free tier on Railway/Render)

**Total**: $5-10/month (within $15 budget)

---

## External Service Setup

### 1. OpenAI API Setup

1. Go to https://platform.openai.com/signup
2. Create account and verify email
3. Navigate to API Keys: https://platform.openai.com/api-keys
4. Click "Create new secret key"
5. Copy the key (starts with `sk-...`)
6. **Save to `.env` file** (see Backend Setup section)

**Note**: New accounts get $5 free credit. After that, add payment method.

### 2. Qdrant Cloud Setup

1. Go to https://cloud.qdrant.io/
2. Sign up with email or GitHub
3. Create a new cluster:
   - Name: `documentation-chatbot`
   - Region: Choose closest to your users
   - Plan: **Free tier** (1GB storage)
4. Wait for cluster to provision (~2-3 minutes)
5. Get credentials:
   - **URL**: Click cluster → Copy "Cluster URL" (e.g., `https://xyz-abc.qdrant.io`)
   - **API Key**: Click "API Keys" → Generate new key → Copy
6. **Save to `.env` file** (see Backend Setup section)

### 3. Neon Postgres Setup

1. Go to https://neon.tech/
2. Sign up with email or GitHub
3. Create a new project:
   - Name: `rag-chatbot`
   - Region: Choose closest to your users
   - Postgres version: Latest (16+)
4. Wait for project to provision (~30 seconds)
5. Get connection string:
   - Navigate to Dashboard → Connection Details
   - Copy **Connection string** (format: `postgresql://user:password@host/dbname`)
6. **Save to `.env` file** (see Backend Setup section)

---

## Backend Setup

### 1. Clone Repository

```bash
# Navigate to project root
cd /path/to/ai-native-book

# Ensure you're on the correct branch
git checkout 011-rag-chatbot-integration
```

### 2. Create Backend Directory Structure

```bash
# Create backend directory (if not exists)
mkdir -p backend/src/{models,services,api,utils}
mkdir -p backend/tests/{unit,integration}
mkdir -p backend/scripts
```

### 3. Install Dependencies with UV

```bash
cd backend

# Create pyproject.toml (if not exists)
cat > pyproject.toml << EOF
[project]
name = "rag-chatbot"
version = "1.0.0"
description = "RAG chatbot backend for Physical AI textbook"
requires-python = ">=3.9"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "python-dotenv>=1.0.0",
    "openai>=1.3.0",
    "qdrant-client>=1.7.0",
    "sqlalchemy>=2.0.0",
    "asyncpg>=0.29.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "markdown>=3.5.0",
    "beautifulsoup4>=4.12.0",
    "tiktoken>=0.5.0",
    "httpx>=0.25.0",
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0"
]
EOF

# Install dependencies using UV
uv pip install -e .
```

**Alternative (requirements.txt)**:
```bash
cat > requirements.txt << EOF
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-dotenv>=1.0.0
openai>=1.3.0
qdrant-client>=1.7.0
sqlalchemy>=2.0.0
asyncpg>=0.29.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
markdown>=3.5.0
beautifulsoup4>=4.12.0
tiktoken>=0.5.0
httpx>=0.25.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
EOF

uv pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Create .env file in backend directory
cat > .env << EOF
# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here

# Qdrant Configuration
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key-here
QDRANT_COLLECTION_NAME=documentation_chunks

# Neon Postgres Configuration
DATABASE_URL=postgresql://user:password@host/dbname

# Application Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,https://yourusername.github.io

# Rate Limiting (optional)
MAX_REQUESTS_PER_HOUR=60
EOF

# Replace placeholder values with actual credentials from External Service Setup
```

**Security Note**: Never commit `.env` file to Git. Add to `.gitignore`:
```bash
echo ".env" >> backend/.gitignore
```

### 5. Initialize Database Schema

```bash
# Install psql (if not already installed)
# Ubuntu/Debian: sudo apt-get install postgresql-client
# macOS: brew install postgresql

# Apply schema
psql "$DATABASE_URL" -f ../specs/011-rag-chatbot-integration/contracts/database-schema.sql

# Verify tables created
psql "$DATABASE_URL" -c "\dt"
# Expected output: chat_sessions, chat_messages
```

### 6. Create Qdrant Collection

```bash
# Run Python script to create collection
python3 << EOF
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType
import os
from dotenv import load_dotenv

load_dotenv()

client = QdrantClient(
    url=os.getenv('QDRANT_URL'),
    api_key=os.getenv('QDRANT_API_KEY')
)

# Create collection
client.create_collection(
    collection_name='documentation_chunks',
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
)

# Create indexes
client.create_payload_index(
    collection_name='documentation_chunks',
    field_name='file_path',
    field_schema=PayloadSchemaType.KEYWORD
)

client.create_payload_index(
    collection_name='documentation_chunks',
    field_name='title',
    field_schema=PayloadSchemaType.KEYWORD
)

print("✅ Qdrant collection created successfully")
EOF
```

### 7. Index Documentation

```bash
# Run indexing script (to be implemented)
python scripts/index_docs.py --docs-dir ../docs

# Expected output:
# Indexing 150 documentation files...
# Generated 450 chunks...
# Uploaded to Qdrant: 450/450
# ✅ Indexing complete
```

---

## Frontend Integration

### 1. Navigate to Frontend Directory

```bash
cd /path/to/ai-native-book
```

### 2. Install Docusaurus Dependencies

```bash
# If not already installed
npm install
# or
yarn install
```

### 3. Swizzle Root Component

```bash
# Swizzle the Root component (safe, wrapper-only)
npm run swizzle @docusaurus/theme-classic Root -- --eject

# This creates: src/theme/Root.tsx
```

### 4. Install Frontend Dependencies

```bash
# Install additional dependencies
npm install --save-dev @types/react @types/react-dom

# or with yarn
yarn add --dev @types/react @types/react-dom
```

### 5. Configure API URL

```bash
# Create frontend .env file
cat > .env << EOF
REACT_APP_API_URL=http://localhost:8000
EOF
```

**Production**: Update `REACT_APP_API_URL` to your deployed backend URL (e.g., `https://your-app.railway.app`)

---

## Running Locally

### 1. Start Backend Server

```bash
# Terminal 1: Start FastAPI backend
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
```

### 2. Verify Backend Health

```bash
# Terminal 2: Test health endpoint
curl http://localhost:8000/api/health

# Expected response:
# {
#   "status": "healthy",
#   "services": {
#     "qdrant": "up",
#     "postgres": "up",
#     "openai": "up"
#   },
#   "timestamp": "2025-12-01T12:00:00.000Z"
# }
```

### 3. Start Docusaurus Dev Server

```bash
# Terminal 3: Start Docusaurus
npm run start

# Expected output:
# [INFO] Starting the development server...
# [SUCCESS] Docusaurus website is running at: http://localhost:3000/
```

### 4. Test Chat Widget

1. Open browser: http://localhost:3000
2. Click floating chat button (bottom-right corner)
3. Type: "What is ROS2?"
4. Verify:
   - Response appears within 3 seconds
   - Source citations are displayed
   - Citations link to actual documentation pages

---

## Testing

### Backend Unit Tests

```bash
cd backend

# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Backend Integration Tests

```bash
# Run integration tests (requires running services)
pytest tests/integration/ -v

# Specific test
pytest tests/integration/test_rag_pipeline.py -v
```

### Manual Frontend Testing

**Checklist**:
- [ ] Chat button visible on all pages
- [ ] Chat window opens/closes smoothly (60fps animation)
- [ ] Messages send with Enter key
- [ ] Loading indicator shows during processing
- [ ] Source citations display correctly with links
- [ ] Conversation persists across page reloads
- [ ] Dark mode works correctly
- [ ] Mobile responsive (viewport ≤767px)
- [ ] Keyboard navigation works (Tab, Enter, Escape)
- [ ] Screen reader announces messages (test with NVDA/VoiceOver)

### Performance Testing

```bash
# Backend load test (using Apache Bench)
ab -n 100 -c 10 -p query.json -T application/json http://localhost:8000/api/chat

# query.json content:
echo '{"message": "What is Physical AI?"}' > query.json

# Expected results:
# - 95% of requests < 2000ms
# - 0% failed requests
```

---

## Deployment

### Backend Deployment (Railway)

1. **Sign up**: https://railway.app/
2. **Create new project**: Click "New Project" → "Deploy from GitHub repo"
3. **Connect repository**: Select `ai-native-book` repo
4. **Configure**:
   - Root directory: `/backend`
   - Build command: `uv pip install -r requirements.txt`
   - Start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
5. **Add environment variables**:
   - Go to Variables tab
   - Add all variables from `.env` file
6. **Deploy**: Click "Deploy" → Wait for build (~3-5 minutes)
7. **Get URL**: Copy generated URL (e.g., `https://your-app.railway.app`)

### Frontend Deployment (GitHub Pages)

```bash
# Update docusaurus.config.js with backend URL
# Edit: docusaurus.config.js

# Add custom field:
customFields: {
  apiUrl: 'https://your-app.railway.app'
}

# Build and deploy
npm run build
npm run deploy

# Verify deployment
open https://yourusername.github.io/ai-native-book
```

### CORS Configuration

Update backend CORS settings to allow GitHub Pages domain:

```python
# backend/src/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://yourusername.github.io"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

---

## Troubleshooting

### Backend Issues

#### 1. "Connection refused" to Postgres
**Symptom**: `asyncpg.exceptions.ConnectionDoesNotExistError`
**Solution**:
```bash
# Verify DATABASE_URL format
echo $DATABASE_URL
# Should be: postgresql://user:password@host/dbname

# Test connection manually
psql "$DATABASE_URL" -c "SELECT 1;"
```

#### 2. "Unauthorized" from Qdrant
**Symptom**: `qdrant_client.exceptions.UnauthorizedException`
**Solution**:
```bash
# Verify API key
echo $QDRANT_API_KEY

# Test connection
python3 << EOF
from qdrant_client import QdrantClient
import os
client = QdrantClient(url=os.getenv('QDRANT_URL'), api_key=os.getenv('QDRANT_API_KEY'))
print(client.get_collections())
EOF
```

#### 3. "Rate limit exceeded" from OpenAI
**Symptom**: `openai.error.RateLimitError`
**Solution**:
- Wait 60 seconds and retry
- Check API usage: https://platform.openai.com/usage
- Add payment method if free credit exhausted

#### 4. "Collection not found" in Qdrant
**Symptom**: `qdrant_client.exceptions.UnexpectedResponse: Collection not found`
**Solution**:
```bash
# Recreate collection
python backend/scripts/create_qdrant_collection.py
python backend/scripts/index_docs.py
```

### Frontend Issues

#### 1. Chat button not visible
**Symptom**: No floating button on page
**Solution**:
```bash
# Verify Root.tsx was swizzled
ls src/theme/Root.tsx

# Check browser console for errors
# Open DevTools → Console tab
```

#### 2. "CORS error" in browser console
**Symptom**: `Access-Control-Allow-Origin` error
**Solution**:
- Verify backend CORS configuration includes frontend URL
- Check `CORS_ORIGINS` in backend `.env` file
- Restart backend server after changes

#### 3. "Network error" when sending messages
**Symptom**: Message fails to send, generic error shown
**Solution**:
```bash
# Verify backend is running
curl http://localhost:8000/api/health

# Check API URL in frontend .env
echo $REACT_APP_API_URL

# Inspect network tab in DevTools for failed requests
```

#### 4. Chat widget laggy/slow animations
**Symptom**: <30fps animations, choppy transitions
**Solution**:
- Use Chrome DevTools Performance panel to profile
- Ensure CSS uses `transform` and `opacity` (GPU-accelerated)
- Check for unnecessary re-renders with React DevTools Profiler

### Performance Issues

#### 1. Slow response times (>3s)
**Symptom**: Chatbot responses take >3 seconds
**Diagnosis**:
```bash
# Check each pipeline stage
# Backend logs should show timing:
# [INFO] Embedding: 180ms
# [INFO] Vector search: 45ms
# [INFO] LLM generation: 1200ms
# [INFO] Total: 1425ms
```
**Solution**:
- If embedding slow: Check OpenAI API latency, consider caching frequent queries
- If search slow: Verify Qdrant cluster region, consider upgrading to paid tier
- If LLM slow: Use streaming responses, optimize context length

#### 2. High OpenAI costs
**Symptom**: API costs exceed $15/month
**Solution**:
- Reduce context length (use top 3 chunks instead of 5)
- Implement query caching (cache frequent questions for 1 hour)
- Use cheaper model for embeddings (already using text-embedding-3-small)
- Monitor usage: https://platform.openai.com/usage

---

## Next Steps

After successful setup:

1. **Run `/sp.tasks`** to generate implementation tasks
2. **Implement backend services** (embedding, vector store, LLM, conversation)
3. **Implement frontend components** (ChatWidget, MessageList, InputArea, etc.)
4. **Write unit tests** (target >80% coverage)
5. **Document architecture** (create `docs/rag-architecture.md`)
6. **Consider ADRs** for significant decisions:
   - RAG Pipeline Architecture
   - Docusaurus Integration Strategy
   - Session Management Design

---

## Resources

- **OpenAI API Docs**: https://platform.openai.com/docs
- **Qdrant Documentation**: https://qdrant.tech/documentation/
- **Neon Documentation**: https://neon.tech/docs
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Docusaurus Documentation**: https://docusaurus.io/docs

---

**Questions or Issues?** Create a GitHub issue or consult the troubleshooting section above.
