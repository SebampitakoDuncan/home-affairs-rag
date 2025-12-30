# Home Affairs RAG System

A RAG (Retrieval-Augmented Generation) system for querying Australian Department of Home Affairs information.

## 🚀 Quick Start

### Option 1: Docker Version (Local Development with Qdrant)

```bash
# Start all services (Qdrant + Streamlit)
docker-compose up -d

# Access the app at: http://localhost:8503
```

### Option 2: Local Version (Python Only)

```bash
# Install dependencies
pip install -r requirements.txt

# Start Streamlit
streamlit run src/ui/simple_chat.py --server.port 8503

# Access at: http://localhost:8503
```

### Option 3: Streamlit Cloud Version

**Deploy to Streamlit Cloud:**

1. Fork/copy this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add these Secrets:
   - `QDRANT_URL` - Your Qdrant URL (use Qdrant Cloud free tier: https://[your-instance].qdrant.tech:6333)
   - `OPENROUTER_API_KEY` - Your OpenRouter API key
   - `OPENROUTER_MODEL` - Model to use (default: gpt-4o-mini)

5. Deploy!

## 📁 Project Structure

```
home-affairs-rag/
├── src/
│   ├── vectorstore/qdrant_store.py    # Qdrant client wrapper
│   ├── embeddings/fastembed.py            # FastEmbed local embeddings
│   ├── processors/                      # Document processing
│   │   ├── text_cleaner.py
│   │   ├── chunker.py
│   │   └── metadata.py
│   ├── rag/                            # RAG pipeline
│   │   ├── prompts.py
│   │   ├── retriever.py
│   │   └── chain.py
│   ├── crawler/                         # Web crawler
│   │   ├── firecrawl_client.py
│   │   ├── crawler.py
│   │   └── scheduler.py
│   └── ui/
│       ├── simple_chat.py              # Simple chat UI (local/cloud)
│       ├── app.py                    # Complex UI (Docker only)
│       ├── components.py               # UI components
│       ├── constants.py                # UI configuration
│       ├── config.toml               # Streamlit config
│       └── custom.css                # Custom styling
├── scripts/                           # Utility scripts
│   ├── test_system.py                 # System tests
│   ├── test_api_keys.py             # API key tests
│   ├── test_rag_pipeline.py         # Full RAG test
│   ├── populate_db.py               # Populate with test data
│   ├── initial_crawl.py             # Trigger initial crawl
│   └── update_db.py                # Update database
├── .env                              # Environment variables
├── requirements.txt                    # Python dependencies
├── docker-compose.yml                  # Docker services
├── Dockerfile                         # Docker build
├── streamlit_app.py                  # **Streamlit Cloud version** (root level)
└── .streamlit/
    ├── config.toml                   # Streamlit theme config
    └── custom.css                    # Custom CSS
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Qdrant Configuration
QDRANT_HOST=localhost                    # Docker version uses localhost
QDRANT_URL=http://localhost:6333        # Streamlit Cloud version
QDRANT_COLLECTION_NAME=home_affairs_docs

# OpenRouter API
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=gpt-4o-mini

# Embeddings
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DEVICE=cpu

# Document Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Streamlit Secrets (Cloud Version)

Add these in Streamlit Cloud > Settings > Secrets:

- `QDRANT_URL` - Your Qdrant instance URL
- `OPENROUTER_API_KEY` - Your OpenRouter API key
- `OPENROUTER_MODEL` - (optional) Model to use

## 🧪 Test Queries

**What are requirements for a 189 visa?**

Expected answer includes:
- Age: Under 45 years
- English: IELTS 6.0 or equivalent
- Skills: Skills assessment for nominated occupation
- Points: Minimum 65 points on points test
- Cost: AUD 4,770
- Processing time: 8-11 months

**How much does a visitor visa cost?**

Expected answer:
- Tourist/Sponsored Family/Business Visitor: AUD 195
- Stay duration varies by stream

**How do I apply for Australian citizenship?**

Expected answer includes:
- Age: 18+ years
- Residence: 4 years as permanent resident
- English: Basic knowledge
- Cost: AUD 540
- Processing: Up to 12 months

## 🔧 Development

### Running Tests

```bash
# Test system components
python scripts/test_system.py

# Test API keys
python scripts/test_api_keys.py

# Test full RAG pipeline
python scripts/test_rag_pipeline.py

# Populate Qdrant with test data
python scripts/populate_db.py
```

### Starting Services

```bash
# Start Qdrant only
docker-compose up -d qdrant

# Start Streamlit only (with Qdrant running)
streamlit run src/ui/simple_chat.py --server.port 8503

# Start all Docker services
docker-compose up -d

# Start Streamlit Cloud version locally
streamlit run streamlit_app.py --server.port 8504
```

## 🐛 Troubleshooting

### App loads but no response
1. Check Qdrant is running: `docker ps | grep qdrant`
2. Check .env file has correct API keys
3. Check Qdrant has documents:
   ```bash
   python scripts/populate_db.py
   ```
4. Check Streamlit logs for errors

### Font doesn't look like DM Sans
1. Clear browser cache
2. Hard refresh (Cmd+Shift+R on Mac, Ctrl+F5 on Windows)
3. Check Google Fonts is loading (Network tab in browser DevTools)

### Import errors in Docker
1. Rebuild container: `docker-compose up -d --build streamlit-app`
2. Check Docker logs: `docker logs streamlit-rag`

## 📝 Notes

### Differences Between Versions

| Feature | Docker Version | Streamlit Cloud Version |
|---------|---------------|------------------------|
| Qdrant | Included in Docker | Use external Qdrant Cloud |
| Environment | Auto-loaded from .env | Use Streamlit Secrets |
| Font | Configured in config.toml | Inline CSS with @import |
| Chat UI | Complex (Linear-inspired) | Simple (standard Streamlit) |
| Location | src/ui/app.py | streamlit_app.py (root) |

## 📄 License

This project is provided as-is for educational purposes.

## 🔗 Links

- [Streamlit Docs](https://docs.streamlit.io)
- [Qdrant Docs](https://qdrant.tech/documentation)
- [OpenRouter Docs](https://openrouter.ai/docs)
- [Firecrawl Docs](https://www.firecrawl.dev/docs)
- [FastEmbed Docs](https://qdrant.github.io/fastembed/)
