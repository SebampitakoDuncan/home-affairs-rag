# Home Affairs RAG System

A production-ready Retrieval-Augmented Generation (RAG) system that crawls the Australian Department of Home Affairs website and provides an AI-powered question-answering interface with citations.

## 🌟 Features

- **Full Website Crawl**: Crawls entire homeaffairs.gov.au website using Firecrawl API
- **Weekly Auto-Updates**: Automatic re-crawl every Sunday at 2 AM
- **Vector Database**: Qdrant for fast similarity search
- **Free Embeddings**: FastEmbed (BAAI/bge-small-en-v1.5) - completely free, local
- **LLM**: OpenRouter API (gpt-4o-mini)
- **Professional UI**: Linear/AI SDK inspired minimalistic dark theme
- **File Upload**: Support for PDF, TXT, and DOCX documents
- **Citations**: Clickable source links for all answers
- **Source Preview**: View original documents in modal
- **Confidence Scores**: Quality indicators for responses
- **Chat History**: Up to 50 messages stored in memory

## 🏗️ Architecture

```
Firecrawl (Web Crawler)
    ↓
Text Cleaner + Chunker + Metadata Extractor
    ↓
FastEmbed (Local Vector Embeddings)
    ↓
Qdrant (Vector Database)
    ↓
LangChain RAG Pipeline
    ↓
OpenRouter (LLM)
    ↓
Streamlit UI (Linear/AI SDK Inspired)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Firecrawl API key
- OpenRouter API key

### Installation

1. **Clone repository**:
```bash
git clone <your-repo-url>
cd home-affairs-rag
```

2. **Set environment variables**:
```bash
# Copy example .env
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Start Docker Compose**:
```bash
docker-compose up -d
```

5. **Run initial crawl** (one-time setup):
```bash
python scripts/initial_crawl.py
```

6. **Access the application**:
```
Open http://localhost:8501 in your browser
```

## 📁 Project Structure

```
home-affairs-rag/
├── .env                          # API keys (NEVER commit)
├── .gitignore                     # Git ignore patterns
├── docker-compose.yml               # Docker orchestration
├── Dockerfile                       # Main app container
├── .streamlit/
│   ├── config.toml                 # Linear-inspired theme
│   └── custom.css                  # Minimalistic styling
├── src/
│   ├── crawler/                   # Web crawling
│   ├── processors/                 # Document processing
│   ├── embeddings/                 # Vector embeddings
│   ├── vectorstore/                # Qdrant integration
│   ├── rag/                        # RAG pipeline
│   └── ui/                         # Streamlit UI
├── scripts/                       # Utility scripts
├── data/                         # Data directory
└── IMPLEMENTATION_PROGRESS.md     # Progress tracking
```

## ⚙️ Configuration

### Environment Variables

```bash
# Firecrawl API
FIRECRAWL_API_KEY=your_firecrawl_api_key

# OpenRouter API
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=gpt-4o-mini

# Qdrant Configuration
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=home_affairs_docs
QDRANT_UPLOADS_COLLECTION=user_uploads

# FastEmbed Configuration
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DEVICE=cpu

# RAG Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.5

# Crawler Settings
CRAWL_LIMIT=10000
CRAWL_DEPTH=3
CRAWL_SCHEDULE=0 2 * * 0  # Sunday at 2 AM
```

## 🎨 UI Design

### Theme: Linear/AI SDK Inspired

**Color Palette**:
- Primary: `#5E6AD2` (soft purple)
- Background: `#0A0A0A` (near black)
- Secondary: `#1F2937` (dark gray)
- Text: `#F9FAFB` (off-white)
- Success: `#10B981` (green)
- Border: `#374151` (subtle gray)

**Design Principles**:
- Minimalistic interface
- Smooth animations
- Dark mode by default
- Professional typography (Inter font)
- Responsive design
- Intuitive navigation

## 📊 Usage Examples

### Example Queries

1. **Visa Requirements**:
   - "What are the requirements for a 189 visa?"
   - "How do I apply for skilled migration to Australia?"

2. **Citizenship**:
   - "What is the process for Australian citizenship?"
   - "How long does it take to get citizenship?"

3. **Border Security**:
   - "What is the Border Watch program?"
   - "How do I report suspicious activity?"

4. **Student Visa**:
   - "What documents do I need for a student visa?"
   - "What are the English language requirements?"

### Expected Response Format

```
The Skilled Nominated (subclass 189) visa allows you to live and work in Australia permanently.

Requirements:
• Be nominated by an Australian employer [1]
• Have skills on the skilled list [1]
• Pass a skills assessment [2]
• Meet English language requirements [2]
• Be under 45 years old [3]

Sources:
[1] https://www.homeaffairs.gov.au/visas/working-in-australia/skilled-independent/subclass-189.html
[2] https://www.homeaffairs.gov.au/visas/eligibility/points-tested.html
[3] https://www.homeaffairs.gov.au/visas/eligibility/age-limit.html

✨ Confidence: 94%
```

## 🔧 Maintenance

### Manual Re-Crawl

To manually trigger a re-crawl:
```bash
python scripts/update_db.py
```

### Update Crawl Schedule

Edit the `CRAWL_SCHEDULE` in `.env` or modify `src/crawler/scheduler.py`.

### Monitor Qdrant

Check collection status:
```bash
# Access Qdrant dashboard
http://localhost:6333/dashboard
```

## 🚢 Deployment

### Local Development

1. Start Docker Compose:
```bash
docker-compose up -d
```

2. Run initial crawl:
```bash
python scripts/initial_crawl.py
```

3. Access UI:
```
http://localhost:8501
```

### Render (Production)

1. Create Render account at [render.com](https://render.com)
2. Create new web service
3. Connect GitHub repository
4. Configure build type: Docker Compose
5. Set environment variables (from `.env`)
6. Deploy
7. Configure cron job (Sunday 2 AM)

## 📈 Performance

**Expected Performance**:
- Query response time: < 3 seconds
- UI load time: < 2 seconds
- Initial crawl time: 2-4 hours (10,000+ pages)
- Weekly incremental crawl: 15-30 minutes

**Resource Usage**:
- CPU: Medium during crawl
- Memory: 2-4GB
- Disk: 1GB+ for vectors
- Network: Moderate (API calls)

## 💰 Cost

**Monthly Costs**: $0

| Component | Cost | Notes |
|-----------|------|-------|
| Firecrawl API | Free tier included | Check limits |
| FastEmbed | $0 | Local, no API costs |
| Qdrant | $0 | Self-hosted Docker |
| OpenRouter | ~$5-20 | Pay-as-you-go |
| Hosting (Render) | $0 | Free tier |
| **TOTAL** | **~$5-20** | Depending on usage |

## 🔒 Security

- API keys stored in `.env` (never committed)
- Input validation and sanitization
- No personal data crawling
- Rate limiting for API calls
- HTTPS enabled in production

## 📝 Development Status

See `IMPLEMENTATION_PROGRESS.md` for detailed implementation status.

**Completed**:
- ✅ Project structure and configuration
- ✅ Docker Compose setup
- ✅ Vector database integration
- ✅ Embeddings with FastEmbed
- ✅ Document processing pipeline
- ✅ System prompts

**In Progress**:
- 🔄 Web crawler implementation
- 🔄 RAG pipeline completion
- 🔄 UI development
- 🔄 Testing and validation

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is open source and available for educational purposes.

## 🆘 Support

For issues or questions:
- Check `IMPLEMENTATION_PROGRESS.md` for status
- Review logs in `data/logs/`
- Open an issue on GitHub

## 🙏 Acknowledgments

- **Firecrawl**: Web crawling API
- **Qdrant**: Vector database
- **FastEmbed**: Vector embeddings
- **LangChain**: RAG framework
- **Streamlit**: UI framework
- **OpenRouter**: LLM API

---

**Built with ❤️ for the Australian community**
