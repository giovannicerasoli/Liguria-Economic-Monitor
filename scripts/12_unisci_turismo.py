
"""Unisce e verifica i CSV ISTAT annuali sul movimento turistico ligure."""

from pathlib import Path
import pandas as pd

RADICE = Path(__file__).resolve().parents[1]
CARTELLA_ORIGINE = RADICE / "data" / "raw" / "turismo"
CARTELLA_DESTINAZIONE = RADICE / "data" / "processed"
NOME_TAVOLA = "Movimento dei clienti negli esercizi ricettivi per tipo di esercizio - annuali"
TERRITORI = ["Liguria", "Genova", "Imperia", "Savona", "La Spezia"]
INDICATORI = {"AR": "Arrivi", "NI": "Presenze"}


def controlla_quadratura(tabella, categoria_totale, categorie_componenti):
    colonne = ["Arrivi", "Presenze"]
    chiave = ["Anno", "Territorio"]
    totale = (tabella[tabella["Codice tipologia"] == categoria_totale]
              .set_index(chiave)[colonne].sort_index())
    componenti = (tabella[tabella["Codice tipologia"].isin(categorie_componenti)]
                  .groupby(chiave)[colonne].sum().sort_index())
    if not totale.equals(componenti):
        raise ValueError(f"Le categorie non quadrano per: {categoria_totale}")


def main():
    tabelle = []

    for territorio in TERRITORI:
        percorso = CARTELLA_ORIGINE / f"{NOME_TAVOLA} {territorio}.csv"
        if not percorso.is_file():
            raise FileNotFoundError(f"File non trovato: {percorso}")

        dati = pd.read_csv(percorso, sep=";", encoding="utf-8-sig")
        colonne_richieste = [
            "FREQ", "REF_AREA", "Territorio", "DATA_TYPE", "Indicatore",
            "ADJUSTMENT", "TYPE_ACCOMMODATION", "Tipologia di esercizio",
            "COUNTRY_RES_GUESTS", "TIME_PERIOD", "Osservazione"
        ]
        mancanti = set(colonne_richieste) - set(dati.columns)
        if mancanti:
            raise ValueError(f"Colonne assenti in {percorso.name}: {sorted(mancanti)}")

        if len(dati) != 154 or not dati["Territorio"].eq(territorio).all():
            raise ValueError(f"Righe o territorio inattesi in: {percorso.name}")
        if not dati["FREQ"].eq("A").all() or not dati["ADJUSTMENT"].eq("N").all():
            raise ValueError(f"Frequenza o correzione inattese in: {percorso.name}")
        if not dati["COUNTRY_RES_GUESTS"].eq("WORLD").all():
            raise ValueError(f"Il filtro di residenza non è 'Mondo': {percorso.name}")
        if not dati["DATA_TYPE"].isin(INDICATORI).all():
            raise ValueError(f"Indicatori inattesi in: {percorso.name}")

        selezione = dati[[
            "TIME_PERIOD", "Territorio", "REF_AREA", "TYPE_ACCOMMODATION",
            "Tipologia di esercizio", "DATA_TYPE", "Osservazione"
        ]].rename(columns={
            "TIME_PERIOD": "Anno",
            "REF_AREA": "Codice territorio",
            "TYPE_ACCOMMODATION": "Codice tipologia",
            "Tipologia di esercizio": "Tipologia",
            "DATA_TYPE": "Codice indicatore",
            "Osservazione": "Valore"
        })
        tabelle.append(selezione)
        print(f"Letto: {territorio} ({len(dati)} righe)")

    dati = pd.concat(tabelle, ignore_index=True)
    dati["Anno"] = pd.to_numeric(dati["Anno"], errors="raise").astype(int)
    dati["Valore"] = pd.to_numeric(dati["Valore"], errors="raise").astype("int64")

    if set(dati["Anno"]) != set(range(2019, 2026)):
        raise ValueError("Il periodo non coincide con il 2019-2025")
    if dati["Valore"].isna().any() or (dati["Valore"] < 0).any():
        raise ValueError("Sono presenti valori mancanti o negativi")

    chiave = ["Anno", "Territorio", "Codice territorio", "Codice tipologia", "Tipologia"]
    if dati.duplicated(chiave + ["Codice indicatore"]).any():
        raise ValueError("Sono presenti osservazioni duplicate")

    tabella = (dati.pivot(index=chiave, columns="Codice indicatore", values="Valore")
               .rename(columns=INDICATORI).reset_index())
    tabella.columns.name = None
    if len(tabella) != 385 or tabella[["Arrivi", "Presenze"]].isna().any().any():
        raise ValueError("Righe o indicatori mancanti dopo l'unione")

    # Controllo: le quattro province devono sommare esattamente alla Liguria.
    colonne_valori = ["Arrivi", "Presenze"]
    chiave_regionale = ["Anno", "Codice tipologia"]
    regione = (tabella[tabella["Territorio"] == "Liguria"]
               .set_index(chiave_regionale)[colonne_valori].sort_index())
    province = (tabella[tabella["Territorio"] != "Liguria"]
                .groupby(chiave_regionale)[colonne_valori].sum().sort_index())
    if not regione.equals(province):
        raise ValueError("La somma delle province non coincide con la Liguria")

    # Controllo delle categorie gerarchiche: non vanno sommate tutte le 11 righe.
    controlla_quadratura(tabella, "ALL", ["HOTELLIKE", "OTHER"])
    controlla_quadratura(tabella, "HOTELLIKE", [
        "4_5_5P_STARSHOTELS", "3_STARSHOTELS_RES", "1_2_STARSHOTELS"
    ])
    controlla_quadratura(tabella, "OTHER", [
        "CAMP_VILL", "DWELLINGS", "FARMHOUSES", "BNB", "OTHERACC"
    ])

    tabella["Permanenza media"] = (
        tabella["Presenze"] / tabella["Arrivi"].replace(0, float("nan"))
    ).round(2)

    # Dal 2025 cambiano le definizioni degli alloggi in affitto e dei totali
    # che li comprendono: non usare questi dati per confronti diretti col 2024.
    tabella["Discontinuita 2025"] = (
        tabella["Anno"].eq(2025)
        & tabella["Codice tipologia"].isin(["ALL", "OTHER", "DWELLINGS"])
    )

    ordine = {nome: i for i, nome in enumerate(TERRITORI)}
    tabella["_ordine"] = tabella["Territorio"].map(ordine)
    tabella = (tabella.sort_values(["_ordine", "Anno", "Codice tipologia"])
               .drop(columns="_ordine").reset_index(drop=True))

    CARTELLA_DESTINAZIONE.mkdir(parents=True, exist_ok=True)
    destinazione = CARTELLA_DESTINAZIONE / "turismo_movimento_annuale_2019_2025.csv"
    tabella.to_csv(destinazione, index=False, encoding="utf-8-sig")

    print("\nControlli superati: 5 territori, 7 anni, 11 tipologie ricettive.")
    print("Quadratura province/regione e categorie: OK")
    print(f"Dataset creato: {destinazione}")
    print(f"Righe: {len(tabella)} | Colonne: {len(tabella.columns)}")
    print("\nLiguria 2025 - Totale esercizi ricettivi:")
    print(tabella.loc[
        (tabella["Territorio"] == "Liguria")
        & (tabella["Anno"] == 2025)
        & (tabella["Codice tipologia"] == "ALL"),
        ["Arrivi", "Presenze", "Permanenza media"]
    ].to_string(index=False))


if __name__ == "__main__":
    main()
