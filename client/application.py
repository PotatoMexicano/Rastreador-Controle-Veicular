import sys
from rich.console import Console
import pandas as pd
import subprocess
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text
from datetime import datetime
from sqlalchemy import URL
from pathlib import Path
import gradient_figlet

gradient_figlet.print_with_gradient_figlet(text='Rastreador Noturno', font='slant', color1='#7F00FF', color2='#78ffd6', justify='center')

production = URL.create(
    drivername='mssql+pyodbc',
    username='montadroid',
    password='md.002#',
    host='192.168.245.17',
    port='1433',
    database='RastreadorVeicular',
    query={
        "driver": "SQL Server Native Client 11.0",
    },
)
engine = create_engine(production)

db = scoped_session(sessionmaker(bind=engine))

conn = engine.connect()

database = pd.read_sql(text("select * from vehicle_event where ras_notificado = 0 order by ras_data_enviado DESC;"), conn)
update = conn.execute(text("UPDATE vehicle_event SET ras_notificado = 1"))
conn.commit()

exportPath = Path(Path(sys.executable).parent, 'exports')
exportPath.mkdir(parents=True, exist_ok=True)

fileNameExport = f'vehicle_event_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx'


console = Console(color_system='windows')
if len(database.index) >= 1:
    database.to_excel(Path(exportPath, fileNameExport), sheet_name='vehicle_event', index=False, float_format='%.2f')
    console.print("\n[green]Finalizado[/green]\n\n", justify="center")
    console.print(f'{Path(exportPath, fileNameExport)}', justify="center")
    subprocess.Popen(f'explorer /select,"{Path(exportPath, fileNameExport)}"')
else:
    console.print("\n[red]Finalizado[/red]\n\n", justify="center")
    console.print("\nNão há novas ocorrências\n", justify="center")

input()
