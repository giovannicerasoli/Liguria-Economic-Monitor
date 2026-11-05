from pathlib import Path
import pandas as pd

# Percorso del progetto
progetto = Path(__file__).resolve().parent.parent

file = (
    progetto / "data" / "raw" / "serie_storiche"
    / "popolazione_eta_sesso_2019_2025.csv"
)

# Carichiamo i dati ISTAT
dati = pd.read_csv(
    file,
    sep=";",
    encoding="utf-8-sig"
)

# Selezioniamo la popolazione totale per sesso,
# escludendo le righe riepilogative delle età
popolazione = dati[
    (dati["Sesso"] == "Totale") &
    (dati["AGE"] != "TOTAL")
].copy()

# Convertiamo i codici ISTAT in età numeriche
# Y_GE100 rappresenta le persone di 100 anni e più
popolazione["Eta_numerica"] = (
    popolazione["AGE"]
    .replace({"Y_GE100": "Y100"})
    .str[1:]
    .astype(int)
)

# Creiamo le tre fasce demografiche
popolazione["Fascia"] = pd.cut(
    popolazione["Eta_numerica"],
    bins=[-1, 14, 64, float("inf")],
    labels=["0-14", "15-64", "65+"]
)

# Sommiamo i residenti per territorio, anno e fascia
struttura = (
    popolazione
    .groupby(
        ["Territorio", "TIME_PERIOD", "Fascia"],
        observed=True
    )["Osservazione"]
    .sum()
    .unstack("Fascia")
)

# Calcoliamo gli indicatori di invecchiamento
struttura["Anziani (%)"] = (
    struttura["65+"]
    / struttura[["0-14", "15-64", "65+"]].sum(axis=1)
    * 100
).round(2)

struttura["Indice di vecchiaia"] = (
    struttura["65+"]
    / struttura["0-14"]
    * 100
).round(2)

# Visualizziamo gli indicatori per tutta la Liguria
print("EVOLUZIONE INVECCHIAMENTO LIGURIA:")
print(
    struttura.loc["Liguria", [
        "0-14",
        "15-64",
        "65+",
        "Anziani (%)",
        "Indice di vecchiaia"
    ]].to_string()
)

# Confrontiamo le province nel 2019 e nel 2025
print("\nCONFRONTO PROVINCIALE 2019-2025:")

confronto = struttura.reset_index()

confronto = confronto[
    confronto["TIME_PERIOD"].isin([2019, 2025])
]

print(
    confronto[[
        "Territorio",
        "TIME_PERIOD",
        "Anziani (%)",
        "Indice di vecchiaia"
    ]].to_string(index=False)
)


# Prepariamo il dataset per la dashboard
indicatori_storici = (
    struttura
    .reset_index()
    .rename(columns={"TIME_PERIOD": "Anno"})
    .sort_values(["Territorio", "Anno"])
    .reset_index(drop=True)
)

# Definiamo il percorso di salvataggio
output = (
    progetto
    / "data"
    / "processed"
    / "evoluzione_invecchiamento_2019_2025.csv"
)

# Salviamo il dataset elaborato
indicatori_storici.to_csv(
    output,
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

# Verifichiamo il risultato
print("\nDATASET INVECCHIAMENTO SALVATO:")
print(output)

print("\nNumero osservazioni:", len(indicatori_storici))
print("Colonne:", indicatori_storici.columns.tolist())
