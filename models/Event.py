from datetime import datetime, timedelta, time
from sqlalchemy import Column, Integer, String, DateTime, Time, Boolean
from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker
from database import Base, engine
from psycopg2 import errors
from sqlalchemy.exc import IntegrityError

Session = sessionmaker(bind = engine)
session = Session()

class Response:
    object:any
    status:int

    def __repr__(self) -> str:
        return f"<Response: {self.object}, {self.status}>"

    def __init__(self, object:any, status:int) -> None:
        self.object = object
        self.status = status

    def scalar(self):
        return self.object

    def success(self) -> bool:
        status = [200, 201, 304]

        if self.status in status:
            return True
        return False

    def fail(self) -> bool:
        status = [400, 404, 409, 500]

        if self.status in status:
            return True
        return False

    def bool(self) -> bool:

        if self.success():
            return True

        if self.fail():
            return False
        
class ResponseVehicleRole(Response):
    
    def found(self) -> bool:
        status = [200]

        if self.status in status:
            return True
        
        return False

class TrackerResponse:
    ras_eve_ignicao:int
    ras_eve_velocidade:int
    ras_vei_placa:str
    ras_vei_id:int
    ras_ras_sinal_gps:int
    ras_eve_data_enviado:datetime
    ras_ras_data_ult_comunicacao:datetime
    ras_eve_longitude:str
    ras_eve_latitude:str

    def __init__(self, data) -> None:
        self.ras_eve_ignicao = int(data['ras_eve_ignicao'])
        self.ras_eve_velocidade = int(data['ras_eve_velocidade'])
        self.ras_vei_placa = str(data['ras_vei_placa'])
        self.ras_vei_id = int(data['ras_vei_id'])
        self.ras_ras_sinal_gps = int(data['ras_ras_sinal_gps'])
        self.ras_eve_longitude = str(data['ras_eve_longitude'])
        self.ras_eve_latitude = str(data['ras_eve_latitude'])

        self.ras_eve_data_enviado = datetime.strptime( data['ras_eve_data_enviado'], '%d/%m/%Y %H:%M:%S' ) + timedelta(hours=-3)
        self.ras_ras_data_ult_comunicacao = datetime.strptime( data['ras_ras_data_ult_comunicacao'], '%d/%m/%Y %H:%M:%S' ) + timedelta(hours=-3)

    def __repr__(self) -> str:
        return f"<Tracker: {self.ras_vei_placa}>"

class VehicleRole(Base):
    __tablename__ = 'vehicle_role'

    id:int = Column(Integer, primary_key=True, autoincrement=True)

    ras_id:int = Column(Integer, nullable=True)
    ras_placa:str = Column(String(25), nullable=False, unique=True)

    ras_data_inicio:str = Column(Time, nullable=False, default=time(hour=5, minute=0, second=0))
    ras_data_fim:str = Column(Time, nullable=False, default=time(hour=18, minute=0, second=0))

    create_at:datetime = Column(DateTime, nullable=False, default=datetime.now)
    update_at:datetime = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Role: {self.ras_placa}>"

    def create(self) -> bool:

        response:ResponseVehicleRole = VehicleRole.select(self.ras_placa)

        if not response.found():
            try:
                session.add(self)
                session.commit()
                session.refresh(self)
                # print(self)
                return Response(self, 201)
            except Exception as err:
                print(f"Error on created vehicle_role: {self}")
                return Response(err, 500)

    def select(placa:str) -> ResponseVehicleRole:

        if not placa:
            return False

        raw = select(VehicleRole).where(VehicleRole.ras_placa == placa)

        response = session.execute(raw).scalar_one_or_none()

        if response:
            return ResponseVehicleRole(response, 200)

        return ResponseVehicleRole(None, 404)

    def update(self) -> Response:

        try:
            session.query(VehicleRole).where(VehicleRole.ras_placa == str(self.ras_placa)).update({
                Event.update_at: datetime.now()
            })

            session.commit()
            session.refresh(self)
            print(f"Updated vehicle_role: {self}")
            return Response(self, 200)
        except:
            return Response(self, 400)
  
class Event(Base):
    __tablename__ = 'vehicle_event'

    id:int = Column(Integer, primary_key=True, autoincrement=True)
    ras_id:int = Column(Integer, nullable=True)
    ras_longitude:str = Column(String(50), nullable=False)
    ras_latitude:str = Column(String(50), nullable=False)
    ras_data_enviado:datetime = Column(DateTime, nullable=False)
    ras_data_ult_comunicacao:datetime = Column(DateTime, nullable=False)
    ras_sinal_gps:int = Column(Integer, nullable=False)
    ras_ignicao:int = Column(Integer, nullable=False)
    ras_placa:str = Column(String(25), nullable=False, unique=True)
    ras_notificado:int = Column(Integer, nullable=False, default=0)

    create_at:datetime = Column(DateTime, nullable=False, default=datetime.now)
    update_at:datetime = Column(DateTime, nullable=True)
    
    def __init__(self, tracker:TrackerResponse) -> None:

        self.ras_longitude = str(tracker.ras_eve_longitude).strip()
        self.ras_latitude = str(tracker.ras_eve_latitude).strip()
        self.ras_data_enviado = tracker.ras_eve_data_enviado
        self.ras_data_ult_comunicacao = tracker.ras_ras_data_ult_comunicacao
        self.ras_id = tracker.ras_vei_id
        self.ras_sinal_gps = tracker.ras_ras_sinal_gps
        self.ras_ignicao = tracker.ras_eve_ignicao
        self.ras_placa = str(tracker.ras_vei_placa).strip()
    
    def __repr__(self) -> str:
        return f"<Event: {self.ras_placa}>"

    def checkDataDB(self) -> bool:

        veiculo = session.query(Event).where(Event.ras_placa == self.ras_placa).one_or_none()

        if veiculo:
            if self.ras_data_enviado > veiculo.ras_data_enviado:
                return True
            else:
                return False

    def updateDB(self) -> Response:

        will_update = self.checkDataDB()
        if will_update:
            # A data atual é superior a data registrada no banco de dados
            try:
                session.query(Event).where(Event.ras_placa == str(self.ras_placa)).update({
                    Event.ras_latitude: self.ras_latitude, 
                    Event.ras_longitude: self.ras_longitude, 
                    Event.ras_data_enviado: self.ras_data_enviado, 
                    Event.ras_data_ult_comunicacao: self.ras_data_ult_comunicacao,
                    Event.ras_placa: str(self.ras_placa),
                    Event.ras_notificado: 0,
                    Event.update_at: datetime.now()
                })

                VehicleRole(ras_id = self.ras_id, ras_placa = self.ras_placa).update()

                session.commit()

                # print(f"Updated vehicle: {self}")

                return Response(self, 200)
            except Exception as err:
                return Response(err, 500)
        else:
            return Response(None, 304)
        
    def create(self) -> Response:

        hasDB = int(session.query(Event).where(Event.ras_placa == str(self.ras_placa)).count())
        
        if hasDB > 0:
            response = self.updateDB()
            return Response(response.bool(), response.status)
        
        if hasDB <= 0:
            try:
                session.add(self)
                session.commit()
                session.refresh(self)
                VehicleRole(ras_id = self.ras_id, ras_placa = self.ras_placa).create()
                return Response(self, 201)

            except IntegrityError as err:
                return Response(err, 500)
            except errors.UniqueViolation as err:
                return Response(err, 500)
            except Exception as err:
                return Response(err, 500)

class VehicleHistoric(Base):
    __tablename__ = 'vehicle_historic'

    id:int = Column(Integer, primary_key=True, autoincrement=True)

    ras_placa:str = Column(String(25), nullable=False)

    inicio_atividade:datetime = Column(DateTime, nullable=False)
    fim_atividade:datetime = Column(DateTime, nullable=True)

    finalizado_atividade:bool = Column(Boolean, default=False, nullable=False)

    finalizado_descricao:str = Column(String(255), nullable=True)

    create_at:datetime = Column(DateTime, nullable=False, default=datetime.now)
    finish_at:datetime = Column(DateTime, nullable=True)

    def __init__(self, placa:str, inicio:datetime) -> None:

        self.ras_placa =  placa
        self.inicio_atividade = inicio
    
    def __repr__(self) -> str:
        return f"<Historic: {self.ras_placa}>"
    
    def select(placa:str, status:bool = False) -> ResponseVehicleRole:


        response = session.query(VehicleHistoric).filter(VehicleHistoric.ras_placa == placa)

        response = response.filter(VehicleHistoric.finalizado_atividade == status)

        response = response.all()

        if ((not response) or (len(response) <= 0)):
            return ResponseVehicleRole(None, 404)
        
        return ResponseVehicleRole(response, 200)
    
    def close(placa:str, final:datetime):

        session.query(VehicleHistoric).where(VehicleHistoric.ras_placa == str(placa)).update({
            VehicleHistoric.fim_atividade: final,
            VehicleHistoric.finalizado_atividade: True,
            VehicleHistoric.finish_at: datetime.now()
        })
        session.commit()

    def create(self) -> Response:

        veiculos_nao_fechados =  VehicleHistoric.select(placa=self.ras_placa, status=False).scalar()

        if ((veiculos_nao_fechados == None) or (len(veiculos_nao_fechados) == 0)):
            session.add(self)
            session.commit()
            session.refresh(self)

            return Response(self, 201)
