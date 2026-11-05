from pathlib import Path
from zipfile import ZipFile
import pandas as pd

# Cartella contenente gli archivi ISTAT
cartella_dati = Path(__file__).resolve().parent.parent / "data" / "raw"

# Lista che conterrà i dataset provinciali
tabelle = []

# Leggiamo i quattro archivi
for archivio in sorted(cartella_dati.glob("*.zip")):

    # Ricaviamo il nome della provincia dal file
    provincia = archivio.stem.split("_", 4)[4].replace("_", " ")

    with ZipFile(archivio) as zip_file:
        nome_csv = zip_file.namelist()[0]

        with zip_file.open(nome_csv) as file:
            dati = pd.read_csv(
                file,
                sep=";",
                skiprows=1,
                encoding="utf-8-sig",
                dtype={"Codice comune": str}
            )

    # Aggiungiamo la provincia di appartenenza
    dati["Provincia"] = provincia

    # Inseriamo il dataset nella lista
    tabelle.append(dati)

# Uniamo i quattro dataset
liguria = pd.concat(tabelle, ignore_index=True)

# Verifichiamo il risultato
print("Righe complessive:", len(liguria))
print("Colonne complessive:", len(liguria.columns))

print("\nComuni per provincia:")
print(liguria.groupby("Provincia")["Codice comune"].nunique())

print("\nPrime 5 righe:")
print(liguria[["Provincia", "Comune", "Età", "Totale"]].head())

# Creiamo la cartella per i dati elaborati
cartella_output = Path(__file__).resolve().parent.parent / "data" / "processed"
cartella_output.mkdir(parents=True, exist_ok=True)

# Salviamo il dataset unificato
percorso_output = cartella_output / "liguria_popolazione_2025.csv"

liguria.to_csv(
    percorso_output,
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("\nDataset salvato correttamente!")
print("Percorso:", percorso_output)
