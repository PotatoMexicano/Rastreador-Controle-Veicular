from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import URL

database = URL.create(
    drivername='postgresql+psycopg2',
    username='postgres',
    password='root',
    host='192.168.245.212',
    port='5432',
    database='rastreador-de-veiculos'
)

# database = URL.create(
#     drivername='mssql+pyodbc',
#     username='montadroid',
#     password='md.002#',
#     host='192.168.245.17',
#     port='1433',
#     database='RastreadorVeicular',
#     query={
#         "driver": "SQL Server Native Client 11.0",
#     },
# )

engine = create_engine(database)

Base = declarative_base()