import os
from urllib.parse import quote_plus

DATABASE_DIALECT = os.environ.get("DATABASE_DIALECT", "postgresql")
DATABASE_USER = quote_plus(os.environ["DATABASE_USER"])
DATABASE_PASSWORD = quote_plus(os.environ["DATABASE_PASSWORD"])
DATABASE_HOST = os.environ["DATABASE_HOST"]
DATABASE_PORT = os.environ["DATABASE_PORT"]
DATABASE_NAME = os.environ["DATABASE_DB"]

SQLALCHEMY_DATABASE_URI = (
    f"{DATABASE_DIALECT}+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}"
    f"@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
)
SECRET_KEY = os.environ["SUPERSET_SECRET_KEY"]
WTF_CSRF_ENABLED = True
