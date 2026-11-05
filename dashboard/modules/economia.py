
from pathlib import Path
from html import escape
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from .lavoro import mostra_lavoro


# ============================================================
# LIGURIA ECONOMIC MONITOR - MODULO ECONOMIA E IMPRESE
# Fonte: Unioncamere-InfoCamere, Movimprese (2019-2025)
# ============================================================

BLU = "#20394B"
PETROLIO = "#008F9C"
VERDE = "#269477"
ROSSO = "#D65F55"
GRIGIO = "#526779"
GRIGIO_BARRE = "#AABBC4"
GRIGLIA = "#E4EBEF"

NOMI_SETTORI = {
    "A": "Agricoltura e pesca",
    "B": "Estrazione minerali",
    "C": "Manifattura",
    "D": "Energia",
    "E": "Acqua e rifiuti",
    "F": "Costruzioni",
    "G": "Commercio",
    "H": "Trasporto e magazzinaggio",
    "I": "Alloggio e ristorazione",
    "J": "Informazione e comunicazione",
    "K": "Finanza e assicurazioni",
    "L": "Attività immobiliari",
    "M": "Attività professionali",
    "N": "Servizi di supporto",
    "O": "Amministrazione pubblica",
    "P": "Istruzione",
    "Q": "Sanità e assistenza",
    "R": "Arte, sport e intrattenimento",
    "S": "Altri servizi",
    "T": "Attività di famiglie",
    "Altri": "Altri settori",
}


# ============================================================
# CARICAMENTO DATI
# ============================================================

def percorso_dati(nome_file):
    """Restituisce il percorso di un CSV elaborato del progetto."""
    progetto = Path(__file__).resolve().parents[2]
    return progetto / "data" / "processed" / nome_file


@st.cache_data
def carica_imprese():
    """Serie storica territoriale Movimprese, 2019-2025."""
    dati = pd.read_csv(
        percorso_dati("imprese_serie_storica_2019_2025.csv"),
        sep=";",
        encoding="utf-8-sig",
    )
    dati["Anno"] = dati["Anno"].astype(int)
    return dati


@st.cache_data
def carica_dettaglio_imprese():
    """Dati provinciali per settore e forma giuridica."""
    dati = pd.read_csv(
        percorso_dati("imprese_dettaglio_2019_2025.csv"),
        sep=";",
        encoding="utf-8-sig",
    )
    dati["Anno"] = dati["Anno"].astype(int)
    return dati


# ============================================================
# FUNZIONI DI SUPPORTO
# ============================================================

def formatta_numero(valore):
    return f"{int(valore):,}".replace(",", ".")


def formatta_delta(valore):
    segno = "+" if valore > 0 else ""
    return segno + formatta_numero(valore)


def colore_delta(valore):
    """Colore coerente con il segno della variazione."""
    if valore < 0:
        return ROSSO
    if valore > 0:
        return VERDE
    return GRIGIO


def stile_grafico(fig, titolo, altezza):
    """Impostazioni visive condivise tra i quattro grafici."""
    fig.update_layout(
        title=dict(
            text=titolo,
            font=dict(size=17, color=BLU)
        ),
        height=altezza,
        margin=dict(l=20, r=55, t=65, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13, color=BLU),
        showlegend=False,
    )
    return fig


def prepara_settori(dettaglio, territorio, anni):
    """Filtra territorio e anni ed esclude le non classificate."""

    dati = dettaglio[
        dettaglio["Anno"].isin(anni)
    ].copy()

    if territorio != "Liguria":
        dati = dati[
            dati["Provincia"] == territorio
        ].copy()

    dati["Codice"] = dati["Settore"].str.extract(
        r"^\s*([A-Z])\b",
        expand=False
    )

    return dati[
        dati["Codice"].notna()
        & (dati["Codice"] != "X")
    ]


# ============================================================
# GRAFICO 1 - EVOLUZIONE DELLE IMPRESE ATTIVE
# ============================================================

def crea_grafico_imprese(dati, territorio):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=dati["Anno"],
            y=dati["Attive"],
            mode="lines+markers",
            name="Imprese attive",
            line=dict(
                color=PETROLIO,
                width=3
            ),

            marker=dict(
                size=8,
                color="white",
                line=dict(
                    color=PETROLIO,
                    width=2.5
                )
            ),

            hovertemplate=(
                "Anno: %{x}<br>"
                "Imprese attive: %{y:,.0f}"
                "<extra></extra>"
            ),
        )
    )

    stile_grafico(
        fig,
        f"Evoluzione delle imprese attive — {territorio}",
        400
    )

    fig.update_layout(
        hovermode="x unified",
        xaxis=dict(
            tickmode="linear",
            dtick=1,
            showgrid=False
        ),
        yaxis=dict(
            title="Numero di imprese attive",
            tickformat=",",
            gridcolor=GRIGLIA,
            zeroline=False,
            range=[
                dati["Attive"].min() * 0.99,
                dati["Attive"].max() * 1.01,
            ],
        ),
    )

    return fig


# ============================================================
# GRAFICO 2 - CONFRONTO PROVINCIALE
# ============================================================

def crea_grafico_province(dati, territorio):

    province = dati[
        (dati["Territorio"] != "Liguria")
        & dati["Anno"].isin([2019, 2025])
    ]

    confronto = province.pivot(
        index="Territorio",
        columns="Anno",
        values="Attive"
    )

    confronto["Variazione (%)"] = (
        (confronto[2025] - confronto[2019])
        / confronto[2019]
        * 100
    )

    confronto = confronto.sort_values(
        "Variazione (%)"
    )

    valori = confronto["Variazione (%)"]


    colori = [
        ROSSO if valore < 0
        else VERDE if valore > 0
        else GRIGIO_BARRE
        for valore in valori
    ]


    opacita = [
        1.0 if territorio == "Liguria" or nome == territorio
        else 0.45
        for nome in confronto.index
    ]


    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=valori,
            y=confronto.index,
            orientation="h",
            marker_color=colori,
            marker_opacity=opacita,
            text=[
                f"{v:+.2f}%".replace(".", ",")
                for v in valori
            ],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "%{y}<br>"
                "Variazione: %{x:+.2f}%"
                "<extra></extra>"
            ),
        )
    )

    stile_grafico(
        fig,
        "Variazione delle imprese attive per provincia",
        400
    )

    fig.update_layout(
        xaxis=dict(
            title="Variazione 2019–2025 (%)",
            ticksuffix="%",
            range=[
                min(valori) - 1.5,
                max(0.8, max(valori) + 0.8)
            ],
            zeroline=True,
            zerolinecolor=GRIGIO_BARRE,
            gridcolor=GRIGLIA,
        ),
        yaxis=dict(
            autorange="reversed",
            showgrid=False
        ),
    )

    return fig


# ============================================================
# GRAFICO 3 - STRUTTURA SETTORIALE 2025
# ============================================================

def crea_grafico_settori(dettaglio, territorio):

    dati = prepara_settori(
        dettaglio,
        territorio,
        [2025]
    )

    settori = (
        dati.groupby("Codice")["Attive"]
        .sum()
        .sort_values(ascending=False)
    )

    totale = settori.sum()

    principali = settori.head(10).copy()

    altri = settori.iloc[10:].sum()

    if altri > 0:
        principali.loc["Altri"] = altri

    tabella = pd.DataFrame({
        "Codice": principali.index,
        "Attive": principali.values,
    })

    tabella["Settore"] = (
        tabella["Codice"].map(NOMI_SETTORI)
    )

    tabella["Quota"] = (
        tabella["Attive"] / totale * 100
    )

    tabella = tabella.sort_values(
        "Quota",
        ascending=False
    )

    colori = [
        GRIGIO_BARRE if codice == "Altri" else PETROLIO
        for codice in tabella["Codice"]
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=tabella["Quota"],
            y=tabella["Settore"],
            orientation="h",
            marker_color=colori,
            customdata=tabella["Attive"],
            text=[
                f"{v:.1f}%".replace(".", ",")
                for v in tabella["Quota"]
            ],
            textposition="outside",
            textfont_size=12,
            cliponaxis=False,
            hovertemplate=(
                "%{y}<br>"
                "Imprese attive: %{customdata:,.0f}<br>"
                "Quota: %{x:.2f}%"
                "<extra></extra>"
            ),
        )
    )

    stile_grafico(
        fig,
        f"Struttura settoriale — {territorio}, 2025",
        550
    )

    fig.update_layout(
        xaxis=dict(
            title="Quota sulle imprese attive classificate (%)",
            ticksuffix="%",
            range=[
                0,
                tabella["Quota"].max() + 5
            ],
            gridcolor=GRIGLIA,
            zeroline=False,
        ),
        yaxis=dict(
            autorange="reversed",
            showgrid=False
        ),
    )

    return fig


# ============================================================
# GRAFICO 4 - EVOLUZIONE DEI SETTORI
# ============================================================

def crea_grafico_evoluzione_settori(dettaglio, territorio):

    dati = prepara_settori(
        dettaglio,
        territorio,
        [2019, 2025]
    )

    confronto = (
        dati.groupby(["Codice", "Anno"])["Attive"]
        .sum()
        .unstack(fill_value=0)
    )

    confronto["Variazione"] = (
        confronto[2025] - confronto[2019]
    )

    confronto["Settore"] = (
        confronto.index.map(NOMI_SETTORI)
    )

    diminuzioni = confronto[
        confronto["Variazione"] < 0
    ].nsmallest(
        5,
        "Variazione"
    )

    aumenti = confronto[
        confronto["Variazione"] > 0
    ].nlargest(
        5,
        "Variazione"
    )

    selezionati = pd.concat(
        [diminuzioni, aumenti]
    ).sort_values("Variazione")

    valori = selezionati["Variazione"]

    dettagli = [
        [
            int(riga[2019]),
            int(riga[2025]),
            (
                100 * riga["Variazione"] / riga[2019]
                if riga[2019] > 0
                else float("nan")
            ),
        ]
        for _, riga in selezionati.iterrows()
    ]


    colori = [
        ROSSO if valore < 0 else VERDE
        for valore in valori
    ]


    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=valori,
            y=selezionati["Settore"],
            orientation="h",
            marker_color=colori,
            customdata=dettagli,
            text=[
                f"{int(v):+,}".replace(",", ".")
                for v in valori
            ],
            textposition="outside",
            textfont_size=12,
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Imprese 2019: %{customdata[0]:,.0f}<br>"
                "Imprese 2025: %{customdata[1]:,.0f}<br>"
                "Variazione: %{x:+,.0f}<br>"
                "Variazione percentuale: "
                "%{customdata[2]:+.2f}%"
                "<extra></extra>"
            ),
        )
    )

    stile_grafico(
        fig,
        f"Settori in crescita e contrazione — {territorio}",
        550
    )

    fig.update_layout(
        xaxis=dict(
            title="Variazione delle imprese attive 2019–2025",
            range=[
                min(valori.min() * 1.25, -1),
                max(valori.max() * 1.25, 1)
            ],
            gridcolor=GRIGLIA,
            zeroline=True,
            zerolinecolor=BLU,
        ),
        yaxis=dict(
            autorange="reversed",
            showgrid=False
        ),
    )

    return fig


# ============================================================
# PAGINA ECONOMIA E IMPRESE
# ============================================================

def mostra_economia(territorio):
    """Visualizza il modulo Economia e imprese."""


    # Navigazione interna del modulo Economia

    area = st.segmented_control(
        "Ambito economico",
        options=[
            "Tessuto imprenditoriale",
            "Mercato del lavoro"
        ],
        default="Tessuto imprenditoriale",
        required=True,
        selection_mode="single",
        key="area_economia"
    )

    if area == "Mercato del lavoro":
        mostra_lavoro(territorio)
        return


    # --------------------------------------------------------
    # Caricamento e selezione dei dati
    # --------------------------------------------------------

    dati = carica_imprese()

    storico = (
        dati[dati["Territorio"] == territorio]
        .sort_values("Anno")
        .copy()
    )

    if storico.empty:
        st.error(
            f"Nessun dato disponibile per {territorio}."
        )
        return

    dati_2025 = storico[storico["Anno"] == 2025]
    dati_2024 = storico[storico["Anno"] == 2024]
    dati_2019 = storico[storico["Anno"] == 2019]

    if (
        dati_2025.empty
        or dati_2024.empty
        or dati_2019.empty
    ):
        st.error(
            "Mancano i dati del 2019, 2024 o 2025."
        )
        return

    corrente = dati_2025.iloc[0]
    precedente = dati_2024.iloc[0]

    attive = int(corrente["Attive"])
    registrate = int(corrente["Registrate"])
    saldo = int(corrente["Saldo"])

    variazione_attive = (
        attive - int(precedente["Attive"])
    )

    variazione_registrate = (
        registrate - int(precedente["Registrate"])
    )

    # --------------------------------------------------------
    # Intestazione
    # --------------------------------------------------------

    ambito = (
        "in Liguria"
        if territorio == "Liguria"
        else f"nella provincia di {territorio}"
    )


    # Intestazione condivisa con il modulo Demografia

    st.html(f"""
    <div class="lem-header">

        <div class="lem-brand">
            Liguria Economic Monitor / Economia e imprese
        </div>

        <h1>Il tessuto imprenditoriale attraverso i dati</h1>

        <p>
            Imprese attive, struttura settoriale
            e dinamiche imprenditoriali {ambito}
            · 2019–2025
        </p>

    </div>
    """)


    # --------------------------------------------------------
    # KPI con colori dinamici
    # --------------------------------------------------------


    # Classi CSS dinamiche per i KPI

    def classe_delta(valore):
        if valore < 0:
            return "lem-delta-negative"
        elif valore > 0:
            return "lem-delta-positive"
        return "lem-delta-neutral"

    classe_attive = classe_delta(variazione_attive)
    classe_registrate = classe_delta(variazione_registrate)


    st.html(f"""
    <div class="lem-section">

        <h2>{territorio} in numeri</h2>

        <span>Tessuto imprenditoriale · 2025</span>

    </div>

    <div class="lem-kpis">

        <div class="lem-kpi">

            <div class="lem-kpi-label">
                Imprese attive
            </div>

            <div class="lem-kpi-value">
                {formatta_numero(attive)}
            </div>

            <div class="lem-kpi-delta">

                
                
                
                <strong style="color: {colore_delta(variazione_registrate)} !important;">


                    {formatta_delta(variazione_attive)} imprese
                </strong>


                rispetto al 2024

            </div>

        </div>

        <div class="lem-kpi">

            <div class="lem-kpi-label">
                Imprese registrate
            </div>

            <div class="lem-kpi-value">
                {formatta_numero(registrate)}
            </div>

            <div class="lem-kpi-delta">

                
                <strong style="color: {'#B4534A' if variazione_registrate < 0 else '#16758A' if variazione_registrate > 0 else '#526779'} !important;">
                    {formatta_delta(variazione_registrate)} imprese
                </strong>


                rispetto al 2024

            </div>

        </div>

        <div class="lem-kpi">

            <div class="lem-kpi-label">
                Saldo iscrizioni–cessazioni
            </div>

            <div class="lem-kpi-value">
                {formatta_delta(saldo)}
            </div>

            <div class="lem-kpi-delta">

                <strong>Anno 2025</strong>

                · Cessazioni non d'ufficio

            </div>

        </div>

    </div>
    """)

    st.caption(
        "Fonte: Unioncamere–InfoCamere, Movimprese. "
        "Il saldo è pari alle iscrizioni meno le "
        "cessazioni non d'ufficio e non coincide "
        "necessariamente con la variazione "
        "delle imprese attive."
    )


    # ====================================================
    # GRAFICI - STRUTTURA CONDIVISA CON DEMOGRAFIA
    # ====================================================

    # Carichiamo una sola volta i dati settoriali
    dettaglio = carica_dettaglio_imprese()

    # ====================================================
    # 01 / DINAMICA DELLE IMPRESE
    # ====================================================

    st.html("""
    <div class="lem-section">
        <h2>01 / Dinamica delle imprese</h2>
        <span>Evoluzione e variazioni territoriali · 2019–2025</span>
    </div>
    """)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        with st.container(border=True, key="lem_chart_economia_1"):

            st.markdown("**Evoluzione delle imprese attive**")
            st.caption(f"{territorio} · 2019–2025")

            fig_imprese = crea_grafico_imprese(
                storico, territorio
            )


            fig_imprese.update_layout(
                title=None,
                height=400,
                margin=dict(l=80, r=25, t=20, b=55),
                xaxis=dict(
                    title=None,
                    tickfont=dict(size=11),
                    automargin=True
                ),
                yaxis=dict(
                    title=None,
                    tickfont=dict(size=11),
                    automargin=True
                )
            )


            st.plotly_chart(
                fig_imprese,
                width="stretch",
                theme=None,
                config={"displayModeBar": False}
            )

            st.caption(
                "Numero di imprese attive al termine "
                "di ciascun anno."
            )

    with col2:
        with st.container(border=True, key="lem_chart_economia_2"):

            st.markdown("**Variazione per provincia**")
            st.caption("Differenza percentuale tra 2019 e 2025")

            fig_province = crea_grafico_province(
                dati, territorio
            )


            fig_province.update_layout(
                title=None,
                height=400,
                margin=dict(l=110, r=35, t=20, b=65),
                xaxis=dict(
                    title=None,
                    tickfont=dict(size=11),
                    automargin=True
                ),
                yaxis=dict(
                    title=None,
                    tickfont=dict(size=12),
                    automargin=True
                )
            )


            st.plotly_chart(
                fig_province,
                width="stretch",
                theme=None,
                config={"displayModeBar": False}
            )

            st.caption(
                "Variazione percentuale delle imprese attive "
                "nelle quattro province liguri."
            )

    # ====================================================
    # 02 / STRUTTURA SETTORIALE
    # ====================================================

    st.html("""
    <div class="lem-section">
        <h2>02 / Struttura settoriale</h2>
        <span>Composizione e trasformazioni · 2019–2025</span>
    </div>
    """)

    col3, col4 = st.columns(2, gap="medium")

    with col3:
        with st.container(border=True, key="lem_chart_economia_3"):

            st.markdown("**Distribuzione delle imprese per settore**")
            st.caption(f"{territorio} · 2025")

            fig_settori = crea_grafico_settori(
                dettaglio, territorio
            )


            fig_settori.update_layout(
                title=None,
                height=550,
                margin=dict(l=180, r=35, t=20, b=65),
                font=dict(size=12, color=BLU),
                xaxis=dict(
                    title=None,
                    tickfont=dict(size=11),
                    automargin=True
                ),
                yaxis=dict(
                    title=None,
                    tickfont=dict(size=11),
                    automargin=True
                )
            )


            fig_settori.update_traces(textfont_size=12)

            st.plotly_chart(
                fig_settori,
                width="stretch",
                theme=None,
                config={"displayModeBar": False}
            )

            st.caption(
                "Quote delle imprese attive classificate. "
                "Escluse le imprese non classificate."
            )

    with col4:
        with st.container(border=True, key="lem_chart_economia_4"):

            st.markdown("**Settori in crescita e contrazione**")
            st.caption(f"{territorio} · 2019–2025")

            fig_evoluzione = crea_grafico_evoluzione_settori(
                dettaglio, territorio
            )


            fig_evoluzione.update_layout(
                title=None,
                height=550,
                margin=dict(l=180, r=45, t=20, b=65),
                font=dict(size=12, color=BLU),
                xaxis=dict(
                    title=None,
                    tickfont=dict(size=11),
                    automargin=True
                ),
                yaxis=dict(
                    title=None,
                    tickfont=dict(size=11),
                    automargin=True
                )
            )


            fig_evoluzione.update_traces(textfont_size=12)

            st.plotly_chart(
                fig_evoluzione,
                width="stretch",
                theme=None,
                config={"displayModeBar": False}
            )

            st.caption(
                "Cinque maggiori aumenti e diminuzioni "
                "del numero di imprese attive."
            )



    # ====================================================
    # INTERPRETAZIONE AUTOMATICA DEI DATI
    # ====================================================

    attive_2019 = int(
        storico.loc[
            storico["Anno"] == 2019, "Attive"
        ].iloc[0]
    )

    differenza = attive - attive_2019

    variazione_percentuale = (
        differenza / attive_2019 * 100
    )

    luogo = (
        "in Liguria"
        if territorio == "Liguria"
        else f"nella provincia di {territorio}"
    )

    andamento = (
        "aumentate"
        if differenza > 0
        else "diminuite"
        if differenza < 0
        else "rimaste invariate"
    )

    percentuale_testo = (
        f"{variazione_percentuale:+.2f}%"
        .replace(".", ",")
    )

    # Analisi settoriale 2019-2025

    settoriali = dettaglio[
        dettaglio["Anno"].isin([2019, 2025])
    ].copy()

    if territorio != "Liguria":
        settoriali = settoriali[
            settoriali["Provincia"] == territorio
        ].copy()

    settoriali["Codice"] = (
        settoriali["Settore"].str.extract(
            r"^\s*([A-Z])\b",
            expand=False
        )
    )

    settoriali = settoriali[
        settoriali["Codice"].notna()
        & (settoriali["Codice"] != "X")
    ]

    confronto = (
        settoriali
        .groupby(["Codice", "Anno"])["Attive"]
        .sum()
        .unstack(fill_value=0)
    )

    confronto["Variazione"] = (
        confronto[2025] - confronto[2019]
    )

    nomi_settori = (
        settoriali
        .drop_duplicates("Codice")
        .set_index("Codice")["Settore"]
        .to_dict()
    )

    codice_crescita = (
        confronto["Variazione"].idxmax()
    )

    codice_calo = (
        confronto["Variazione"].idxmin()
    )


    settore_crescita = escape(
        NOMI_SETTORI[codice_crescita]
    )

    settore_calo = escape(
        NOMI_SETTORI[codice_calo]
    )


    aumento = int(
        confronto.loc[
            codice_crescita, "Variazione"
        ]
    )

    diminuzione = int(
        confronto.loc[
            codice_calo, "Variazione"
        ]
    )

    # Riquadro interpretativo condiviso con Demografia

    st.html(f"""
    <div class="lem-insight">

        <h3>Cosa raccontano i dati</h3>

        <p>
            Tra il 2019 e il 2025 le imprese attive
            {luogo} sono {andamento} di
            <strong>{formatta_numero(abs(differenza))}
            unità</strong>, con una variazione
            complessiva del
            <strong>{percentuale_testo}</strong>.
        </p>

        <p>
            Il settore con il maggiore aumento
            in valore assoluto è
            <strong>{settore_crescita}</strong>,
            con <strong>{formatta_delta(aumento)}
            imprese attive</strong>.
            La maggiore contrazione riguarda
            <strong>{settore_calo}</strong>,
            con <strong>{formatta_delta(diminuzione)}
            imprese</strong>.
        </p>

        <p>
            Nel 2025 il saldo tra iscrizioni e
            cessazioni non d'ufficio è stato di
            <strong>{formatta_delta(saldo)}</strong>.
            Questo indicatore non coincide
            necessariamente con la variazione
            dello stock delle imprese attive.
        </p>

    </div>
    """)

    # ====================================================
    # FOOTER E NOTE METODOLOGICHE
    # ====================================================

    st.html("""
    <div class="lem-footer">

        <div>
            Liguria Economic Monitor · Modulo Economia e imprese
        </div>

        <div>
            Fonte: Unioncamere–InfoCamere, Movimprese.
        </div>

        <div>
            Elaborazioni statistiche su dati 2019–2025.
            Le variazioni descrivono differenze
            tra stock di imprese attive alle date indicate.
            Il saldo è calcolato come iscrizioni meno
            cessazioni non d'ufficio.
        </div>

    </div>
    """)
