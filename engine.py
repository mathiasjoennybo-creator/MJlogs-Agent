from dataclasses import dataclass
from typing import List, Dict, Any

# 1. DEFINITION AF VERDEN (Objekter)
@dataclass
class Medarbejder:
    navn: str
    type: str
    timelon: int
    max_timer: int
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
        self.log = []

    def optimer_plan(self, vagter: List[Vagt], personale: List[Medarbejder]) -> Dict[str, Any]:
        self.log.append("STARTER AUTOMATISK ALLOKERING...")
        
        # Sorter personalet (billigste først)
        personale.sort(key=lambda x: x.timelon)

        for vagt in vagter:
            vagt_daekket = False
            
            for person in personale:
                # Regel 1: Max timer
                if person.timer_brugt + vagt.timer > person.max_timer:
                    continue
                
                # Regel 2: Budget
                vagt_pris = vagt.timer * person.timelon
                if self.forbrugt + vagt_pris > self.budget:
                    self.log.append(f"ADVARSEL: Råd ikke til at sætte {person.navn} på om {vagt.dag}.")
                    continue
                
                # SUCESS
                vagt.tildelt_til = person.navn
                vagt.status = "Dækket"
                person.timer_brugt += vagt.timer
                self.forbrugt += vagt_pris
                vagt_daekket = True
                
                self.log.append(f"[SUCCES] Tildelte {vagt.timer}t om {vagt.dag} til {person.navn}")
                break
            
            if not vagt_daekket:
                self.log.append(f"[FEJL] Kunne ikke finde dækning til {vagt.dag}.")

        # 3. OUTPUT (Pakker resultatet pænt sammen til API'et)
        return {
            "startbudget": self.budget,
            "forbrugt": self.forbrugt,
            "overskud": self.budget - self.forbrugt,
            "vagter": [{"dag": v.dag, "timer": v.timer, "tildelt_til": v.tildelt_til, "status": v.status} for v in vagter],
            "log": self.log
        }
