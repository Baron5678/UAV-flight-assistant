from sqlalchemy.engine import URL
import os

def getenv(key: str) -> str:
    v = os.getenv(key)
    if not v:
        raise RuntimeError(f"Missing required env var: {key}")
    return v

def build(env_drivername: str, env_username: str, env_password: str, env_host: str, env_port :str,  env_database: str) -> URL:
    return URL.create(
    drivername=getenv(env_drivername),
    username=getenv(env_username),
    password=getenv(env_password),
    host=getenv(env_host),
    port=int(getenv(env_port)),
    database=getenv(env_database),
)
