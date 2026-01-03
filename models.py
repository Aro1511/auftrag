from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Auftraggeber:
    id: int
    name: str
    adresse: str
    email: str
    telefon: str
    auftragsart: str
    status: str = "offen"
    erledigt_am: Optional[str] = None

    def markiere_als_erledigt(self):
        self.status = "erledigt"
        self.erledigt_am = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
