from sqlalchemy import create_engine


DATABASE_URL = (
    "postgresql+psycopg://supportflow:"
    "supportflow_dev_password@127.0.0.1:5433/supportflow"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)