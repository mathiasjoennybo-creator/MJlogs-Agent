from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from engine import Medarbejder, Vagt, Vagtplanlaegger

# 1. API Opsætning
app = FastAPI(title="Planday-Killer API", version="1.0")

# 2. Datamodeller (Krav til indkommende data)
class VagtInput(BaseModel):
    dag: str
    timer: int

class PersonInput(BaseModel):
    navn: str
    type: str
    timelon: int
    max_timer: int

class API_Request(BaseModel):
    budget: int
    vagter: List[VagtInput]
    personale: List[PersonInput]

# 3. ENDPOINT (Den digitale dør)
@app.post("/api/v1/optimer-vagtplan")
async def beregn_vagtplan(data: API_Request):
    
    # A. Oversæt indkommende JSON-data til Python Objekter
    personale_db = [Medarbejder(**p.dict()) for p in data.personale]
    uge_vagter = [Vagt(**v.dict()) for v in data.vagter]
    
    # B. Start Motoren (Importeret fra engine.py)
    motor = Vagtplanlaegger(budget=data.budget)
    resultat = motor.optimer_plan(uge_vagter, personale_db)
    
    # C. Send det færdige regnskab tilbage til Appen
    return {
        "status": "success",
        "data": resultat
    }