from pathlib import Path
from zipfile import ZipFile
import pandas as pd

# Individuiamo la cartella contenente i dati ISTAT
cartella_dati = Path(__file__).resolve().parent.parent / "data" / "raw"

# Cerchiamo tutti gli archivi ZIP presenti
archivi = sorted(cartella_dati.glob("*.zip"))

print(f"Archivi ISTAT trovati: {len(archivi)}")

# Esploriamo il contenuto di ogni archivio
for archivio in archivi:
    print(f"\nArchivio: {archivio.name}")

    with ZipFile(archivio) as zip_file:
        for nome_file in zip_file.namelist():
            print(f"  - {nome_file}")

# Leggiamo le prime righe del dataset di Imperia
primo_archivio = archivi[0]

with ZipFile(primo_archivio) as zip_file:
    nome_csv = zip_file.namelist()[0]

    with zip_file.open(nome_csv) as file:
        dati = pd.read_csv(
            file,
            sep=";",
            skiprows=1,
            encoding="utf-8-sig",
            dtype={"Codice comune": str},
            nrows=5
        )

# Esaminiamo la struttura del dataset
print("\nCOLONNE DEL DATASET:")
print(dati.columns.tolist())

print("\nPRIME 5 RIGHE:")
print(dati.to_string(index=False))
