
"""Consolida i dati ISTAT mensili 2019-2025 e calcola la stagionalità turistica."""

from pathlib import Path
import pandas as pd


# ============================================================
# PERCORSI E CONFIGURAZIONE
# ============================================================

RADICE = Path(__file__).resolve().parents[1]
RAW = RADICE / "data" / "raw" / "turismo"
PROCESSED = RADICE / "data" / "processed"

PREFISSO = "Movimento dei clienti negli esercizi ricettivi per tipo di esercizio - mensili"
TERRITORI = ["Liguria", "Genova", "Imperia", "Savona", "La Spezia"]
TIPOLOGIE = {
    "ALL": "Totale esercizi ricettivi",
    "HOTELLIKE": "Esercizi alberghieri",
    "OTHER": "Esercizi extra-alberghieri",
}
INDICATORI = {"AR": "Arrivi", "NI": "Presenze"}
MESI = [
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre",
]
PERIODI_ATTESI = {
    f"{anno}-{mese:02d}"
    for anno in range(2019, 2026)
    for mese in range(1, 13)
}


# ============================================================
# LETTURA E CONTROLLI DEI CSV
# ============================================================

def leggi_territorio(territorio):
    percorso = RAW / f"{PREFISSO} {territorio}.csv"

    if not percorso.is_file():
        raise FileNotFoundError(f"CSV mensile non trovato: {percorso}")

    df = pd.read_csv(percorso, sep=";", encoding="utf-8-sig")

    richieste = {
        "FREQ", "Territorio", "DATA_TYPE", "ADJUSTMENT",
        "TYPE_ACCOMMODATION", "COUNTRY_RES_GUESTS",
        "TIME_PERIOD", "Osservazione",
    }

    if not richieste.issubset(df.columns):
        raise ValueError(
            f"Colonne mancanti in {percorso.name}: "
            f"{sorted(richieste - set(df.columns))}"
        )

    if len(df) != 504 or not df["Territorio"].eq(territorio).all():
        raise ValueError(f"Righe o territorio inattesi: {percorso.name}")

    if not df["FREQ"].eq("M").all() or not df["ADJUSTMENT"].eq("N").all():
        raise ValueError(f"Frequenza o correzione inattese: {percorso.name}")

    if not df["COUNTRY_RES_GUESTS"].eq("WORLD").all():
        raise ValueError(f"Il filtro di provenienza non è Mondo: {percorso.name}")

    if set(df["TYPE_ACCOMMODATION"]) != set(TIPOLOGIE):
        raise ValueError(f"Tipologie ricettive inattese: {percorso.name}")

    if set(df["DATA_TYPE"]) != set(INDICATORI):
        raise ValueError(f"Indicatori inattesi: {percorso.name}")

    if set(df["TIME_PERIOD"].astype(str)) != PERIODI_ATTESI:
        raise ValueError(f"Mesi mancanti o inattesi: {percorso.name}")

    df = df.rename(columns={
        "TIME_PERIOD": "Periodo",
        "TYPE_ACCOMMODATION": "Codice tipologia",
        "DATA_TYPE": "Codice indicatore",
        "Osservazione": "Valore",
    })

    df["Valore"] = pd.to_numeric(df["Valore"], errors="raise")

    if df["Valore"].isna().any() or (df["Valore"] < 0).any():
        raise ValueError(f"Valori mancanti o negativi: {percorso.name}")

    if (df["Valore"] % 1 != 0).any():
        raise ValueError(f"Valori non interi: {percorso.name}")

    df["Valore"] = df["Valore"].astype("int64")

    colonne = [
        "Periodo", "Territorio", "Codice tipologia", "Codice indicatore"
    ]

    if df.duplicated(colonne).any():
        raise ValueError(f"Osservazioni duplicate: {percorso.name}")

    print(f"Letto: {territorio} ({len(df)} righe)")

    return df[colonne + ["Valore"]]


def verifica_uguaglianza(prima, seconda, messaggio):
    if not prima.equals(seconda):
        differenze = (
            prima.compare(seconda)
            if prima.index.equals(seconda.index)
            else None
        )

        esempio = "" if differenze is None else f"\n{differenze.head()}"
        raise ValueError(messaggio + esempio)


def main():

    dati = pd.concat(
        [leggi_territorio(territorio) for territorio in TERRITORI],
        ignore_index=True,
    )

    dati["Anno"] = dati["Periodo"].str[:4].astype(int)
    dati["Mese"] = dati["Periodo"].str[5:7].astype(int)
    dati["Nome mese"] = dati["Mese"].apply(lambda m: MESI[m - 1])
    dati["Tipologia"] = dati["Codice tipologia"].map(TIPOLOGIE)

    # Arrivi e presenze diventano colonne distinte.

    chiave = [
        "Anno", "Mese", "Nome mese", "Periodo", "Territorio",
        "Codice tipologia", "Tipologia",
    ]

    dettaglio = (
        dati.pivot(
            index=chiave,
            columns="Codice indicatore",
            values="Valore",
        )
        .rename(columns=INDICATORI)
        .reset_index()
    )

    dettaglio.columns.name = None

    if (
        len(dettaglio) != 1260
        or dettaglio[["Arrivi", "Presenze"]].isna().any().any()
    ):
        raise ValueError(
            "Unione incompleta: attese 1.260 righe con due indicatori"
        )

    valori = ["Arrivi", "Presenze"]

    # Controllo: totale = alberghiero + extralberghiero.

    chiave_tipologie = ["Periodo", "Territorio"]

    totali = (
        dettaglio[dettaglio["Codice tipologia"] == "ALL"]
        .set_index(chiave_tipologie)[valori]
        .sort_index()
    )

    componenti = (
        dettaglio[dettaglio["Codice tipologia"] != "ALL"]
        .groupby(chiave_tipologie)[valori]
        .sum()
        .sort_index()
    )

    verifica_uguaglianza(
        totali,
        componenti,
        "Totale diverso da alberghiero + extralberghiero",
    )

    print("Controllo totale = alberghiero + extralberghiero: OK")

    # Controllo: somma delle province = Liguria.

    chiave_regione = ["Periodo", "Codice tipologia"]

    regione = (
        dettaglio[dettaglio["Territorio"] == "Liguria"]
        .set_index(chiave_regione)[valori]
        .sort_index()
    )

    province = (
        dettaglio[dettaglio["Territorio"] != "Liguria"]
        .groupby(chiave_regione)[valori]
        .sum()
        .sort_index()
    )

    verifica_uguaglianza(
        regione,
        province,
        "Le province non quadrano con la Liguria",
    )

    print("Controllo somma province = Liguria: OK")

    # Controllo: somma dei mesi = dataset annuale.

    percorso_annuale = (
        PROCESSED / "turismo_movimento_annuale_2019_2025.csv"
    )

    if not percorso_annuale.is_file():
        raise FileNotFoundError(
            f"Dataset annuale già elaborato non trovato: {percorso_annuale}"
        )

    annuale = pd.read_csv(
        percorso_annuale,
        encoding="utf-8-sig",
    )

    annuale = annuale[
        annuale["Codice tipologia"].isin(TIPOLOGIE)
    ]

    chiave_annuale = [
        "Anno", "Territorio", "Codice tipologia"
    ]

    annuale = (
        annuale.set_index(chiave_annuale)[valori]
        .sort_index()
    )

    somma_mesi = (
        dettaglio.groupby(chiave_annuale)[valori]
        .sum()
        .sort_index()
    )

    verifica_uguaglianza(
        somma_mesi,
        annuale,
        "I mesi non quadrano con i dati annuali",
    )

    print("Controllo somma dei 12 mesi = dati annuali: OK")

    # Permanenza media.

    dettaglio["Permanenza media"] = (
        dettaglio["Presenze"]
        / dettaglio["Arrivi"].replace(0, float("nan"))
    ).round(2)

    # Discontinuità statistica del 2025:
    # i totali e l'extralberghiero includono gli
    # alloggi in affitto non imprenditoriali.

    dettaglio["Discontinuita 2025"] = (
        dettaglio["Anno"].eq(2025)
        & dettaglio["Codice tipologia"].isin(["ALL", "OTHER"])
    )

    # Dataset sintetico per i grafici.
    # Si considera soltanto ALL, evitando doppi conteggi.

    stagionalita = dettaglio[
        dettaglio["Codice tipologia"] == "ALL"
    ].copy()

    stagionalita = stagionalita[[
        "Anno", "Mese", "Nome mese", "Periodo", "Territorio",
        "Arrivi", "Presenze", "Permanenza media",
        "Discontinuita 2025",
    ]]

    # Quota di ogni mese sul totale dell'anno.

    stagionalita["Quota arrivi annuali (%)"] = (
        100 * stagionalita["Arrivi"]
        / stagionalita.groupby(
            ["Anno", "Territorio"]
        )["Arrivi"].transform("sum")
    ).round(2)

    stagionalita["Quota presenze annuali (%)"] = (
        100 * stagionalita["Presenze"]
        / stagionalita.groupby(
            ["Anno", "Territorio"]
        )["Presenze"].transform("sum")
    ).round(2)

    if len(stagionalita) != 420:
        raise ValueError("Attese 420 osservazioni mensili totali")

    # Ordinamento dei territori e dei mesi.

    ordine = {
        territorio: i
        for i, territorio in enumerate(TERRITORI)
    }

    for tabella in [dettaglio, stagionalita]:

        tabella["_ordine"] = (
            tabella["Territorio"].map(ordine)
        )

        colonne_ordinamento = ["_ordine", "Anno", "Mese"]

        if "Codice tipologia" in tabella.columns:
            colonne_ordinamento.append("Codice tipologia")

        tabella.sort_values(
            colonne_ordinamento,
            inplace=True,
        )

        tabella.drop(columns="_ordine", inplace=True)
        tabella.reset_index(drop=True, inplace=True)

    # Salvataggio.

    PROCESSED.mkdir(parents=True, exist_ok=True)

    file_dettaglio = (
        PROCESSED / "turismo_movimento_mensile_2019_2025.csv"
    )

    file_stagionalita = (
        PROCESSED / "turismo_stagionalita_2019_2025.csv"
    )

    dettaglio.to_csv(
        file_dettaglio,
        index=False,
        encoding="utf-8-sig",
    )

    stagionalita.to_csv(
        file_stagionalita,
        index=False,
        encoding="utf-8-sig",
    )

    # Risultati di controllo.

    print("\n=== DATASET CREATI ===")
    print(
        f"Dettaglio mensile: {len(dettaglio)} righe "
        f"-> {file_dettaglio.name}"
    )
    print(
        f"Stagionalità: {len(stagionalita)} righe "
        f"-> {file_stagionalita.name}"
    )

    print("\n=== MESE DI MASSIMO AFFLUSSO: 2024 ===")

    anno_2024 = stagionalita[
        stagionalita["Anno"] == 2024
    ]

    picchi = anno_2024.loc[
        anno_2024.groupby("Territorio")["Presenze"].idxmax()
    ]

    for territorio in TERRITORI:

        riga = picchi[
            picchi["Territorio"] == territorio
        ].iloc[0]

        print(
            f"{territorio}: {riga['Nome mese']} - "
            f"{int(riga['Presenze']):,} presenze - "
            f"{riga['Quota presenze annuali (%)']:.2f}% dell'anno"
        )

    print("\nElaborazione completata.")


if __name__ == "__main__":
    main()
