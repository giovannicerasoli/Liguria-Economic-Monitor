
from pathlib import Path
import pandas as pd

# ============================================================
# LIGURIA ECONOMIC MONITOR
# Script 11 - Analisi del mercato del lavoro
# ============================================================

PROGETTO = Path(__file__).resolve().parent.parent
CARTELLA = PROGETTO / "data" / "processed"

FILE = CARTELLA / "mercato_lavoro_tassi_2019_2025.csv"

dati = pd.read_csv(
    FILE,
    sep=";",
    encoding="utf-8-sig"
)

indicatori = [
    "Tasso occupazione",
    "Tasso disoccupazione",
    "Tasso inattivita"
]

territori = [
    "Liguria",
    "Genova",
    "Imperia",
    "Savona",
    "La Spezia"
]

# ============================================================
# 1. CONFRONTO TERRITORIALE 2019-2025
# ============================================================

totale = dati[
    (dati["Sesso"] == "Totale")
    & dati["Anno"].isin([2019, 2025])
].copy()

confronto = totale.pivot(
    index="Territorio",
    columns="Anno",
    values=indicatori
)

# Differenze in punti percentuali
risultati = pd.DataFrame(index=confronto.index)

for indicatore in indicatori:

    risultati[f"{indicatore} 2019"] = confronto[
        (indicatore, 2019)
    ]

    risultati[f"{indicatore} 2025"] = confronto[
        (indicatore, 2025)
    ]

    risultati[f"{indicatore} diff. p.p."] = (
        confronto[(indicatore, 2025)]
        - confronto[(indicatore, 2019)]
    ).round(1)

risultati = risultati.reindex(territori)

print("\nCONFRONTO TERRITORIALE 2019-2025")
print(risultati.to_string())


# ============================================================
# 2. DIFFERENZE TRA UOMINI E DONNE NEL 2025
# ============================================================

dati_2025 = dati[
    (dati["Anno"] == 2025)
    & dati["Sesso"].isin(["Maschi", "Femmine"])
].copy()

genere = dati_2025.pivot(
    index="Territorio",
    columns="Sesso",
    values=indicatori
)

divari = pd.DataFrame(index=genere.index)

for indicatore in indicatori:

    divari[f"{indicatore} uomini"] = genere[
        (indicatore, "Maschi")
    ]

    divari[f"{indicatore} donne"] = genere[
        (indicatore, "Femmine")
    ]

    divari[f"{indicatore} divario F-M"] = (
        genere[(indicatore, "Femmine")]
        - genere[(indicatore, "Maschi")]
    ).round(1)

divari = divari.reindex(territori)

print("\nDIFFERENZE DI GENERE - 2025")
print(divari.to_string())


# ============================================================
# 3. SINTESI
# ============================================================

print("\nSINTESI REGIONALE 2019-2025")

for indicatore in indicatori:

    variazione = risultati.loc[
        "Liguria",
        f"{indicatore} diff. p.p."
    ]

    print(f"{indicatore}: {variazione:+.1f} punti percentuali")


print("\nDIVARIO DI OCCUPAZIONE TRA DONNE E UOMINI - 2025")

for territorio in territori:

    divario = divari.loc[
        territorio,
        "Tasso occupazione divario F-M"
    ]

    print(f"{territorio}: {divario:+.1f} punti percentuali")
