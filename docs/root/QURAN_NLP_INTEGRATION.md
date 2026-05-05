# QURAN-NLP Data Integration Guide

## Overview

This guide explains how to integrate additional Islamic knowledge from the **[islamAndAi/QURAN-NLP](https://github.com/islamAndAi/QURAN-NLP)** GitHub repository into your Islamic AI Agent.

### Available Data Sources

The QURAN-NLP repository contains:

1. **📖 Quran Translations** (English)
   - Multiple English translations of the Holy Quran
   - Verse-by-verse format
   - Location: `translation/english/`

2. **📚 Tafseer/Commentary** (English)
   - Quranic interpretations and commentary
   - Scholarly explanations of verses
   - Location: `tafaseer/english/`

3. **✨ Names of Allah** (99 Divine Attributes)
   - English translations of names with meanings
   - Arabic names with transliterations
   - Location: `names_of_Allah/`

4. **📋 Additional Resources**
   - Hadith collections
   - Surah information
   - Comprehensive datasets

---

## Quick Start: Ingest & Update

### Option 1: Automatic Ingestion (Recommended)

```bash
cd /Users/fahadiqbal/Downloads/Latest\ Projects/Islamic-AIAgent
source .venv/bin/activate
python scripts/ingest_quran_nlp_data.py
```

**What this does:**
- Downloads Quran translations from GitHub
- Downloads Tafseer/commentary data
- Downloads Names of Allah information
- Indexes all data with BM25 Okapi
- Creates enhanced index: `bm25_index_enhanced.pkl`
- Merges with existing local knowledge base

**Output:**
```
✨ Successfully ingested data from GitHub
✅ Total Documents: [number]
✅ Index Size: [MB]
✅ Documents by source: [breakdown]
✅ Documents by type: [breakdown]
```

### Option 2: Manual Download & Process

If you prefer to download manually:

1. **Download from GitHub:**
   ```bash
   git clone https://github.com/islamAndAi/QURAN-NLP.git
   cd QURAN-NLP/data
   ```

2. **Copy to knowledge base:**
   ```bash
   cp -r translation/english/* ~/Downloads/Latest\ Projects/Islamic-AIAgent/backend/knowledge/data/
   cp -r tafaseer/english/* ~/Downloads/Latest\ Projects/Islamic-AIAgent/backend/knowledge/data/
   cp -r names_of_Allah/* ~/Downloads/Latest\ Projects/Islamic-AIAgent/backend/knowledge/data/
   ```

3. **Rebuild index:**
   ```bash
   python scripts/ingest_quran_nlp_data.py
   ```

---

## Integration Details

### What Gets Created

After ingestion, you'll have:

| File | Purpose | Size |
|------|---------|------|
| `backend/knowledge/bm25_index_enhanced.pkl` | Enhanced BM25 index with GitHub data | ~100+ MB |
| `backend/knowledge/cache_quran_nlp/` | Downloaded files cache | ~500 MB |
| Updated metadata | Source attribution for all new documents | - |

### Automatic Priority System

The system automatically prioritizes indexes:

1. **First choice**: `bm25_index_enhanced.pkl` (GitHub + local data)
2. **Fallback**: `bm25_index.pkl` (original local data only)

### Data Structure

Each ingested document has metadata:

```json
{
  "source": "filename.json",
  "type": "quran_translation|tafseer|names_of_allah|hadith|text",
  "surah": 1,
  "verse": 1,
  "surah_name": "Al-Fatiha",
  "name": "Ar-Rahman",
  "arabic": "الرحمن"
}
```

---

## Usage After Integration

### 1. Restart Backend

```bash
# Kill existing backend
pkill -f web_api.py

# Start new backend with enhanced index
cd /Users/fahadiqbal/Downloads/Latest\ Projects/Islamic-AIAgent
source .venv/bin/activate
python backend/api/web_api.py &
```

### 2. Query Enhanced Knowledge Base

The system now has access to all the integrated data:

```bash
# Query about Quran translations
curl -X POST http://localhost:5010/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What does Surah Al-Fatiha say about Gods mercy?"}'

# Query about Names of Allah
curl -X POST http://localhost:5010/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about Ar-Rahman (The Merciful)"}'

# Query Tafseer
curl -X POST http://localhost:5010/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain the Tafseer of the first verse of Quran"}'
```

### 3. Check Enhanced Status

```bash
# Backend logs will show:
✅ BM25 loaded: [number] documents (✨ ENHANCED)

# This confirms GitHub data is integrated
```

---

## What's New in Your Knowledge Base

### Enhanced Coverage

**Before Integration:**
- Local Quran: 4 translations
- Local Hadith: 8 collections
- Local Tafseer: Limited
- Local Scholarly: 378 documents
- **Total**: ~35,796 documents

**After Integration:**
- Quran: All GitHub translations added
- Tafseer: Comprehensive commentary added
- Names of Allah: 99 divine attributes explained
- Local data: Still fully available
- **Total**: 40,000+ documents (estimated)

### New Query Capabilities

You can now ask about:

✅ Specific Quranic verses with multiple translations
✅ Scholarly interpretations (Tafseer) of verses
✅ Names of Allah with meanings and significance
✅ Cross-referenced Islamic knowledge
✅ Comparative Islamic scholarship

---

## Troubleshooting

### Issue: Ingestion fails with network error

**Solution:**
```bash
# Check internet connection
ping github.com

# If network is slow, increase timeout in script
# Edit scripts/ingest_quran_nlp_data.py
# Change: timeout=30 to timeout=60
```

### Issue: Index file too large

**Solution:**
```bash
# The index might be large (100+ MB)
# This is normal and provides better search accuracy
# You can compress: gzip -9 bm25_index_enhanced.pkl

# To use compressed version, update hybrid_rag_llm.py
# Add: with gzip.open(bm25_path, 'rb') as f:
```

### Issue: Backend shows "standard" instead of "ENHANCED"

**Solution:**
```bash
# Make sure enhanced index was created
ls -lh backend/knowledge/bm25_index*.pkl

# Should see both:
# - bm25_index.pkl (original)
# - bm25_index_enhanced.pkl (new)

# Verify ingestion completed successfully
python scripts/ingest_quran_nlp_data.py
```

---

## Advanced Configuration

### Customize Ingestion

Edit `scripts/ingest_quran_nlp_data.py` to:

**Limit data sources:**
```python
# Line 140: self.ingest_quran_translations()  # Add/remove calls
# Line 141: self.ingest_tafaseer()
# Line 142: self.ingest_names_of_allah()
# Line 143: self.ingest_local_data()
```

**Adjust limits:**
```python
# Line 110: for json_file in json_files[:10]:  # Change 10 to 5 or 20
```

**Change download timeout:**
```python
# Line 63: response = requests.get(url, timeout=30)  # Change to 60
```

### Monitor Ingestion Progress

```bash
# Watch logs in real-time
tail -f /tmp/quran_nlp_ingestion.log

# Or run with verbose output
python scripts/ingest_quran_nlp_data.py 2>&1 | tee ingestion.log
```

---

## Performance Impact

### Index Size Comparison

| Metric | Before | After |
|--------|--------|-------|
| Index Size | 48.4 MB | ~100-120 MB |
| Documents | 35,796 | 40,000+ |
| Search Speed | < 100ms | < 150ms |
| Memory Usage | ~200 MB | ~400 MB |

**Impact**: Minimal. Modern systems handle this easily.

---

## Next Steps

### 1. Ingest the Data

```bash
python scripts/ingest_quran_nlp_data.py
```

### 2. Restart Backend

```bash
pkill -f web_api.py
python backend/api/web_api.py &
```

### 3. Test Enhanced Capabilities

```bash
# Test comprehensive Quranic query
curl -X POST http://localhost:5010/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me everything about Surah Al-Fatiha - translation, Tafseer, and significance"}'
```

### 4. Monitor Quality

Check response quality scores:
- Quality should be **60-90%** with enhanced data
- Sources should show **GitHub + Local** attribution
- Responses should be **more comprehensive**

---

## Updating Data Periodically

To update with latest GitHub data:

```bash
# Re-run ingestion (safe - will replace old enhanced index)
python scripts/ingest_quran_nlp_data.py

# Restart backend
pkill -f web_api.py
python backend/api/web_api.py &
```

The system will:
- ✅ Download latest data from GitHub
- ✅ Merge with local knowledge base
- ✅ Create new enhanced index
- ✅ Preserve existing data (no data loss)

---

## Support & Troubleshooting

**Questions?** Check:
1. `backend/utils/hybrid_rag_llm.py` - How indexes are loaded
2. `scripts/ingest_quran_nlp_data.py` - Ingestion logic
3. Backend logs: `tail -f /tmp/backend.log`

**Issues?** Run diagnostic:

```bash
python -c "
from pathlib import Path
knowledge_dir = Path('backend/knowledge')
print('📂 Knowledge Base Contents:')
print(list(knowledge_dir.glob('*.pkl')))
print(list(knowledge_dir.glob('cache*')))
"
```

---

**Status**: ✨ Ready to integrate additional authentic Islamic knowledge! ✨

Your Islamic AI Agent will now have access to comprehensive Quranic translations, scholarly Tafseer, and divine Names from the QURAN-NLP repository.
