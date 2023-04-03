from rich.console import Console
from models.Event import Event

from rocketry.conds import minutely
from rocketry import Rocketry

from datetime import datetime, timedelta, date, time
from models.Event import Event, VehicleRole
from models.Event import ResponseVehicleRole
from models.Event import VehicleHistoric
from models.Event import TrackerResponse
import pathlib
import requests
import json
from decouple import config

app = Rocketry(execution='async')

console = Console()

class API:
    
    SECRET_KEY = config('SECRET_KEY')
    API_KEY = config('API_KEY')

def printLog(message:str) -> None:
    path = pathlib.Path(pathlib.Path(__file__).parent, 'debug.log')
    with open(path, 'a', encoding='utf-8') as file_writer:
        file_writer.write(f'[{datetime.now()}] - {message}\n')

def horario_entre_intervalo(verificar:time, inicial:time, final:time):
    
    # Verifica se os horários estão no mesmo período
    if inicial < final:
        if verificar >= inicial and verificar <= final:
            # Autorizado
            return False
        else:
            # Restrito
            return True
    else:
        if verificar >= inicial or verificar <= final:
            # Autorizado
            return False
        else:
            # Restrito
            return True

@app.task(minutely)
def load_new_data():   

    datetime_incial = datetime.combine(date.today(), time(5,0,0))
    datetime_final = datetime_incial + timedelta(hours=13)
    time_inicial = datetime_incial.time()
    time_final = datetime_final.time()

    response = requests.get(f"https://ws.fulltrack2.com/events/all/apiKey/{API.API_KEY}/secretKey/{API.SECRET_KEY}")

    registrados = 0

    if response.status_code == 200:
        json_object = json.loads(response.content)

        for row in json_object['data']:

            tracker = TrackerResponse(row)

            if tracker.ras_eve_ignicao == 1:

                if tracker.ras_eve_velocidade != 0:

                    data = (tracker.ras_eve_data_enviado).time()

                    found_initial_end = False

                    while found_initial_end != True:

                        role:ResponseVehicleRole = VehicleRole.select(tracker.ras_vei_placa)

                        if not role.found():
                            VehicleRole(ras_id = tracker.ras_vei_id, ras_placa = tracker.ras_vei_placa).create()

                        if role.found():
                            role:VehicleRole = role.scalar()

                            time_inicial = role.ras_data_inicio
                            time_final = role.ras_data_fim

                            found_initial_end = True

                    result = horario_entre_intervalo(data, time_inicial, time_final)

                    if result:

                        console.print(f"Veículo: {str(role.ras_placa).ljust(8)[:8]} [[red]{time_inicial}[/red], [red]{time_final}[/red]] -> [red]Restrito  [/red] [[red]{data}[/red]] ", end="")

                        response_add = Event(tracker).create()
                        VehicleHistoric(tracker.ras_vei_placa, tracker.ras_eve_data_enviado).create()

                        if response_add.success():

                            if int(response_add.status) == 201:
                                console.print("[bright_green]Registrado[/bright_green]")
                                registrados += 1
                            elif int(response_add.status) == 200:
                                console.print("[magenta]Atualizado[/magenta]")
                                registrados += 1
                            else:
                                console.print("")

                        if response_add.fail():
                            console.print("Erro -> ", end="")
                            console.print(f"{response_add.scalar()}")                    
                    else:
                        console.print(f"Veículo: {str(role.ras_placa).ljust(8)[:8]} [[green]{time_inicial}[/green], [green]{time_final}[/green]] -> [green]Autorizado[/green] [[green]{data}[/green]]")
                        VehicleHistoric.close(tracker.ras_vei_placa, tracker.ras_eve_data_enviado)

    if registrados > 0:
        now = datetime.strftime(datetime.now(), "%d/%m/%Y %H:%M")

        print(f"\n\n{now} Novas {registrados} ocorrências.\n\n")
        printLog(f"Novas {registrados} ocorrências.\n")
    else:
        now = datetime.strftime(datetime.now(), "%d/%m/%Y %H:%M")
        print(f"\n\n{now} Sem novas ocorrências.\n\n")

if __name__ == '__main__':
    try:
        printLog("Processo iniciado...")
        app.run()
    except KeyboardInterrupt:
        printLog("Usuário forçou encerramento\n")
        raise SystemExit
    except Exception as err:
        printLog(f" {str(err)} \n")
        raise SystemExit
