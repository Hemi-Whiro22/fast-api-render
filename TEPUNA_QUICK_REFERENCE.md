# Te Puna Public Schema for IwiPortalPanel
**Status**: ✅ Live in frontend/src/data/public_schema_te_puna.json

## Quick Reference: Archive Tables

### 🪶 taonga_metadata
**Purpose**: Māori cultural artifacts and treasures  
**Fields**: 9  
```
id (uuid)                      → Unique identifier
name (text)                    → Taonga name
description (text)            → Cultural description
cultural_significance (text)   → Significance to iwi
source (text)                  → Origin/source
iwi (text)                     → Associated iwi
category (text)                → Classification
created_at (timestamp)         → Record creation
updated_at (timestamp)         → Last update
```

### 📚 summaries
**Purpose**: Document abstracts and summaries  
**Fields**: 6  
```
id (uuid)                      → Unique identifier
document_id (uuid)             → Linked document
summary_text (text)            → Summary content
keywords (text)                → Searchable keywords
language (text)                → Language (mi, en, etc)
created_at (timestamp)         → Creation date
```

### 📋 ocr_logs  
**Purpose**: OCR extraction history (archive)  
**Fields**: 8  
```
id (uuid)                      → Log entry ID
file_name (text)               → Original filename
file_url (text)                → Archived document URL
text_content (text)            → Extracted text
language_detected (text)       → Language (mri, eng, etc)
confidence_score (numeric)     → OCR confidence %
meta (jsonb)                   → Additional metadata
created_at (timestamp)         → Extraction date
```

### 🌐 translations
**Purpose**: Māori ↔ English translation archive  
**Fields**: 10  
```
id (uuid)                      → Translation ID
ocr_id (uuid)                  → Source OCR record
source_lang (text)             → Source language
target_lang (text)             → Target language
source_text (text)             → Original text
translated_text (text)         → Translated text
model_used (text)              → Translation model
confidence (numeric)           → Translation confidence
meta (jsonb)                   → Model metadata
created_at (timestamp)         → Translation date
```

### 🧠 memory_logs
**Purpose**: Knowledge processing and learning history  
**Fields**: 7  
```
id (uuid)                      → Log entry ID
memory_type (text)             → Type of memory (reflection, etc)
content (text)                 → Memory content
embedding (vector/1536)        → Vector embedding
related_task (uuid)            → Associated task
meta (jsonb)                   → Processing metadata
created_at (timestamp)         → Creation date
```

## IwiPortalPanel Archive View

The archive tab displays:
1. **Available Tables**: Shows all 5 tables with field counts
2. **Table Descriptions**: Context about what each table contains
3. **Records**: Filtered results from selected table
4. **Schema Awareness**: UI knows structure and can format appropriately

### Example Archive Record Display
```
📚 Te Puna Archive (Read-Only)

🪶 Archive Tables Available:
  • taonga_metadata (9 fields)
  • summaries (6 fields)
  • ocr_logs (8 fields)
  • translations (10 fields)
  • memory_logs (7 fields)

[Records from selected table rendered here]
```

## Alignment Status

| Table | Status | Match % | Notes |
|-------|--------|---------|-------|
| ocr_logs | ✅ ALIGNED | 100% | +confidence_score field in Te Puna |
| translations | ✅ ALIGNED | 100% | Perfect match |
| memory_logs | ✅ ALIGNED | 100% | Perfect match |
| task_queue | ❌ MISSING | 0% | Operational only; not needed in archive |
| taonga_metadata | ✨ EXTRA | - | Iwi-specific archive table |
| summaries | ✨ EXTRA | - | Document abstracts for browsing |

## Backend Integration

**Access Pattern**: Read-only via Supabase anon key + RLS  
**Credentials**: TEPUNA_URL + TEPUNA_API_KEY  
**Client Factory**: `get_supabase_client("tepuna")`  
**Async Support**: Yes - `afetch_records`, `aquery_table`  

### Backend Route Example
```python
@router.get("/iwi/archive")
async def get_archive(limit: int = 20):
    # Fetch from Te Puna (read-only)
    response = await afetch_records("tepuna", "summaries", limit)
    return response
```

## Public vs Private Schema

**Public Schema** (frontend/src/data/public_schema_te_puna.json):
- Table names & descriptions
- Column names & types
- No credentials or internal details
- Safe to bundle in frontend build

**Private Schema** (backend/schema_drift_report.json):
- Full alignment analysis
- Internal use only
- Not exposed to frontend
- For admin/migration planning

## Regenerating Schema

Run locally (uses demo schema in dev mode):
```bash
cd /home/hemi-whiro/Desktop/tiwhanawhana
python scripts/scan_te_puna_schema.py
```

Outputs:
- `logs/schema_te_puna.json` ← Raw metadata
- `backend/schema_drift_report.json` ← Alignment analysis
- `logs/public_schema_te_puna.json` ← Frontend-safe
- `backend/migration_suggestions.sql` ← Recommendations

## Māori Language Support

All field names preserve te reo Māori context:
- **taonga** = treasure/cultural artifact
- **maturanga** = knowledge
- **Te Puna** = the source/wellspring
- **kaitiakitanga** = guardianship

Archive honors iwi data sovereignty with:
- ✅ Read-only enforcement (RLS at database level)
- ✅ Audit logging (all access tracked)
- ✅ Cultural context preservation
- ✅ Knowledge safeguarding

---

**Last Generated**: 2025-11-09  
**Source**: Te Puna (fyrzttjlvofmcfxibtpi) Supabase project  
**Status**: Production-ready  
**Updates**: Run scan script periodically to refresh
