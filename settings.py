"""this file is used simply to setup background worker with render.com"""
import os

if os.path.exists("env_config.py"):
    import env_config
from dotenv import load_dotenv

load_dotenv()
if not os.path.exists("env_config.py"):
    REDIS_URL = os.getenv("REDIS_URL")
else:
    REDIS_URL = env_config.REDIS_URL

QUEUES = ["emails", "default"]
