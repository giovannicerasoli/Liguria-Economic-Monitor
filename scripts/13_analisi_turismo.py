
from pathlib import Path
import pandas as pd

RADICE = Path(__file__).resolve().parents[1]
INPUT = RADICE / "data" / "processed" / "turismo_movimento_annuale_2019_2025.csv"
OUTPUT = RADICE / "data" / "processed" / "indicatori_turismo_2019_2025.csv"

dati = pd.read_csv(INPUT, encoding="utf-8-sig")

# Consideriamo solo il totale degli esercizi ricettivi.
# Le altre righe rappresentano categorie e sottocategorie.
totali = dati[dati["Codice tipologia"] == "ALL"].copy()

totali = totali[
    ["Anno", "Territorio", "Arrivi", "Presenze", "Permanenza media"]
].sort_values(["Territorio", "Anno"])

assert len(totali) == 35, "Numero di osservazioni inatteso"

# ----------------------------------------------------------
# 1. SERIE STORICA REGIONALE
# ----------------------------------------------------------

print("\n=== TURISMO IN LIGURIA: 2019-2025 ===")

liguria = totali[totali["Territorio"] == "Liguria"].copy()

print(liguria.to_string(index=False))

# ----------------------------------------------------------
# 2. VARIAZIONI 2019-2024
# ----------------------------------------------------------

print("\n=== VARIAZIONI 2019-2024 ===")

r2019 = liguria[liguria["Anno"] == 2019].iloc[0]
r2024 = liguria[liguria["Anno"] == 2024].iloc[0]

for indicatore in ["Arrivi", "Presenze"]:
    variazione = (
        (r2024[indicatore] / r2019[indicatore]) - 1
    ) * 100

    print(f"{indicatore}: {variazione:+.2f}%")

print(
    "\nNota: il 2025 presenta una discontinuita "
    "statistica negli alloggi in affitto e nei totali."
)

# ----------------------------------------------------------
# 3. CONFRONTO PROVINCIALE 2025
# ----------------------------------------------------------

print("\n=== PROVINCE LIGURI: 2025 ===")

province = totali[
    (totali["Anno"] == 2025)
    & (totali["Territorio"] != "Liguria")
].copy()

totale_presenze = liguria[
    liguria["Anno"] == 2025
]["Presenze"].iloc[0]

province["Quota presenze (%)"] = (
    province["Presenze"] / totale_presenze * 100
).round(2)

province = province.sort_values(
    "Presenze", ascending=False
)

print(province.to_string(index=False))

# ----------------------------------------------------------
# 4. STRUTTURE ALBERGHIERE ED EXTRALBERGHIERE
# ----------------------------------------------------------

print("\n=== TIPOLOGIE RICETTIVE: LIGURIA 2025 ===")

tipologie = dati[
    (dati["Anno"] == 2025)
    & (dati["Territorio"] == "Liguria")
    & (dati["Codice tipologia"].isin(["HOTELLIKE", "OTHER"]))
].copy()

tipologie = tipologie[
    ["Tipologia", "Arrivi", "Presenze", "Permanenza media"]
]

tipologie["Quota presenze (%)"] = (
    tipologie["Presenze"] / totale_presenze * 100
).round(2)

print(tipologie.to_string(index=False))

# ----------------------------------------------------------
# 5. SALVATAGGIO
# ----------------------------------------------------------

totali.to_csv(
    OUTPUT,
    index=False,
    encoding="utf-8-sig"
)

print("\nDataset indicatori salvato:")
print(OUTPUT)
print(f"Righe: {len(totali)}")
