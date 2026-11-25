import requests
import csv
import os
from datetime import datetime
from zoneinfo import ZoneInfo

URL = "https://opendata.technolution.nl/opendata/parkingdata/v1/dynamic/0967d16d-061b-4f44-838d-36cec4be68b9"

BESTAND = "parkeerdata.csv"

# Data ophalen
response = requests.get(
    URL,
    headers={"Accept": "application/json"},
    timeout=30
)
response.raise_for_status()

data = response.json()

# Waarden uitlezen
capaciteit = int(data["parkingCapacity"])
vrije_plaatsen = int(data["vacantSpaces"])
bezette_plaatsen = capaciteit - vrije_plaatsen
bronmeettijd = data.get("lastUpdated", "")

# Nederlandse tijd
nu = datetime.now(ZoneInfo("Europe/Amsterdam"))
opvraagtijd = nu.strftime("%Y-%m-%d %H:%M:%S")

# Controleren of CSV al bestaat
bestand_bestaat = os.path.exists(BESTAND)

# Nieuwe meting toevoegen
with open(BESTAND, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    if not bestand_bestaat:
        writer.writerow([
            "OpvraagtijdLokaal",
            "BronmeettijdUTC",
            "VrijePlaatsen",
            "Capaciteit",
            "BezettePlaatsen",
            "Meetstatus"
        ])

    writer.writerow([
        opvraagtijd,
        bronmeettijd,
        vrije_plaatsen,
        capaciteit,
        bezette_plaatsen,
        "OK"
    ])

print(
    f"Meting opgeslagen: {opvraagtijd} | "
    f"vrij={vrije_plaatsen} | bezet={bezette_plaatsen} | "
    f"capaciteit={capaciteit}"
)
