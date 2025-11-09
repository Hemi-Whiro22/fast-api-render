import os, sys, locale
from dotenv import load_dotenv
from supabase import create_client, Client

# ──────────────────────────────────────────────────────────────
# Load .env and enforce locale / encoding
# ──────────────────────────────────────────────────────────────
def init_locale():
    try:
        locale.setlocale(locale.LC_ALL, "mi_NZ.UTF-8")
    except locale.Error:
        locale.setlocale(locale.LC_ALL, "en_NZ.UTF-8")
    sys.stdout.reconfigure(encoding="utf-8")
    os.environ["PYTHONIOENCODING"] = "utf-8"

def load_env():
    env_path = os.path.expanduser("~/.env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        raise FileNotFoundError(f"❌  Missing {env_path}")

# ──────────────────────────────────────────────────────────────
# Initialize Supabase clients for both projects
# ──────────────────────────────────────────────────────────────
def init_supabase_clients() -> dict[str, Client]:
    den_url  = os.getenv("DEN_URL")
    den_key  = os.getenv("DEN_API_KEY")
    te_url   = os.getenv("TEPUNA_URL")
    te_key   = os.getenv("TEPUNA_API_KEY")

    if not all([den_url, den_key, te_url, te_key]):
        raise EnvironmentError("Missing Supabase URLs or API keys in .env")

    den_client = create_client(den_url, den_key)
    tepuna_client = create_client(te_url, te_key)
    return {"den": den_client, "tepuna": tepuna_client}

# ──────────────────────────────────────────────────────────────
# Initialize OpenAI configuration
# ──────────────────────────────────────────────────────────────
def init_openai():
    openai_key = os.getenv("OPENAI_API_KEY")
    openai_dev = os.getenv("OPENAI_DEV_KEY")
    model_main = os.getenv("OPENAI_MODEL", "gpt-5")
    model_local = os.getenv("LOCAL_MODEL", "llama3")
    agent_name = os.getenv("AGENT_NAME", "tiwhanawhana")
    return {
        "api_key": openai_key,
        "dev_key": openai_dev,
        "model_main": model_main,
        "model_local": model_local,
        "agent_name": agent_name,
    }

# ──────────────────────────────────────────────────────────────
# Global bootstrap
# ──────────────────────────────────────────────────────────────
def bootstrap():
    init_locale()
    load_env()
    clients = init_supabase_clients()
    openai_conf = init_openai()
    print(f"🌿 Tiwhanawhana loaded with locale {locale.getlocale()} and agent {openai_conf['agent_name']}")
    return clients, openai_conf

# Example usage:
# clients, openai_conf = bootstrap()
