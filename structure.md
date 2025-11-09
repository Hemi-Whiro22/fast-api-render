# Tiwhanawhana-Orchestrator Project Structure

```
Tiwhanawhana-Orchestrator/
├── .continue/
│   └── mcpServers/
├── .devcontainer/
├── .mauri/
│   └── prompts/
├── .supabase/
│   ├── ghost_project/
│   │   └── supabase/
│   │       ├── migrations/
│   │       └── .temp/
│   ├── migrations/
│   └── .temp/
├── .vscode/
├── Te_Po/        # Backend (Te Pō - The Night/Processing Realm)
│   ├── core/
│   ├── kaitiaki-intake/
│   │   ├── active/
│   │   ├── processed/
│   │   ├── raw/
│   │   └── raw_archive/
│   ├── logs/
│   ├── models/
│   ├── patches/
│   ├── routes/
│   │   └── tiwhanawhana/
│   ├── services/
│   │   ├── carver/
│   │   ├── core/
│   │   ├── embed/
│   │   ├── intake/
│   │   ├── mauri/
│   │   ├── memory/
│   │   ├── ocr/
│   │   ├── ruru/
│   │   └── translate/
│   ├── shared/
│   │   └── utils/
│   ├── tests/
│   ├── testsmkdir/
│   └── utils/
│       └── middleware/
├── mauri/        # Realm manifests, configs, glyphs
│   ├── prompts/
│   ├── config.py
│   ├── current_seal.json
│   ├── mauri.json
│   ├── README.txt
│   └── trace.json
├── documents/
│   └── json/
│       ├── audit_logs/
│       └── elder_reviews/
├── logs/
├── scripts/
├── services/
│   └── cli/
├── shared/
│   └── mauri/
├── supabase/
│   └── .temp/
├── Te-Ao/
│   └── src/
│       ├── assets/
│       ├── data/
│       ├── hooks/
│       └── panels/
├── tiwhanawhana/
├── touch/
├── utils/
│   └── mauri_loader.py/
├── ARCHITECTURE_DIAGRAM.md
├── chat.md
├── check_tiwhanawhana_integrity.sh
├── CHECKLIST.md
├── CLARIFICATION.md
├── COMMANDS.sh
├── DEEP_SCAN_ANALYSIS.md
├── DELIVERY.md
├── docker-compose.yaml
├── DOCKER_DEPLOYMENT_FLOW.md
├── init.sh
├── INTAKE_SETUP_GUIDE.md
├── INTEGRATION_SUMMARY.md
├── IWI_PORTAL_GUIDE.md
├── LICENSE
├── manifest.yaml
├── nano.47479.save
├── package.json
├── ProjectManifest.yaml
├── pyproject.toml
├── query_tables.py
├── QUICK_REFERENCE.md
├── README.md
├── README_INTAKE.md
├── RENDER_DEPLOY.md
├── run_tiwhanawhana.sh
├── setup.cfg
├── STAGES_EXPLAINED.md
├── start.sh
├── STRUCTURE_EXTENSION_SCAN.md
├── SUPABASE_LINK.md
├── TE_PUNA_MIGRATION_COMPLETE.md
├── TE_PUNA_SCHEMA_REPORT.md
├── TEPUNA_QUICK_REFERENCE.md
├── test_intake.sh
└── tohu_json
```

## Key Directories Explained

### Te_Po Structure (Backend - The Processing Realm)
- **Te_Po/** - Main Python/FastAPI application (Te Pō - The Night realm)
  - **core/** - Core application logic and configuration
  - **kaitiaki-intake/** - Data intake processing pipeline
    - **active/** - Currently processing files
    - **processed/** - Completed intake files
    - **raw/** - Raw unprocessed files
    - **raw_archive/** - Archived raw files
  - **services/** - Microservices architecture
    - **carver/** - Content extraction service
    - **core/** - Core service functionality
    - **embed/** - Embedding generation service
    - **intake/** - File intake service
    - **mauri/** - Cultural wisdom processing
    - **memory/** - Memory management service
    - **ocr/** - Optical character recognition
    - **ruru/** - Search and retrieval
    - **translate/** - Translation services
  - **routes/** - API route definitions
  - **models/** - Data models and schemas
  - **tests/** - Test suite

### Frontend Structure
- **Te-Ao/** - React/Vite frontend application
  - **src/** - Source code
    - **assets/** - Static assets
    - **data/** - Data files
    - **hooks/** - React hooks
    - **panels/** - UI panel components

### Configuration & Infrastructure
- **.supabase/** - Supabase configuration and migrations
- **.continue/** - Continue AI configuration
- **.devcontainer/** - Development container setup
- **.mauri/** - Cultural wisdom prompts and templates
- **scripts/** - Utility scripts
- **logs/** - Application logs
- **documents/** - Documentation and JSON data

### Root Files
- Configuration files: `pyproject.toml`, `package.json`, `docker-compose.yaml`
- Documentation: Various `.md` files with guides and references
- Scripts: Shell scripts for deployment and testing
- Manifests: `manifest.yaml`, `ProjectManifest.yaml`

## Notes
- Node modules, virtual environments, and cache directories are excluded from this structure
- The project follows a microservices architecture with clear separation of concerns
- Cultural elements (Māori terminology) are integrated throughout the naming conventions
- Both Python (backend) and JavaScript/React (frontend) components are present