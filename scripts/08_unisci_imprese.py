
from pathlib import Path
import pandas as pd

# Percorsi del progetto
progetto = Path(__file__).resolve().parent.parent
cartella_raw = progetto / "data" / "raw" / "imprese"
cartella_output = progetto / "data" / "processed"

# Variabili quantitative
misure = [
    "Registrate",
    "Attive",
    "Iscrizioni",
    "Cessazioni non d ufficio",
    "Saldo"
]

# Variabili che identificano ogni osservazione
chiave = [
    "Anno",
    "Trimestre",
    "Settore",
    "Divisione",
    "Regione",
    "Provincia",
    "Forma giuridica",
    "Tipo ricerca"
]

# Nomi delle province
province = {
    "GENOVA": "Genova",
    "IMPERIA": "Imperia",
    "LA SPEZIA": "La Spezia",
    "SAVONA": "Savona"
}

# Carichiamo i sette archivi
archivi = []

for anno in range(2019, 2026):

    percorso = cartella_raw / f"movimprese_{anno}.csv"

    dati = pd.read_csv(
        percorso,
        sep=";",
        encoding="utf-8-sig"
    )

    # Controlli di coerenza
    if not (dati["Anno"] == anno).all():
        raise ValueError(f"Anno errato nel file {anno}")

    if not (dati["Trimestre"] == 0).all():
        raise ValueError(f"Periodo errato nel file {anno}")

    if set(dati["Provincia"]) != set(province):
        raise ValueError(f"Province inattese nel file {anno}")

    if dati.duplicated(subset=chiave).any():
        raise ValueError(f"Duplicati nel file {anno}")

    if dati[misure].isna().any().any():
        raise ValueError(f"Valori mancanti nel file {anno}")

    if not (
        dati["Saldo"]
        == dati["Iscrizioni"] - dati["Cessazioni non d ufficio"]
    ).all():
        raise ValueError(f"Saldi non coerenti nel file {anno}")

    archivi.append(dati)

    print(f"{anno}: {len(dati)} righe verificate")


# Unifichiamo tutti i dati
dettaglio = pd.concat(
    archivi,
    ignore_index=True
)

# Uniformiamo i nomi delle province
dettaglio["Provincia"] = dettaglio["Provincia"].map(province)

dettaglio = dettaglio.sort_values(
    ["Anno", "Provincia", "Settore", "Divisione", "Forma giuridica"]
)

# Salviamo il dataset completo
dettaglio.to_csv(
    cartella_output / "imprese_dettaglio_2019_2025.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)


# Aggregazione provinciale
provinciali = (
    dettaglio
    .groupby(["Anno", "Provincia"], as_index=False)[misure]
    .sum()
)

# Aggregazione regionale
regionali = (
    provinciali
    .groupby("Anno", as_index=False)[misure]
    .sum()
)

regionali["Provincia"] = "Liguria"

# Creiamo un'unica serie storica
serie = pd.concat(
    [provinciali, regionali],
    ignore_index=True
)

serie = (
    serie
    .rename(columns={"Provincia": "Territorio"})
    .sort_values(["Anno", "Territorio"])
)

# Salviamo la serie per la dashboard
serie.to_csv(
    cartella_output / "imprese_serie_storica_2019_2025.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("\nRighe nel dettaglio:", len(dettaglio))
print("Righe nella serie storica:", len(serie))

print("\nSERIE STORICA REGIONALE:")
print(
    serie.loc[
        serie["Territorio"] == "Liguria",
        ["Anno", "Registrate", "Attive", "Saldo"]
    ].to_string(index=False)
)
