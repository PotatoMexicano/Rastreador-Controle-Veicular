from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import URL
from decouple import config

# DEVELOPMENT
# database = URL.create(
#     drivername='postgresql+psycopg2',
#     username= config('DEV_DB_USER'),
#     password= config('DEV_DB_PWD'),
#     host= config('DEV_DB_HOST'),
#     port= config('DEV_DB_PORT'),
#     database= config('DEV_DB_DATABASE')
# )

# PRODUCTION
database = URL.create(
    drivername='mssql+pyodbc',
    username= config('DB_USER'),
    password= config('DB_PWD'),
    host= config('DB_HOST'),
    port= config('DB_PORT'),
    database= config('DB_DATABASE'),
    query={
        "driver": "SQL Server Native Client 11.0",
    },
)

engine = create_engine(database)

Base = declarative_base()