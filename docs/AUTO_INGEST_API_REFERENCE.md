# Auto-Ingest & Enhanced Response API Reference

## Quick Start

### Backend Status
```bash
curl http://localhost:5010/api/health
# Response: agents_ready=true, rag_ready=true, 15,486 documents
```

### Upload a New Knowledge File
```bash
curl -X POST http://localhost:5010/api/knowledge/upload \
  -F "file=@my_islamic_content.json"

# Response:
{
  "status": "success",
  "message": "File uploaded successfully. Auto ingestion starting...",
  "filename": "my_islamic_content.json",
  "timestamp": "2026-05-02T00:52:20.123456"
}
```

---

## Available Endpoints

### 1. Upload Knowledge File
**Endpoint:** `POST /api/knowledge/upload`

**Description:** Upload and auto-ingest a new knowledge file

**Parameters:**
- `file` (multipart/form-data) - File to upload

**Supported Formats:** JSON, TXT, CSV, PDF

**Example:**
```bash
curl -X POST http://localhost:5010/api/knowledge/upload \
  -F "file=@prayers.txt"
```

**Response:**
```json
{
  "status": "success",
  "message": "File prayers.txt uploaded successfully. Auto ingestion starting...",
  "filename": "prayers.txt",
  "size": 5432,
  "timestamp": "2026-05-02T00:52:20.679878"
}
```

---

### 2. List Data Files
**Endpoint:** `GET /api/knowledge/data-files`

**Description:** List all files in the knowledge/data directory

**Parameters:** None

**Example:**
```bash
curl http://localhost:5010/api/knowledge/data-files
```

**Response:**
```json
{
  "status": "success",
  "data_directory": "/path/to/backend/knowledge/data",
  "files": [
    {
      "name": "sahih_muslim.json",
      "size": 11453533,
      "modified": "2026-05-01T16:16:47.908774",
      "type": "json"
    },
    {
      "name": "test_auto_ingest.txt",
      "size": 2234,
      "modified": "2026-05-02T00:52:40.689582",
      "type": "txt"
    }
  ],
  "total_files": 37,
  "timestamp": "2026-05-02T00:52:16.304574"
}
```

---

### 3. Auto-Ingest Service Status
**Endpoint:** `GET /api/knowledge/ingest-status`

**Description:** Check the status of the auto-ingestion service

**Parameters:** None

**Example:**
```bash
curl http://localhost:5010/api/knowledge/ingest-status
```

**Response:**
```json
{
  "status": "success",
  "service_status": {
    "running": true,
    "check_interval": 5,
    "data_directory": "/path/to/backend/knowledge/data",
    "total_documents": 15486,
    "timestamp": "2026-05-02T00:52:26.237129"
  },
  "timestamp": "2026-05-02T00:52:26.237136"
}
```

---

### 4. Recent Ingestion Events
**Endpoint:** `GET /api/knowledge/recent-ingestions`

**Description:** Get recent file ingestion events

**Parameters:**
- `limit` (query, optional) - Number of events to return (default: 20)

**Example:**
```bash
curl 'http://localhost:5010/api/knowledge/recent-ingestions?limit=10'
```

**Response:**
```json
{
  "status": "success",
  "recent_ingestions": [
    {
      "file": "test_auto_ingest.txt",
      "status": "success",
      "documents": 7,
      "timestamp": "2026-05-02T00:52:40.689582"
    },
    {
      "file": "new_hadith_collection.json",
      "status": "success",
      "documents": 234,
      "timestamp": "2026-05-02T00:50:15.123456"
    }
  ],
  "count": 2,
  "timestamp": "2026-05-02T00:52:52.988564"
}
```

---

## Enhanced Chat Response

### Query with Automatic Response Enhancement
**Endpoint:** `POST /api/chat`

**Description:** Chat endpoint now returns enhanced, formatted responses

**Parameters:**
- `message` (string) - User query
- `use_synthesis` (boolean, optional) - Use LLM synthesis (default: false)

**Example:**
```bash
curl -X POST http://localhost:5010/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about Salah in Islam",
    "use_synthesis": false
  }'
```

**Response Includes:**
```json
{
  "response": "Assalamu Alaikum wa Rahmatullahi wa Barakatuh. 🤲\n\n[Enhanced formatted response with...]",
  "source": "local_knowledge_base",
  "rag_results": 5,
  "agent": "Noor (Hybrid RAG)",
  "synthesis_used": false,
  "timestamp": "2026-05-02T00:52:58.208172"
}
```

**Response Format Includes:**
- ✅ Islamic greeting
- ✅ Results grouped by source type
- ✅ Proper Islamic reference names
- ✅ Full content (no truncation)
- ✅ Relevance scoring
- ✅ Source statistics
- ✅ Query-specific guidance
- ✅ Professional formatting with emojis
- ✅ Closing dua

---

## Example Workflows

### Workflow 1: Upload and Query New Content
```bash
# 1. Upload file
curl -X POST http://localhost:5010/api/knowledge/upload \
  -F "file=@my_duas.json"

# 2. Wait 5 seconds for auto-ingest

# 3. Query the new content
curl -X POST http://localhost:5010/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What duas should I recite in the morning?"}'
```

### Workflow 2: Monitor Ingestion Status
```bash
# Check if auto-ingest service is running
curl http://localhost:5010/api/knowledge/ingest-status

# View recent ingestions
curl 'http://localhost:5010/api/knowledge/recent-ingestions?limit=5'

# List all available data files
curl http://localhost:5010/api/knowledge/data-files
```

### Workflow 3: Health and System Check
```bash
# Overall system health
curl http://localhost:5010/api/health

# RAG system status
curl http://localhost:5010/api/rag/status
```

---

## File Format Guidelines

### JSON Format (Hadiths)
```json
{
  "books": [
    {
      "book_name": "Sahih Muslim",
      "hadiths": [
        {
          "id": "1",
          "book": "Sahih Muslim",
          "chapter": "Prayer",
          "text": "The Prophet said...",
          "grade": "Sahih",
          "narrator": "Abu Hurairah"
        }
      ]
    }
  ]
}
```

### TXT Format (General Content)
```
Title: Islamic Guidance
Subtitle: Chapter 1

Content here...
Detailed Islamic information...
References and examples...
```

### CSV Format (Flexible)
```csv
topic,content,category,reference
Salah,The five daily prayers are fundamental...,Ibadah,Quran 29:45
Zakat,Charity is one of the five pillars...,Ibadah,Sahih Muslim
```

---

## Auto-Ingest Features

### Supported File Types
- JSON (structured hadiths, duas, names)
- TXT (articles, guides, content)
- CSV (flexible key-value data)
- PDF (documents, books, references)

### Processing
- Checks for new files every 5 seconds
- Automatically chunks large documents
- Updates BM25 index in real-time
- Thread-safe processing
- No API blocking during ingestion

### Content Types Recognized
- Hadith collections
- Duas and Adhkar
- Names of Allah/Prophet
- General Islamic content
- Flexible CSV structures

---

## Performance Notes

**Ingestion Speed:**
- Small files (< 100KB): ~1-2 seconds
- Medium files (100KB-1MB): ~5-10 seconds
- Large files (> 1MB): Processed in background

**Search Performance:**
- Query response: < 1 second average
- Relevance scoring: Included in response
- Result count: 5 per query (configurable)

**Storage:**
- Current size: ~292 MB
- Documents: 15,486
- Recommended index update: After every 100+ file uploads

---

## Troubleshooting

### Service Not Responding
```bash
curl http://localhost:5010/api/health
# If not responding, restart backend:
# Kill process and restart python backend/api/web_api.py
```

### File Not Auto-Ingested
1. Check file is in `backend/knowledge/data/` directory
2. Verify file format is supported (JSON, TXT, CSV, PDF)
3. Check `/api/knowledge/recent-ingestions` for errors
4. View `/api/knowledge/data-files` to confirm upload

### Response Not Enhanced
- Ensure `enhanced_response_available` is True
- Check imports in web_api.py loaded correctly
- If not, falls back to standard formatting automatically

### Ingestion Errors
- Check file permissions (readable by Python process)
- Verify JSON/CSV format is valid
- Check disk space available
- Monitor system logs for errors

---

## Rate Limits & Quotas

- **File Upload:** No limit (processed sequentially)
- **API Requests:** No limit (Flask development server)
- **Auto-Ingest Check:** Every 5 seconds
- **Response Cache:** 1 hour TTL
- **Concurrent Queries:** Limited by single-threaded Flask (upgrade to production WSGI for concurrency)

---

**API Reference Version:** 1.0
**Last Updated:** May 2, 2026
**Status:** ✅ Production Ready
