
from pathlib import Path
import pandas as pd

# ============================================================
# LIGURIA ECONOMIC MONITOR
# Script 10 - Unificazione dei tassi del mercato del lavoro
# Fonte: ISTAT, Rilevazione sulle forze di lavoro
# ============================================================

PROGETTO = Path(__file__).resolve().parent.parent

RAW = PROGETTO / "data" / "raw" / "lavoro"
OUTPUT = PROGETTO / "data" / "processed"

TERRITORI = {
    "Liguria", "Genova", "Imperia", "Savona", "La Spezia"
}

SESSI = {"Maschi", "Femmine", "Totale"}
ANNI = set(range(2019, 2026))

CHIAVI = ["REF_AREA", "Territorio", "SEX", "Sesso", "Anno"]

INDICATORI = [
    (
        "tasso_occupazione_2019_2025.csv",
        "EMP_R",
        "Tasso occupazione"
    ),
    (
        "tasso_disoccupazione_2019_2025.csv",
        "UNEM_R",
        "Tasso disoccupazione"
    ),
    (
        "tasso_inattivita_2019_2025.csv",
        "INAC_R",
        "Tasso inattivita"
    )
]


# ============================================================
# CARICAMENTO E CONTROLLO DEI DATASET
# ============================================================

def carica_indicatore(nome_file, codice, colonna):

    dati = pd.read_csv(
        RAW / nome_file,
        sep=";",
        encoding="utf-8-sig"
    )

    richieste = {
        "REF_AREA", "Territorio", "SEX", "Sesso",
        "TIME_PERIOD", "Osservazione",
        "FREQ", "AGE", "DATA_TYPE"
    }

    if not richieste.issubset(dati.columns):
        raise ValueError(
            f"Colonne mancanti in {nome_file}: "
            f"{richieste - set(dati.columns)}"
        )

    # Controlliamo frequenza, età e indicatore
    if not (
        dati["FREQ"].eq("A")
        & dati["AGE"].eq("Y15-64")
        & dati["DATA_TYPE"].eq(codice)
    ).all():
        raise ValueError(
            f"Frequenza, età o indicatore errati: {nome_file}"
        )

    # Rinominiamo le colonne
    dati = dati.rename(columns={
        "TIME_PERIOD": "Anno",
        "Osservazione": colonna
    })

    dati["Anno"] = pd.to_numeric(
        dati["Anno"], errors="raise"
    ).astype(int)

    dati[colonna] = pd.to_numeric(
        dati[colonna], errors="raise"
    )

    # Verifichiamo le combinazioni attese
    osservate = set(
        dati[["Territorio", "Sesso", "Anno"]]
        .itertuples(index=False, name=None)
    )

    attese = {
        (territorio, sesso, anno)
        for territorio in TERRITORI
        for sesso in SESSI
        for anno in ANNI
    }

    if osservate != attese or dati.duplicated(CHIAVI).any():
        raise ValueError(
            f"Territori, sessi, anni incompleti "
            f"o duplicati: {nome_file}"
        )

    # Verifichiamo i valori dei tassi
    if (
        dati[colonna].isna().any()
        or not dati[colonna].between(0, 100).all()
    ):
        raise ValueError(
            f"Valori mancanti o non validi: {nome_file}"
        )

    print(
        f"{nome_file}: {len(dati)} osservazioni verificate"
    )

    return dati[CHIAVI + [colonna]]


# ============================================================
# UNIFICAZIONE DEI TRE INDICATORI
# ============================================================

serie = None

for nome_file, codice, colonna in INDICATORI:

    tabella = carica_indicatore(
        nome_file, codice, colonna
    )

    if serie is None:
        serie = tabella

    else:
        serie = serie.merge(
            tabella,
            on=CHIAVI,
            how="outer",
            validate="one_to_one",
            indicator=True
        )

        if not serie["_merge"].eq("both").all():
            raise ValueError(
                f"Chiavi non corrispondenti: {nome_file}"
            )

        serie = serie.drop(columns="_merge")


# ============================================================
# CONTROLLO DI COERENZA TRA I TASSI
# ============================================================

# Verifichiamo la relazione tra occupazione,
# disoccupazione e inattività.
# Tolleranza: 0,2 punti percentuali per arrotondamenti.

occupazione_calcolata = (
    (100 - serie["Tasso inattivita"])
    * (1 - serie["Tasso disoccupazione"] / 100)
)

scarto_massimo = (
    occupazione_calcolata
    - serie["Tasso occupazione"]
).abs().max()

if scarto_massimo > 0.2:
    raise ValueError(
        f"Tassi non coerenti: "
        f"scarto massimo {scarto_massimo:.3f} p.p."
    )


# ============================================================
# CREAZIONE DEI DATASET FINALI
# ============================================================

serie = (
    serie
    .sort_values(["Territorio", "Sesso", "Anno"])
    .reset_index(drop=True)
)

# Solo valori relativi a entrambi i sessi
serie_totale = serie[
    serie["Sesso"] == "Totale"
].copy()

OUTPUT.mkdir(parents=True, exist_ok=True)

# Dataset completo
serie.to_csv(
    OUTPUT / "mercato_lavoro_tassi_2019_2025.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

# Dataset totale per la dashboard
serie_totale.to_csv(
    OUTPUT / "mercato_lavoro_tassi_totale_2019_2025.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# RIEPILOGO FINALE
# ============================================================

print("\nRighe serie completa:", len(serie))
print("Righe serie totale:", len(serie_totale))

print(
    f"Scarto massimo tra tassi (arrotondamento): "
    f"{scarto_massimo:.3f} p.p."
)

print("\nLIGURIA 2025 - ENTRAMBI I SESSI")

print(
    serie_totale.loc[
        (serie_totale["Territorio"] == "Liguria")
        & (serie_totale["Anno"] == 2025),
        [
            "Anno",
            "Tasso occupazione",
            "Tasso disoccupazione",
            "Tasso inattivita"
        ]
    ].to_string(index=False)
)
