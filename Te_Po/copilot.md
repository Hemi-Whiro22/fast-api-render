# 🪶 Tiwhanawhana Project Context

## SYSTEM
- **Tiwhanawhana** = FastAPI main service (port 8000)
- **Intake Bridge** = Scanner → Supabase.task_queue
- **Whiro** = Auditor (Phase 2 template)
- **Mataroa** = Local navigator (agent CLI)
- **Rongohia** = Historian (archive / embed)
- **Supabase Schema** = `tiwhanawhana.*`
- **Public Queue** = `public.task_queue`

## DEPLOYMENT
- **Local:** `docker-compose up`
- **Cloud:** Render → `render.yaml`
- **Env Vars:** in `.env`
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `OPENAI_API_KEY`
  - `ENABLE_KAITIAKI_DELEGATION=true`

## TEST FLOW
1. Run `docker-compose up`
2. Drop file in `kaitiaki-intake/active`
3. `curl -X POST http://localhost:8000/intake/scan`
4. Confirm row in `tiwhanawhana.task_queue`
5. Run `./test_intake.sh`

## CONVENTIONS
- All new tables live under **tiwhanawhana.***
- Audits under **whiro.audit_logs**
- One public port 8000 only
- Use **Supabase task_queue** for async jobs

## NEXT TASKS
- ✅ Phase 1 Intake tested
- ⏳ Push to Render
- 🟡 Implement Whiro watcher (Phase 2)
