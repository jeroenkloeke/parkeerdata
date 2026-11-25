import requests
import csv
import os
from datetime import datetime
from zoneinfo import ZoneInfo

URL = "https://opendata.technolution.nl/opendata/parkingdata/v1/dynamic/0967d16d-061b-4f44-838d-36cec4be68b9"
BESTAND = "parkeerdata.csv"


def zoek_waarde(data, sleutel):
    """
    Doorzoekt geneste dictionaries en lijsten
    naar een bepaalde sleutel.
    """
    if isinstance(data, dict):
        if sleutel in data:
            return data[sleutel]

        for waarde in data.values():
            resultaat = zoek_waarde(waarde, sleutel)
            if resultaat is not None:
                return resultaat

    elif isinstance(data, list):
        for onderdeel in data:
            resultaat = zoek_waarde(onderdeel, sleutel)
            if resultaat is not None:
                return resultaat

    return None


# Data ophalen
response = requests.get(
    URL,
    headers={
        "Accept": "application/json",
        "User-Agent": "parkeerdata-github-action/1.0"
    },
    timeout=30
)

response.raise_for_status()
data = response.json()

# Handig voor foutopsporing in GitHub Actions
print("Ontvangen hoofdstructuur:", type(data).__name__)

if isinstance(data, dict):
    print("Beschikbare hoofdsleutels:", list(data.keys()))

# Waarden zoeken, ook als deze dieper in de JSON staan
capaciteit = zoek_waarde(data, "parkingCapacity")
vrije_plaatsen = zoek_waarde(data, "vacantSpaces")
bronmeettijd = zoek_waarde(data, "lastUpdated")

# Duidelijke foutmelding wanneer de velden niet zijn aangetroffen
if capaciteit is None or vrije_plaatsen is None:
    print("Ontvangen JSON:")
    print(data)

    raise ValueError(
        "parkingCapacity en/of vacantSpaces niet gevonden "
        "in het antwoord van de databron."
    )

capaciteit = int(capaciteit)
vrije_plaatsen = int(vrije_plaatsen)
bezette_plaatsen = capaciteit - vrije_plaatsen

# Lokale Nederlandse opvraagtijd
nu = datetime.now(ZoneInfo("Europe/Amsterdam"))
opvraagtijd = nu.strftime("%Y-%m-%d %H:%M:%S")

bestand_bestaat = os.path.exists(BESTAND)
bestand_is_leeg = bestand_bestaat and os.path.getsize(BESTAND) == 0

# Nieuwe meting toevoegen
with open(BESTAND, "a", newline="", encoding="utf-8") as bestand:
    writer = csv.writer(bestand)

    if not bestand_bestaat or bestand_is_leeg:
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
        bronmeettijd or "",
        vrije_plaatsen,
        capaciteit,
        bezette_plaatsen,
        "OK"
    ])

print(
    f"Meting opgeslagen: {opvraagtijd} | "
    f"vrij={vrije_plaatsen} | "
    f"bezet={bezette_plaatsen} | "
    f"capaciteit={capaciteit}"
)
