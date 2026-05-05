# API Reference - Noor (Flask Backend)

The Noor backend is a local-first Flask API used by the React frontend. The core flow is:
chat request → routing → retrieval (KB + Quran MCP) → evidence pack → local LLM synthesis → response.

## Base URL and Headers
- Base URL: `http://localhost:5010`
- JSON requests: `Content-Type: application/json`

## Health and Readiness

### `GET /api/health`
Returns backend status plus RAG and local LLM reachability.

### `POST /api/initialize`
Forces agent initialization (useful after startup).

## Core Chat

### `POST /api/chat`
Primary chat endpoint.

Request body:
```json
{
  "message": "What is the virtue of Tahajjud?",
  "user_gender": "not_specified",
  "use_synthesis": true,
  "quran_translation_lang": "en",
  "latitude": 24.4686,
  "longitude": 39.6142
}
```

Notes:
- `quran_translation_lang` influences Quran translation selection when Quran MCP is used.
- If systems are still initializing, you may receive HTTP `503` with `code: "AGENT_INITIALIZING"`.

Response:
```json
{
  "response": "Assalamu Alaikum ...",
  "timestamp": "2026-05-05T12:34:56.000000",
  "agent": "Noor",
  "thoughts": null
}
```

### `POST /api/multi-chat`
Same core routing pipeline, but returns a `specialist` label.

### `POST /api/collaborative`
Same core routing pipeline, but returns a coordinator label.

### `POST /api/chat/multimodal`
Attachment field exists, but in local-only mode attachments are rejected.
Send text-only messages.

## Quran Support

### `GET /api/quran/translation-languages`
Returns available translation language codes discovered via Quran Foundation MCP.

Response:
```json
{
  "languages": [{"code": "en", "edition_count": 20}],
  "default": "en"
}
```

## RAG / Knowledge Base

### `POST /api/rag/search`
Direct KB search (returns raw KB formatted text).

Request body:
```json
{ "query": "patience in Islam", "k": 10 }
```

### `GET /api/knowledge-base/status`
Returns KB initialization stats.

## Knowledge File Upload and Listing

### `POST /api/knowledge/upload`
Upload a knowledge file to `backend/knowledge/data/`.
- Form field: `file`
- Allowed: `json`, `txt`, `csv`, `pdf`

### `POST /api/knowledge/upload-secure`
Secure uploader with size guard.
- Form field: `file`
- 5MB limit
- Allowed: `pdf`, `txt`, `docx`, `json`, `csv`

### `GET /api/knowledge/list`
Lists `.pdf`, `.txt`, `.json` from the knowledge data folder.

### `GET /api/knowledge/data-files`
Lists all files in the knowledge data folder (includes detected `type`).

### `DELETE /api/knowledge/delete?filename=<name>`
Deletes a file from the knowledge data folder.

### `GET /api/knowledge/ingest-status`
Auto-ingest service status (BM25 watcher).

### `GET /api/knowledge/recent-ingestions?limit=20`
Recent auto-ingestion events.

## Utility Endpoints

### `POST /api/prayer-times`
Body:
```json
{ "latitude": 24.4686, "longitude": 39.6142 }
```

### `POST /api/qibla`
Body:
```json
{ "latitude": 24.4686, "longitude": 39.6142 }
```

### `POST /api/zakat/calculate`
Body:
```json
{ "cash": 5000, "gold_grams": 100, "investments": 2000, "debts": 500 }
```
