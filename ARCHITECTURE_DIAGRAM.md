# 🌊 Tiwhanawhana Architecture - Visual Guide

## Current Flow (Phase 1)

```
                          YOUR SYSTEM
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    📄 Documents (at root)
    ├─ kaitiaki-intake/
    │  └─ active/              ← YOU DROP DOCS HERE
    │     ├─ document1.md
    │     ├─ document2.json
    │     └─ document3.txt
    │
    └─ kaitiaki-dashboard/     ← UI (separate)
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                              ↓
                     [PORT 8000: FastAPI]
                    🌊 TIWHANAWHANA WATCHDOG
    
    ┌──────────────────────────────────────────────────────┐
    │ FastAPI Server (Te-Po/core/main.py) - Te Pō Realm   │
    │                                                      │
    │ Routes:                                              │
    │  ✅ GET  /ocr              (existing)                │
    │  ✅ GET  /translate        (existing)                │
    │  ✅ GET  /embed            (existing)                │
    │  ✅ GET  /memory           (existing)                │
    │  ✅ GET  /mauri            (existing)                │
    │  ✨ POST /intake/scan      (NEW)                     │
    │  ✨ GET  /intake/status    (NEW)                     │
    │  ✨ GET  /intake/documents (NEW)                     │
    │  ✨ POST /intake/process   (NEW)                     │
    │                                                      │
    │ Core Components:                                     │
    │  📡 intake_bridge.py      (NEW: Scans folder)        │
    │  📡 intake.py             (NEW: API routes)          │
    │  🔧 ocr.py, translate.py  (existing)                 │
    └──────────────────────────────────────────────────────┘
                              ↓
                     [Intake Bridge Magic]
                  (Te-Po/routes/tiwhanawhana/
                       intake_bridge.py)
    
    ┌──────────────────────────────────────────────────────┐
    │ Intake Bridge                                        │
    │                                                      │
    │ 1. Scan kaitiaki-intake/active/ every 30s            │
    │ 2. For each file:                                    │
    │    ├─ Read content                                   │
    │    ├─ Generate ID (intake_abc123)                    │
    │    ├─ Create record                                  │
    │    └─ Queue to Supabase                              │
    │ 3. Request Whiro audit                               │
    │ 4. Log to mauri_logs                                 │
    └──────────────────────────────────────────────────────┘
                              ↓
              [Queue Tasks to Supabase]
    
    ┌──────────────────────────────────────────────────────┐
    │ Supabase (Remote Database)                           │
    │                                                      │
    │ tiwhanawhana.task_queue                              │
    │  ├─ Entry 1:                                         │
    │  │  ├─ task_type: "intake_document_process"          │
    │  │  ├─ status: "pending"                             │
    │  │  ├─ priority: 2                                   │
    │  │  └─ payload: { document_id, content... }          │
    │  │                                                    │
    │  └─ Entry 2:                                         │
    │     ├─ task_type: "whiro_audit_document"             │
    │     ├─ status: "pending"                             │
    │     ├─ priority: 3                                   │
    │     └─ payload: { document_id, content... }          │
    │                                                      │
    │ tiwhanawhana.mauri_logs                              │
    │  └─ { message: "Document intake_abc123 received... } │
    │                                                      │
    │ audit_logs (FUTURE - Whiro)                          │
    │  └─ (empty for now - Whiro will fill this)           │
    │                                                      │
    └──────────────────────────────────────────────────────┘
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                        🟢 PHASE 1 COMPLETE
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Phase 2 (Coming Soon - Whiro Added)

```
    [Same as Phase 1 above] ✓
                            ↓
                     [From Supabase]
                    
    ┌──────────────────────────────────────────────────────┐
    │ 🛡️ WHIRO AUDITOR (Phase 2)                          │
    │                                                      │
    │ 1. Listen to task_queue                              │
    │    (task_type = "whiro_audit_document")              │
    │ 2. For each task:                                    │
    │    ├─ Read document content                          │
    │    ├─ Analyze cultural sensitivity                   │
    │    ├─ Check UTF-8 encoding                           │
    │    ├─ Check language compliance                      │
    │    ├─ Determine compliance status                    │
    │    └─ Generate audit report                          │
    │ 3. Save to audit_logs                                │
    │ 4. Update task_queue status = "completed"            │
    │                                                      │
    │ Location:                                            │
    │  backend/matua_whiro/kaitiaki/whiro/               │
    │  whiro_intake_processor.py                           │
    │                                                      │
    └──────────────────────────────────────────────────────┘
                            ↓
                  [Write Results to Supabase]
                            ↓
    ┌──────────────────────────────────────────────────────┐
    │ Supabase - Complete Audit Trail                      │
    │                                                      │
    │ tiwhanawhana.task_queue                              │
    │  ├─ Entry 1: status = "completed" ✅                 │
    │  └─ Entry 2: status = "completed" ✅                 │
    │                                                      │
    │ audit_logs (NOW POPULATED)                           │
    │  └─ {                                                │
    │      audit_id: "whiro_xyz789",                       │
    │      document_id: "intake_abc123",                   │
    │      compliance_status: "compliant",                 │
    │      cultural_analysis: { ... },                     │
    │      recommended_action: "APPROVE"                   │
    │    }                                                 │
    │                                                      │
    └──────────────────────────────────────────────────────┘
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                      🟢 PHASE 2 COMPLETE
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Phase 3 (Optional - More Agents)

```
    [Phase 1 + 2 above] ✓
                        ↓
           [From task_queue Supabase]
                        ↓
    
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │  🧠 RONGOHIA │  │  📊 KITENGA  │  │  🌿 HINEWAI │
    │  Knowledge  │  │  Data Intell │  │  Purifier   │
    │  Indexing   │  │  Analysis    │  │  (UTF-8)    │
    │             │  │              │  │             │
    │ Listen:     │  │ Listen:      │  │ Listen:     │
    │  index_docs │  │  analyze_doc │  │  clean_text │
    └─────────────┘  └─────────────┘  └─────────────┘
            ↓              ↓                  ↓
    
    ┌──────────────────────────────────────────────────────┐
    │ 🌟 AOTAHI - COLLECTIVE INTELLIGENCE                  │
    │ (Coordinates all agents + balances workflow)         │
    │                                                      │
    │ Manages:                                             │
    │  • Task distribution                                 │
    │  • Agent coordination                                │
    │  • Workflow optimization                             │
    │  • System harmony monitoring                         │
    └──────────────────────────────────────────────────────┘
                            ↓
    ┌──────────────────────────────────────────────────────┐
    │ Supabase - Full Audit Trail + Analysis               │
    │                                                      │
    │ tiwhanawhana.task_queue (all completed)              │
    │ audit_logs (full cultural compliance)                │
    │ rongohia.knowledge_index (documents indexed)         │
    │ kitenga.analysis_results (data insights)             │
    │ hinewai.sanitization_log (text cleaned)              │
    │                                                      │
    └──────────────────────────────────────────────────────┘
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                   🟢 PHASE 3 COMPLETE (Optional)
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Component Interaction Summary

```
TIER 1 - UI/Input
├─ kaitiaki-dashboard      (Vue/React - monitoring)
├─ kaitiaki-intake         (Document folder)
└─ API Endpoints           (FastAPI /intake/*)

TIER 2 - Orchestration
├─ Tiwhanawhana Watchdog   (FastAPI - core)
├─ Intake Bridge           (Scanner - monitors folder)
└─ FastAPI Routes          (API layer)

TIER 3 - Processing
├─ Whiro Auditor           (Validates documents)
├─ Rongohia Knowledge      (Indexes content)
├─ Kitenga Data            (Analyzes data)
├─ Hinewai Purifier        (Cleans text)
└─ Others (as needed)

TIER 4 - Coordination (Optional)
└─ Aotahi Collective       (Manages all agents)

TIER 5 - Storage
├─ Supabase (Remote)       (Documents + audit trail)
├─ task_queue Table        (Work queue)
├─ audit_logs Table        (Compliance trail)
└─ mauri_logs Table        (System lifecycle)
```

## Key Files

```
✅ Core (Existing)
├─ backend/main.py
├─ backend/routes/tiwhanawhana/ocr.py
├─ backend/routes/tiwhanawhana/translate.py
├─ backend/routes/tiwhanawhana/embed.py
├─ backend/routes/tiwhanawhana/memory.py
└─ backend/routes/tiwhanawhana/mauri.py

✨ NEW (Phase 1)
├─ backend/routes/tiwhanawhana/intake.py         (FastAPI routes)
├─ backend/routes/tiwhanawhana/intake_bridge.py  (Scanner)
└─ (updated) backend/main.py                     (import intake)

🛡️ NEXT (Phase 2 Template)
└─ backend/matua_whiro/kaitiaki/whiro/WHIRO_INTAKE_TEMPLATE.py

📚 Documentation
├─ INTAKE_SETUP_GUIDE.md
├─ QUICK_REFERENCE.md
├─ INTEGRATION_SUMMARY.md
├─ CHECKLIST.md
└─ test_intake.sh (test script)
```

---

**Status**: Phase 1 code ready. Phase 2 template provided. Phase 3 optional.

You're good to test! 🚀

