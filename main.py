import time
from dataclasses import dataclass
from typing import List

# 1. DEFINITION AF VERDEN (Objekter)
@dataclass
class Medarbejder:
    navn: str
    type: str       # F.eks. "Ungarbejder" eller "Senior"
    timeløn: int
    max_timer: int  # Hvor mange timer de MÅ arbejde pr. uge
    timer_brugt: int = 0

@dataclass
class Vagt:
    dag: str
    timer: int
    status: str = "Ubesat"
    tildelt_til: str = "Ingen"

# 2. ALGORITMEN (Den kunstige hjerne)
class Vagtplanlaegger:
    def __init__(self, budget: int):
        self.budget = budget
        self.forbrugt = 0
        self.log = [] # Gemmer systemets tanker

    def optimer_plan(self, vagter: List[Vagt], personale: List[Medarbejder]):
        self.log.append("STARTER AUTOMATISK ALLOKERING...")
        
        # Sorter personalet, så systemet ALTID prøver at bruge den billigste først (Profit-optimering)
        personale.sort(key=lambda x: x.timeløn)

        for vagt in vagter:
            vagt_dækket = False
            
            for person in personale:
                # Regel 1: Har personen plads i sit timeregnskab?
                if person.timer_brugt + vagt.timer > person.max_timer:
                    continue # Gå videre til den næste person
                
                # Regel 2: Er der råd i budgettet?
                vagt_pris = vagt.timer * person.timeløn
                if self.forbrugt + vagt_pris > self.budget:
                    self.log.append(f"ADVARSEL: Råd ikke til at sætte {person.navn} på om {vagt.dag}.")
                    continue
                
                # SUCESS: Reglerne er overholdt, tildel vagten!
                vagt.tildelt_til = person.navn
                vagt.status = "Dækket"
                person.timer_brugt += vagt.timer
                self.forbrugt += vagt_pris
                vagt_dækket = True
                
                self.log.append(f"[SUCCES] Tildelte {vagt.timer}t om {vagt.dag} til {person.navn} ({person.timeløn} kr/t)")
                break # Vagten er dækket, stop med at lede
            
            if not vagt_dækket:
                self.log.append(f"[FEJL] Kunne ikke finde dækning til {vagt.dag}. Budget eller timer er opbrugt!")

# 3. KØRSLEN (Test af systemet offline)
if __name__ == "__main__":
    print("--- ENTERPRISE ENGINE V1.0 ---")
    
    # Vi opretter vores personale
    personale_db = [
        Medarbejder("Lukas (Ung)", "Ungarbejder", 75, max_timer=10),
        Medarbejder("Emma (Ung)", "Ungarbejder", 75, max_timer=10),
        Medarbejder("Jens (Senior)", "Senior", 160, max_timer=37)
    ]
    
    # Vi opretter ugens vagter (I alt 32 timer)
    uge_vagter = [
        Vagt("Mandag", 8),
        Vagt("Tirsdag", 8),
        Vagt("Onsdag", 8),
        Vagt("Torsdag", 8)
    ]
    
    # Vi starter motoren med et stramt budget på 3.500 kr.
    motor = Vagtplanlaegger(budget=3500)
    
    # Vi lader systemet tænke...
    print("Beregner optimal rute...")
    time.sleep(1) 
    motor.optimer_plan(uge_vagter, personale_db)
    
    # Udskriv systemets logik
    print("\n--- SYSTEMETS TANKER ---")
    for tanke in motor.log:
        print(tanke)
        
    # Udskriv det endelige regnskab
    print(f"\n--- BUNDLINJE ---")
    print(f"Startbudget: {motor.budget} kr")
    print(f"Forbrugt:    {motor.forbrugt} kr")
    print(f"Overskud:    {motor.budget - motor.forbrugt} kr\n")