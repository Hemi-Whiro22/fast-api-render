#!/usr/bin/env bash
echo "🌕 Initialising Tiwhanawhana Orchestrator..."
sleep 1

# backend setup
mkdir -p backend/app frontend .vscode .devcontainer

cat > backend/app/main.py <<'EOF'
from fastapi import FastAPI

app = FastAPI(title="Tiwhanawhana Orchestrator")

@app.get("/")
def root():
    return {"status": "awake", "message": "Tiwhanawhana Orchestrator online 🌕"}
EOF

# simple requirements
cat > backend/requirements.txt <<'EOF'
fastapi
uvicorn
pydantic
pgvector
supabase
openai
EOF

# frontend scaffold placeholder
cat > frontend/package.json <<'EOF'
{
  "name": "tiwhanawhana-frontend",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  }
}
EOF

# VSCode setup
cat > .vscode/settings.json <<'EOF'
{
  "workbench.colorTheme": "Default Dark Modern",
  "editor.fontFamily": "JetBrains Mono, Consolas, monospace",
  "editor.fontSize": 14,
  "editor.formatOnSave": true
}
EOF

# Devcontainer
cat > .devcontainer/devcontainer.json <<'EOF'
{
  "name": "Tiwhanawhana Orchestrator",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "features": {
    "ghcr.io/devcontainers/features/node:1": {
      "version": "20"
    }
  },
  "postCreateCommand": "pip install -r backend/requirements.txt && cd frontend && npm install",
  "forwardPorts": [8000, 5173],
  "remoteUser": "vscode"
}
EOF

echo "✅ Tiwhanawhana scaffold complete."
echo "→ Run Te-Po: uvicorn Te_Po.core.main:app --reload"
echo "→ Run frontend: cd frontend && npm run dev"
404: Not Found
# === 7. Generate helper scripts ===
echo "⚙️  Creating helper scripts..."
mkdir -p scripts

cat > scripts/setup_env.py << 'EOF'
#!/usr/bin/env python3
import os
def create_env():
    env_path = os.path.join("backend", ".env")
    if os.path.exists(env_path):
        print("✅ .env already exists.")
        return
    template = """# Tiwhanawhana .env
OPENAI_API_KEY=
DEN_URL=
DEN_API_KEY=
DEN_DB_URL=postgresql://postgres:password@localhost:5432/tiwhanawhana
TEPUNA_URL=
TEPUNA_API_KEY=
TEPUNA_DB_URL=
EMBEDDING_MODEL=text-embedding-3-large
OCR_MODEL=gpt-4o-mini
"""
    os.makedirs("backend", exist_ok=True)
    with open(env_path, "w") as f:
        f.write(template)
    print("🌿 Created backend/.env")
if __name__ == "__main__":
    create_env()
EOF

chmod +x scripts/setup_env.py
echo "✅ setup_env.py ready."

cat > scripts/dev_start.sh << 'EOF'
#!/usr/bin/env bash
echo "🌕 Starting Tiwhanawhana dev environment..."
cd backend || exit
if [ ! -f ".env" ]; then
  echo "⚠️  No .env found. Run: python3 ../scripts/setup_env.py"
  exit 1
fi
uvicorn app.main:app --reload &
cd ../frontend && npm install && npm run dev &
wait
EOF
chmod +x scripts/dev_start.sh

cat > scripts/build_frontend.sh << 'EOF'
#!/usr/bin/env bash
cd frontend || exit
npm install && npm run build
EOF
chmod +x scripts/build_frontend.sh

cat > scripts/check_status.py << 'EOF'
#!/usr/bin/env python3
import psutil
print("🔍 Checking Tiwhanawhana ports...")
for conn in psutil.net_connections():
    if conn.laddr.port in (8000, 5173):
        print(f"✅ Port {conn.laddr.port} active (PID {conn.pid})")
EOF

echo "✅ All helper scripts created."
# === 9. Mauri Layer (SVGs, Glyphs, Meta) ===
echo "🎨 Loading Tiwhanawhana mauri layer..."
mkdir -p assets/svg assets/glyphs mauri/meta

# --- Default Glyphs ---
cat > assets/svg/koru_spiral.svg << 'EOF'
<svg width="300" height="300" viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg">
  <circle cx="150" cy="150" r="120" stroke="#00FFAA" stroke-width="4" fill="none"/>
  <path d="M150,270
           C75,240,60,150,120,90
           C180,30,270,75,240,150
           C210,225,120,240,150,270Z"
        fill="none" stroke="#007755" stroke-width="4"/>
  <circle cx="150" cy="150" r="8" fill="#00FFAA"/>
</svg>
EOF

cat > assets/svg/wolf_toho.svg << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
  <path fill="#00E5FF" d="M128 12c-8 14-20 30-28 42-22 32-50 60-80 86l52 30c16 9 26 26 26 44v20l30-10 30 10v-20c0-18 10-35 26-44l52-30c-30-26-58-54-80-86-8-12-20-28-28-42z"/>
</svg>
EOF

# --- Metadata file (manifest) ---
cat > mauri/meta/mauri_manifest.json << 'EOF'
{
  "project": "Tiwhanawhana Orchestrator",
  "glyphs": ["koru_spiral.svg", "wolf_toho.svg"],
  "version": "1.0.0",
  "theme": {
    "primary": "#00FFAA",
    "accent": "#007755",
    "background": "#0A0A0A",
    "text": "#E0E0E0"
  },
  "cloak": {
    "mana": "high",
    "taputapu": "AwaNet",
    "carver": "Adrian Hemi",
    "co_creator": "Kitenga"
  }
}
EOF

echo "🌿 Mauri glyphs and manifest written to assets/ + mauri/meta/"
echo "✅ Tiwhanawhana Orchestrator setup complete! 🌕"