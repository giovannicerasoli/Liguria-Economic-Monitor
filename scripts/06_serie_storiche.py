from pathlib import Path
import pandas as pd

# Percorso del progetto
progetto = Path(__file__).resolve().parent.parent

# Carichiamo la serie storica ISTAT
file = (
    progetto
    / "data"
    / "raw"
    / "serie_storiche"
    / "popolazione_province_2019_2025.csv"
)

dati = pd.read_csv(
    file,
    sep=";",
    encoding="utf-8-sig"
)

# Selezioniamo la popolazione totale, senza
# sommare nuovamente maschi e femmine
totali = dati[dati["Sesso"] == "Totale"].copy()

# Organizziamo le osservazioni in una tabella
serie = totali.pivot(
    index="TIME_PERIOD",
    columns="Territorio",
    values="Osservazione"
).sort_index()

print("EVOLUZIONE DELLA POPOLAZIONE 2019-2025:")
print(serie.to_string())

# Calcoliamo la variazione tra 2019 e 2025
confronto = pd.DataFrame({
    "2019": serie.loc[2019],
    "2025": serie.loc[2025]
})

# Variazione assoluta
confronto["Variazione assoluta"] = (
    confronto["2025"] - confronto["2019"]
)

# Variazione percentuale
confronto["Variazione (%)"] = (
    confronto["Variazione assoluta"]
    / confronto["2019"]
    * 100
).round(2)

print("\nVARIAZIONE DEMOGRAFICA 2019-2025:")
print(confronto.to_string())

# Verifichiamo la corrispondenza tra
# il totale regionale e le quattro province
province = ["Genova", "Imperia", "La Spezia", "Savona"]

controllo = (
    serie[province].sum(axis=1)
    == serie["Liguria"]
)

print("\nCONTROLLO COERENZA PER ANNO:")
print(controllo)


# Calcoliamo le variazioni assolute anno per anno
variazioni_annuali = serie.diff().iloc[1:].astype(int)

print("\nVARIAZIONI ASSOLUTE ANNUALI:")
print(variazioni_annuali.to_string())

# Calcoliamo le variazioni percentuali annuali
variazioni_percentuali = (
    serie.pct_change(fill_method=None)
    .iloc[1:]
    .mul(100)
    .round(2)
)

print("\nVARIAZIONI PERCENTUALI ANNUALI:")
print(variazioni_percentuali.to_string())

# Individuiamo l'anno con la popolazione minima
anno_minimo = serie["Liguria"].idxmin()

print("\nANNO CON POPOLAZIONE MINIMA IN LIGURIA:")
print(anno_minimo)
print("Residenti:", serie.loc[anno_minimo, "Liguria"])


# Trasformiamo la tabella in formato lungo
storico = (
    serie.rename_axis("Anno")
    .reset_index()
    .melt(
        id_vars="Anno",
        var_name="Territorio",
        value_name="Residenti"
    )
    .sort_values(["Territorio", "Anno"])
    .reset_index(drop=True)
)

# Calcoliamo la variazione annuale per ogni territorio
storico["Variazione annua"] = (
    storico.groupby("Territorio")["Residenti"]
    .diff()
    .astype("Int64")
)

# Calcoliamo la variazione percentuale
storico["Variazione annua (%)"] = (
    storico.groupby("Territorio")["Residenti"]
    .pct_change(fill_method=None)
    .mul(100)
    .round(2)
)

# Salviamo i risultati
output = (
    progetto
    / "data"
    / "processed"
    / "serie_storica_popolazione_2019_2025.csv"
)

storico.to_csv(
    output,
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("\nDATASET STORICO SALVATO:")
print(output)
print("Osservazioni:", len(storico))

print("\nDATI REGIONALI:")
print(
    storico[storico["Territorio"] == "Liguria"]
    .to_string(index=False)
)
