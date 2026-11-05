from pathlib import Path
import pandas as pd

# Carichiamo il dataset demografico
cartella_progetto = Path(__file__).resolve().parent.parent

percorso_file = (
    cartella_progetto
    / "data"
    / "processed"
    / "liguria_popolazione_2025.csv"
)

liguria = pd.read_csv(
    percorso_file,
    sep=";",
    encoding="utf-8-sig",
    dtype={"Codice comune": str}
)

# Escludiamo le righe con i totali comunali (Età = 999)
dati_eta = liguria[liguria["Età"] != 999].copy()

# Suddividiamo la popolazione in tre fasce di età
dati_eta["Fascia età"] = pd.cut(
    dati_eta["Età"],
    bins=[-1, 14, 64, float("inf")],
    labels=["0-14", "15-64", "65+"]
)

# Calcoliamo i residenti per fascia e provincia
struttura_eta = (
    dati_eta
    .groupby(["Provincia", "Fascia età"], observed=True)["Totale"]
    .sum()
    .unstack()
)

print("POPOLAZIONE PER FASCIA DI ETÀ:")
print(struttura_eta)

# Calcoliamo i totali regionali
print("\nTOTALE LIGURIA PER FASCIA:")
print(struttura_eta.sum())

# Controlliamo la coerenza con i totali ISTAT
totali_istat = (
    liguria[liguria["Età"] == 999]
    .groupby("Provincia")["Totale"]
    .sum()
)

controllo = struttura_eta.sum(axis=1) == totali_istat

print("\nCONTROLLO COERENZA:")
print(controllo)


# Calcoliamo gli indicatori demografici provinciali
indicatori = pd.DataFrame(index=struttura_eta.index)

# Percentuale di residenti con almeno 65 anni
indicatori["Anziani (%)"] = (
    struttura_eta["65+"]
    / struttura_eta.sum(axis=1)
    * 100
)

# Indice di vecchiaia
indicatori["Indice di vecchiaia"] = (
    struttura_eta["65+"]
    / struttura_eta["0-14"]
    * 100
)

# Indice di dipendenza strutturale
indicatori["Indice di dipendenza"] = (
    (struttura_eta["0-14"] + struttura_eta["65+"])
    / struttura_eta["15-64"]
    * 100
)

# Visualizziamo i risultati arrotondati
print("\nINDICATORI DEMOGRAFICI PROVINCIALI:")
print(indicatori.round(2).to_string())

# Calcoliamo gli stessi indicatori per tutta la Liguria
regione = struttura_eta.sum()

print("\nINDICATORI REGIONALI:")
print("Anziani (%):", round(
    regione["65+"] / regione.sum() * 100, 2
))

print("Indice di vecchiaia:", round(
    regione["65+"] / regione["0-14"] * 100, 2
))

print("Indice di dipendenza:", round(
    (regione["0-14"] + regione["65+"])
    / regione["15-64"] * 100, 2
))


# Aggiungiamo gli indicatori regionali alla tabella
indicatori.loc["Liguria"] = [
    regione["65+"] / regione.sum() * 100,
    regione["65+"] / regione["0-14"] * 100,
    (regione["0-14"] + regione["65+"])
    / regione["15-64"] * 100
]

# Percorso del file di output
percorso_output = (
    cartella_progetto
    / "data"
    / "processed"
    / "indicatori_demografici_2025.csv"
)

# Salviamo la tabella degli indicatori
indicatori.round(2).to_csv(
    percorso_output,
    sep=";",
    encoding="utf-8-sig",
    index_label="Territorio"
)

print("\nIndicatori demografici salvati correttamente!")
print("Percorso:", percorso_output)
