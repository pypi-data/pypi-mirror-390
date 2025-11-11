from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent


env = environ.Env(DEBUG=True, LOG_LEVEL="warn")

env.read_env(str(BASE_DIR / ".env"))
