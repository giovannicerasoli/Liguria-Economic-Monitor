
from pathlib import Path
import pandas as pd

# Percorso del progetto
progetto = Path(__file__).resolve().parent.parent

file = (
    progetto
    / "data"
    / "processed"
    / "imprese_serie_storica_2019_2025.csv"
)

# Carichiamo la serie storica
dati = pd.read_csv(
    file,
    sep=";",
    encoding="utf-8-sig"
)

# Selezioniamo le quattro province
province = dati[
    dati["Territorio"] != "Liguria"
].copy()

# Organizziamo le imprese attive per provincia e anno
attive = province.pivot(
    index="Territorio",
    columns="Anno",
    values="Attive"
)

# Confrontiamo il 2019 con il 2025
confronto = pd.DataFrame({
    "Attive 2019": attive[2019],
    "Attive 2025": attive[2025]
})

# Variazione assoluta
confronto["Variazione assoluta"] = (
    confronto["Attive 2025"]
    - confronto["Attive 2019"]
)

# Variazione percentuale
confronto["Variazione (%)"] = (
    confronto["Variazione assoluta"]
    / confronto["Attive 2019"]
    * 100
).round(2)

# Ordiniamo dalla variazione peggiore alla migliore
confronto = confronto.sort_values("Variazione (%)")

print("EVOLUZIONE IMPRESE ATTIVE PER PROVINCIA:")
print(confronto.to_string())

# Controllo della coerenza territoriale
totale_province = (
    province.groupby("Anno")["Attive"].sum()
)

totale_regione = (
    dati[dati["Territorio"] == "Liguria"]
    .set_index("Anno")["Attive"]
)

controllo = totale_province == totale_regione

print("\nCONTROLLO COERENZA:")
print(controllo)

# Individuiamo le province con le variazioni estreme
print("\nPROVINCIA CON LA MAGGIORE DIMINUZIONE:")
print(confronto["Variazione (%)"].idxmin())

print("\nPROVINCIA CON LA VARIAZIONE MIGLIORE:")
print(confronto["Variazione (%)"].idxmax())


# ============================================================
# ANALISI PRELIMINARE DEI SETTORI ECONOMICI
# ============================================================

# Carichiamo il dataset dettagliato
file_dettaglio = (
    progetto
    / "data"
    / "processed"
    / "imprese_dettaglio_2019_2025.csv"
)

dettaglio = pd.read_csv(
    file_dettaglio,
    sep=";",
    encoding="utf-8-sig"
)

# Selezioniamo il 2025
dati_2025 = dettaglio[
    dettaglio["Anno"] == 2025
].copy()

# Raggruppiamo le imprese per settore
settori = (
    dati_2025
    .groupby("Settore")[["Registrate", "Attive"]]
    .sum()
    .sort_values("Attive", ascending=False)
)

print("\nIMPRESE PER SETTORE ECONOMICO - 2025:")
print(settori.to_string())

print("\nNUMERO DI SETTORI:")
print(len(settori))

# Controlliamo i totali settoriali per tutti gli anni
totali_settori = dettaglio.groupby("Anno")["Attive"].sum()

totali_regionali = (
    dati[dati["Territorio"] == "Liguria"]
    .set_index("Anno")["Attive"]
)

controllo_settori = totali_settori == totali_regionali

print("\nCONTROLLO TOTALI SETTORIALI:")
print(controllo_settori)



# ============================================================
# EVOLUZIONE SETTORIALE 2019-2025
# ============================================================

# Identifichiamo i settori attraverso il codice ATECO
# (A, B, C, ..., X)
dettaglio["Codice settore"] = (
    dettaglio["Settore"].str.extract(r"^\s*([A-Z])\s")
)

if dettaglio["Codice settore"].isna().any():
    raise ValueError("Alcuni settori non hanno un codice valido")

# Selezioniamo gli anni iniziale e finale
estremi = dettaglio[
    dettaglio["Anno"].isin([2019, 2025])
]

# Numero di imprese attive per settore e anno
confronto_settori = (
    estremi
    .groupby(["Codice settore", "Anno"])["Attive"]
    .sum()
    .unstack("Anno", fill_value=0)
    .rename(columns={
        2019: "Attive 2019",
        2025: "Attive 2025"
    })
)

# Aggiungiamo i nomi dei settori
nomi = (
    dettaglio[dettaglio["Anno"] == 2025]
    .drop_duplicates("Codice settore")
    .set_index("Codice settore")["Settore"]
)

confronto_settori.insert(
    0, "Settore", nomi.reindex(confronto_settori.index)
)

# Calcoliamo le variazioni
confronto_settori["Variazione assoluta"] = (
    confronto_settori["Attive 2025"]
    - confronto_settori["Attive 2019"]
)

confronto_settori["Variazione (%)"] = (
    confronto_settori["Variazione assoluta"]
    / confronto_settori["Attive 2019"].replace(0, float("nan"))
    * 100
).round(2)

# Separiamo le imprese non classificate
confronto_classificati = confronto_settori.drop(
    index="X", errors="ignore"
)

# Ordiniamo dalla perdita maggiore alla crescita maggiore
confronto_classificati = confronto_classificati.sort_values(
    "Variazione assoluta"
)

pd.set_option("display.max_colwidth", None)

print("\nEVOLUZIONE SETTORIALE 2019-2025:")
print(confronto_classificati.to_string())



# ============================================================
# EVOLUZIONE SETTORIALE PER PROVINCIA 2019-2025
# ============================================================

# Escludiamo le imprese non classificate
dati_classificati = dettaglio[
    (dettaglio["Codice settore"] != "X")
    & (dettaglio["Anno"].isin([2019, 2025]))
].copy()

# Numero di imprese attive per provincia, settore e anno
settori_province = (
    dati_classificati
    .groupby(["Provincia", "Codice settore", "Anno"])["Attive"]
    .sum()
    .unstack("Anno", fill_value=0)
)

# Calcoliamo la variazione assoluta
settori_province["Variazione"] = (
    settori_province[2025] - settori_province[2019]
)

# Aggiungiamo il nome del settore
settori_province["Settore"] = (
    settori_province.index
    .get_level_values("Codice settore")
    .map(nomi)
)

# Stampiamo le principali variazioni per ogni provincia
for provincia in ["Genova", "Imperia", "Savona", "La Spezia"]:

    tabella = (
        settori_province
        .loc[provincia]
        .sort_values("Variazione")
    )

    print(f"\n========== {provincia.upper()} ==========")

    print("\n5 SETTORI CON MAGGIORE DIMINUZIONE:")
    print(
        tabella[["Settore", 2019, 2025, "Variazione"]]
        .head(5)
        .to_string(index=False)
    )

    print("\n5 SETTORI CON MAGGIORE AUMENTO:")
    print(
        tabella[["Settore", 2019, 2025, "Variazione"]]
        .tail(5)
        .sort_values("Variazione", ascending=False)
        .to_string(index=False)
    )
