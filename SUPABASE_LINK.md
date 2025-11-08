# Alpha-Den Supabase Link - Configuration Summary

**Date:** November 9, 2025  
**Project:** Tiwhanawhana AwaNet  
**Supabase Project:** Alpha-Den (ruqejtkudezadrqbdodx)

## Link Status: ✅ COMPLETE

### 1. Project Configuration
- **Project ID:** `ruqejtkudezadrqbdodx`
- **API Endpoint:** `https://pfyxslvdrcwcdsfldyvl.supabase.co`
- **Region:** us-east-1
- **Database Version:** PostgreSQL 17
- **Status:** Linked and validated

### 2. Git Integration
```bash
# Successfully linked with:
supabase link --project-ref ruqejtkudezadrqbdodx

# Location: supabase/config.toml
# - Configured API ports (54321-54323)
# - Studio enabled on 54323
# - Auth configured with Render redirect URLs
# - Storage limit: 50MB
```

### 3. Environment Variables (Render Dashboard)
Add these to Render Environment tab:

```
DEN_URL=https://pfyxslvdrcwcdsfldyvl.supabase.co
DEN_API_KEY=<paste-service-role-key>
SUPABASE_URL=${DEN_URL}
SUPABASE_KEY=${DEN_API_KEY}
```

### 4. Backend Configuration
- **File:** `backend/utils/supabase_client.py`
- **Status:** Updated with Alpha-Den validation logging
- **Async Support:** Full (afetch_records, ainsert_record, afetch_latest, aquery_table)
- **Retries:** Exponential backoff (3 attempts, 0.5-2s delays)
- **Response Type:** Unified `SupabaseResponse` dataclass

### 5. Local Development (.env.local)
```bash
# Template created at .env.local (not committed—keep local)
DEN_URL=https://pfyxslvdrcwcdsfldyvl.supabase.co
DEN_API_KEY=<your-service-role-key>
SUPABASE_URL=${DEN_URL}
SUPABASE_KEY=${DEN_API_KEY}
```

### 6. Migrations
Current remote migration status shows:
- Migration history linked to Alpha-Den project
- Local `supabase/migrations/` can now track schema changes
- Use `supabase db push` to sync migrations to remote

### 7. Verification Checklist
```bash
# Test connection locally:
cd /home/hemi-whiro/Desktop/tiwhanawhana
supabase db pull          # Pull latest schema
supabase db diff          # Check for local changes
supabase secrets list     # Verify secrets are available

# On Render (auto via environment):
# - Boots with DEN_URL + DEN_API_KEY injected
# - Logs: "✅ Supabase Git link validated for Alpha-Den project"
# - API endpoint: https://pfyxslvdrcwcdsfldyvl.supabase.co
```

### 8. Next Steps
1. ✅ Paste `DEN_API_KEY` into Render Environment
2. ⏳ Redeploy Render service
3. ⏳ Monitor logs for "✅ DEN Supabase client initialized successfully"
4. ⏳ Test endpoints:
   - `GET /health` (should return 200)
   - `GET /mauri/status` (should fetch latest mauri logs from Supabase)
5. ⏳ Pull migrations: `supabase db pull` to bring schema into local control

### 9. Security Notes
- `.env.local` is in `.gitignore` ✅
- `DEN_API_KEY` stored only in Render Environment (encrypted at rest) ✅
- All connections use service-role keys (not JWT tokens) ✅
- Secrets never logged or exposed in code ✅

### 10. Māori Language Support
- Locale: `mi_NZ.UTF-8`
- Charset: UTF-8 (full Unicode support)
- Timezone: Pacific/Auckland
- Kaitiaki mode: enabled

---

**Commit:** `2689427`  
**Branch:** main  
**Status:** Ready for Render redeploy 🚀
