
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURAZIONE
# ============================================================

RADICE = Path(__file__).resolve().parents[1]
RAW = RADICE / "data" / "raw" / "turismo"
PROCESSED = RADICE / "data" / "processed"

PREFISSO = (
    "Movimento dei clienti negli esercizi ricettivi "
    "per tipo di esercizio - annuali"
)

TERRITORI = [
    "Liguria",
    "Genova",
    "Imperia",
    "Savona",
    "La Spezia"
]

PROVENIENZE = {
    "Italia": "IT",
    "Estero": "WRL_X_ITA"
}

INDICATORI = {
    "AR": "Arrivi",
    "NI": "Presenze"
}

CHIAVE = [
    "Anno",
    "Territorio",
    "Codice tipologia"
]


# ============================================================
# LETTURA DEI DIECI CSV
# ============================================================

tabelle = []

for territorio in TERRITORI:
    for provenienza, codice_istat in PROVENIENZE.items():

        percorso = RAW / (
            f"{PREFISSO} {territorio}_{provenienza}.csv"
        )

        if not percorso.exists():
            raise FileNotFoundError(
                f"File non trovato: {percorso}"
            )

        df = pd.read_csv(
            percorso,
            sep=";",
            encoding="utf-8-sig"
        )

        if len(df) != 154:
            raise ValueError(
                f"Numero di righe inatteso: {percorso.name}"
            )

        if not df["Territorio"].eq(territorio).all():
            raise ValueError(
                f"Territorio non corretto: {percorso.name}"
            )

        if not df["COUNTRY_RES_GUESTS"].eq(codice_istat).all():
            raise ValueError(
                f"Provenienza non corretta: {percorso.name}"
            )

        if not df["FREQ"].eq("A").all():
            raise ValueError("Frequenza non annuale")

        if not df["ADJUSTMENT"].eq("N").all():
            raise ValueError("Correzione statistica inattesa")

        if not df["DATA_TYPE"].isin(INDICATORI).all():
            raise ValueError("Indicatore inatteso")

        if set(df["TIME_PERIOD"]) != set(range(2019, 2026)):
            raise ValueError("Periodo diverso da 2019-2025")

        df = df.rename(columns={
            "TIME_PERIOD": "Anno",
            "TYPE_ACCOMMODATION": "Codice tipologia",
            "Tipologia di esercizio": "Tipologia",
            "DATA_TYPE": "Codice indicatore",
            "Osservazione": "Valore"
        })

        df["Provenienza"] = provenienza

        df = df[[
            "Anno",
            "Territorio",
            "Codice tipologia",
            "Tipologia",
            "Provenienza",
            "Codice indicatore",
            "Valore"
        ]]

        tabelle.append(df)

        print(
            f"Letto: {territorio} - {provenienza} "
            f"({len(df)} righe)"
        )


# ============================================================
# UNIONE E CONTROLLO
# ============================================================

dati = pd.concat(
    tabelle,
    ignore_index=True
)

dati["Anno"] = dati["Anno"].astype(int)
dati["Valore"] = pd.to_numeric(
    dati["Valore"],
    errors="raise"
).astype("int64")

if dati["Valore"].isna().any():
    raise ValueError("Valori mancanti")

if (dati["Valore"] < 0).any():
    raise ValueError("Valori negativi")

chiave_completa = [
    "Anno",
    "Territorio",
    "Codice tipologia",
    "Provenienza",
    "Codice indicatore"
]

if dati.duplicated(chiave_completa).any():
    raise ValueError("Osservazioni duplicate")

# Arrivi e presenze diventano colonne distinte.

dettaglio = dati.pivot(
    index=[
        "Anno",
        "Territorio",
        "Codice tipologia",
        "Tipologia",
        "Provenienza"
    ],
    columns="Codice indicatore",
    values="Valore"
).rename(
    columns=INDICATORI
).reset_index()

dettaglio.columns.name = None

if len(dettaglio) != 770:
    raise ValueError("Numero di righe inatteso")

if dettaglio[["Arrivi", "Presenze"]].isna().any().any():
    raise ValueError("Arrivi o presenze mancanti")


# ============================================================
# CONFRONTO CON I TOTALI MONDO GIÀ ELABORATI
# ============================================================

percorso_mondo = (
    PROCESSED
    / "turismo_movimento_annuale_2019_2025.csv"
)

mondo = pd.read_csv(
    percorso_mondo,
    encoding="utf-8-sig"
)

mondo = mondo[[
    "Anno",
    "Territorio",
    "Codice tipologia",
    "Tipologia",
    "Arrivi",
    "Presenze"
]].copy()

mondo["Provenienza"] = "Mondo"

valori = ["Arrivi", "Presenze"]

somma_provenienze = (
    dettaglio.groupby(CHIAVE)[valori]
    .sum()
    .sort_index()
)

totali_mondo = (
    mondo.set_index(CHIAVE)[valori]
    .sort_index()
)

if not somma_provenienze.equals(totali_mondo):
    raise ValueError(
        "Italia + Estero non coincide con Mondo"
    )

print(
    "\nControllo Italia + Estero = Mondo: OK"
)

# Controllo delle quattro province per provenienza.

province = (
    dettaglio[dettaglio["Territorio"] != "Liguria"]
    .groupby([
        "Anno",
        "Provenienza",
        "Codice tipologia"
    ])[valori]
    .sum()
    .sort_index()
)

regione = (
    dettaglio[dettaglio["Territorio"] == "Liguria"]
    .set_index([
        "Anno",
        "Provenienza",
        "Codice tipologia"
    ])[valori]
    .sort_index()
)

if not province.equals(regione):
    raise ValueError(
        "Somma delle province diversa dalla Liguria"
    )

print("Controllo province = Liguria: OK")


# ============================================================
# DATASET COMPLETO PER TIPOLOGIA E PROVENIENZA
# ============================================================

dettaglio = pd.concat(
    [dettaglio, mondo],
    ignore_index=True
)

dettaglio["Permanenza media"] = (
    dettaglio["Presenze"]
    / dettaglio["Arrivi"].replace(0, float("nan"))
).round(2)

dettaglio["Discontinuita 2025"] = (
    dettaglio["Anno"].eq(2025)
    & dettaglio["Codice tipologia"].isin([
        "ALL",
        "OTHER",
        "DWELLINGS"
    ])
)

dettaglio = dettaglio.sort_values([
    "Territorio",
    "Anno",
    "Codice tipologia",
    "Provenienza"
]).reset_index(drop=True)

output_dettaglio = (
    PROCESSED
    / "turismo_provenienza_dettaglio_2019_2025.csv"
)

dettaglio.to_csv(
    output_dettaglio,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# DATASET SINTETICO: UNA RIGA PER ANNO E TERRITORIO
# ============================================================

totali = dettaglio[
    dettaglio["Codice tipologia"] == "ALL"
].copy()

indice = ["Anno", "Territorio"]

arrivi = totali.pivot(
    index=indice,
    columns="Provenienza",
    values="Arrivi"
)

presenze = totali.pivot(
    index=indice,
    columns="Provenienza",
    values="Presenze"
)

if not arrivi.index.equals(presenze.index):
    raise ValueError("Indici non coerenti")

riepilogo = pd.DataFrame({
    "Anno": arrivi.index.get_level_values("Anno"),
    "Territorio": arrivi.index.get_level_values("Territorio"),
    "Arrivi italiani": arrivi["Italia"].to_numpy(),
    "Arrivi esteri": arrivi["Estero"].to_numpy(),
    "Arrivi totali": arrivi["Mondo"].to_numpy(),
    "Presenze italiane": presenze["Italia"].to_numpy(),
    "Presenze estere": presenze["Estero"].to_numpy(),
    "Presenze totali": presenze["Mondo"].to_numpy()
})

riepilogo["Quota arrivi esteri (%)"] = (
    riepilogo["Arrivi esteri"]
    / riepilogo["Arrivi totali"] * 100
).round(2)

riepilogo["Quota presenze estere (%)"] = (
    riepilogo["Presenze estere"]
    / riepilogo["Presenze totali"] * 100
).round(2)

riepilogo["Quota arrivi italiani (%)"] = (
    riepilogo["Arrivi italiani"]
    / riepilogo["Arrivi totali"] * 100
).round(2)

riepilogo["Quota presenze italiane (%)"] = (
    riepilogo["Presenze italiane"]
    / riepilogo["Presenze totali"] * 100
).round(2)

riepilogo["Permanenza media italiani"] = (
    riepilogo["Presenze italiane"]
    / riepilogo["Arrivi italiani"].replace(0, float("nan"))
).round(2)

riepilogo["Permanenza media esteri"] = (
    riepilogo["Presenze estere"]
    / riepilogo["Arrivi esteri"].replace(0, float("nan"))
).round(2)

riepilogo["Discontinuita 2025"] = (
    riepilogo["Anno"] == 2025
)

ordine_territori = {
    nome: i for i, nome in enumerate(TERRITORI)
}

riepilogo["_ordine"] = (
    riepilogo["Territorio"].map(ordine_territori)
)

riepilogo = (
    riepilogo.sort_values(["_ordine", "Anno"])
    .drop(columns="_ordine")
    .reset_index(drop=True)
)

if len(riepilogo) != 35:
    raise ValueError("Numero di osservazioni inatteso")

output_riepilogo = (
    PROCESSED
    / "turismo_provenienza_2019_2025.csv"
)

riepilogo.to_csv(
    output_riepilogo,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# RISULTATI
# ============================================================

print("\n=== DATASET CREATI ===")
print(
    f"Riepilogo: {len(riepilogo)} righe"
)
print(
    f"Dettaglio: {len(dettaglio)} righe"
)

print("\n=== LIGURIA 2024 ===")

liguria_2024 = riepilogo[
    (riepilogo["Territorio"] == "Liguria")
    & (riepilogo["Anno"] == 2024)
]

print(
    liguria_2024[[
        "Arrivi italiani",
        "Arrivi esteri",
        "Quota arrivi esteri (%)",
        "Presenze italiane",
        "Presenze estere",
        "Quota presenze estere (%)"
    ]].to_string(index=False)
)

print("\nElaborazione completata.")
