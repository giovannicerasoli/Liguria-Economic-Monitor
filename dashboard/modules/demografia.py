"""Analisi, indicatori e grafici del modulo Demografia."""

import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# Colori condivisi dalle visualizzazioni demografiche
BLU = "#20394B"
PETROLIO = "#008F9C"
SABBIA = "#D5A65C"
GRIGIO = "#AABAC5"


def numero(valore):
    return f"{valore:,.0f}".replace(",", ".")


def decimale(valore):
    return f"{valore:.2f}".replace(".", ",")


def delta(valore, decimali=0):
    segno = "+" if valore > 0 else ""
    if decimali == 0:
        return segno + numero(valore)
    return segno + decimale(valore)


def grafico_base(fig, altezza=330):
    fig.update_layout(
        template="none",
        height=altezza,
        font=dict(family="Arial", color=BLU),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=65, r=25, t=20, b=40),
        showlegend=False,
        hoverlabel=dict(bgcolor=BLU, font=dict(color="white")),
    )
    return fig


def mostra_demografia(territorio, storico, invecchiamento, dati_eta):
    """Mostra il modulo Demografia completo per il territorio selezionato."""

    # Indicatori per il territorio selezionato

    serie = storico[
        storico["Territorio"] == territorio
    ].sort_values("Anno").copy()

    indici = invecchiamento[
        invecchiamento["Territorio"] == territorio
    ].sort_values("Anno").copy()

    attuale = serie[serie["Anno"] == 2025].iloc[0]
    precedente = serie[serie["Anno"] == 2024].iloc[0]

    eta_attuale = indici[indici["Anno"] == 2025].iloc[0]
    eta_precedente = indici[indici["Anno"] == 2024].iloc[0]

    residenti = int(attuale["Residenti"])
    residenti_2019 = int(
        serie[serie["Anno"] == 2019]["Residenti"].iloc[0]
    )

    variazione_annua = residenti - int(precedente["Residenti"])
    variazione_periodo = residenti - residenti_2019

    variazione_percentuale = (
        variazione_periodo / residenti_2019 * 100
    )

    anziani = float(eta_attuale["Anziani (%)"])
    indice = float(eta_attuale["Indice di vecchiaia"])

    delta_anziani = (
        anziani - float(eta_precedente["Anziani (%)"])
    )

    delta_indice = (
        indice - float(eta_precedente["Indice di vecchiaia"])
    )

    indice_2019 = float(
        indici[indici["Anno"] == 2019][
            "Indice di vecchiaia"
        ].iloc[0]
    )

    variazione_indice_periodo = indice - indice_2019

    titolo_territorio = (
        "La Liguria" if territorio == "Liguria"
        else territorio
    )

    titolo_hero = (
        "La Liguria attraverso i dati"
        if territorio == "Liguria"
        else f"{territorio} attraverso i dati"
    )

    soggetto_testo = (
        "la Liguria"
        if territorio == "Liguria"
        else territorio
    )


    # Intestazione demografica già presente nella versione originale
    # Intestazione del modulo Demografia
    st.html(f"""
    <div class="lem-header">
        <div class="lem-brand">
            Liguria Economic Monitor / Demografia
        </div>

        <h1>{titolo_hero}</h1>

        <p>
            Popolazione, trasformazioni territoriali
            e invecchiamento demografico · 2019–2025
        </p>
    </div>
    """)

    # KPI

    mostra_kpi(
        titolo_territorio=titolo_territorio,
        residenti=numero(residenti),
        variazione=delta(variazione_annua),
        anziani=decimale(anziani),
        delta_anziani=delta(delta_anziani, 2),
        indice=decimale(indice),
        delta_indice=delta(delta_indice, 2)
    )

    # Evoluzione popolazione

    fig_pop = crea_grafico_popolazione(
        serie=serie,
        petrolio=PETROLIO,
        grafico_base=grafico_base,
        numero=numero
    )

    # Confronto province

    fig_province = crea_grafico_confronto_province(
        storico=storico,
        territorio=territorio,
        petrolio=PETROLIO,
        grigio=GRIGIO,
        grafico_base=grafico_base
    )

    # Grafici popolazione

    st.html("""
    <div class="lem-section">
        <h2>01 / Dinamica della popolazione</h2>
        <span>Variazioni territoriali · 2019–2025</span>
    </div>
    """)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        with st.container(border=True, key="lem_chart_demo_1"):
            st.markdown("**Evoluzione dei residenti**")
            st.caption(f"{territorio} · 2019–2025")
            st.plotly_chart(
                fig_pop,
                width="stretch",
                theme=None,
                config={"displayModeBar": False}
            )

    with col2:
        with st.container(border=True, key="lem_chart_demo_2"):
            st.markdown("**Variazione per provincia**")
            st.caption("Differenza percentuale tra 2019 e 2025")
            st.plotly_chart(
                fig_province,
                width="stretch",
                theme=None,
                config={"displayModeBar": False}
            )

    # Indice di vecchiaia

    fig_indice = crea_grafico_invecchiamento(
        invecchiamento=invecchiamento,
        territorio=territorio,
        petrolio=PETROLIO,
        grigio=GRIGIO,
        grafico_base=grafico_base
    )

    # Piramide demografica

    fig_piramide = crea_grafico_piramide(
        dati_eta=dati_eta,
        territorio=territorio,
        residenti=residenti,
        petrolio=PETROLIO,
        sabbia=SABBIA,
        grafico_base=grafico_base,
        numero=numero
    )

    # Grafici struttura per età

    st.html("""
    <div class="lem-section">
        <h2>02 / Struttura e invecchiamento</h2>
        <span>Trasformazioni demografiche</span>
    </div>
    """)

    col3, col4 = st.columns(2, gap="medium")

    with col3:
        with st.container(border=True, key="lem_chart_demo_3"):
            st.markdown("**Evoluzione dell'indice di vecchiaia**")
            st.caption(f"{territorio} · 2019–2025")
            st.plotly_chart(
                fig_indice,
                width="stretch",
                theme=None,
                config={"displayModeBar": False}
            )
            st.caption(
                "Indice: residenti di almeno 65 anni "
                "ogni 100 residenti di 0–14 anni."
            )

    with col4:
        with st.container(border=True, key="lem_chart_demo_4"):
            st.markdown("**Piramide demografica**")
            st.caption(f"{territorio} · 1° gennaio 2025")

            st.plotly_chart(
                fig_piramide,
                width="stretch",
                theme=None,
                config={"displayModeBar": False}
            )

            st.caption(
                "Distribuzione della popolazione residente "
                "per classi quinquennali di età e sesso."
            )

    # Interpretazione statistica

    if variazione_periodo < 0:
        movimento = (
            f"ha perso {numero(abs(variazione_periodo))} residenti"
        )
    elif variazione_periodo > 0:
        movimento = (
            f"ha guadagnato {numero(variazione_periodo)} residenti"
        )
    else:
        movimento = "ha mantenuto invariato il numero di residenti"

    if variazione_indice_periodo > 0:
        tendenza_eta = (
            "è aumentato di "
            f"{decimale(variazione_indice_periodo)} punti"
        )
    elif variazione_indice_periodo < 0:
        tendenza_eta = (
            "è diminuito di "
            f"{decimale(abs(variazione_indice_periodo))} punti"
        )
    else:
        tendenza_eta = "è rimasto invariato"

    st.html(f"""
    <div class="lem-insight">

        <h3>Cosa raccontano i dati</h3>

        <p>
            Tra il 2019 e il 2025, {soggetto_testo}
            {movimento},
            con una variazione complessiva del
            {delta(variazione_percentuale, 2)}%.
            Nello stesso periodo, l'indice di vecchiaia
            {tendenza_eta},
            passando da {decimale(indice_2019)}
            a {decimale(indice)}.
            Nel 2025, il {decimale(anziani)}% della
            popolazione residente ha almeno 65 anni.
        </p>

    </div>
    """)

    # Fonti

    st.html("""
    <div class="lem-footer">
        Liguria Economic Monitor · Modulo Demografia<br>
        Fonte: ISTAT — Popolazione residente al 1° gennaio.<br>
        Elaborazioni statistiche su dati 2019–2025.
        Le variazioni descrivono differenze tra stock
        di popolazione alle date indicate.
    </div>
    """)


# ============================================================
# INDICATORI PRINCIPALI
# ============================================================

def mostra_kpi(
    titolo_territorio,
    residenti,
    variazione,
    anziani,
    delta_anziani,
    indice,
    delta_indice
):

    st.html(f"""
    <div class="lem-section">
        <h2>{titolo_territorio} in numeri</h2>
        <span>Al 1° gennaio 2025</span>
    </div>

    <div class="lem-kpis">

        <div class="lem-kpi">
            <div class="lem-kpi-label">
                Popolazione residente
            </div>

            <div class="lem-kpi-value">
                {residenti}
            </div>

            <div class="lem-kpi-delta">
                <strong>{variazione} residenti</strong>
                rispetto al 2024
            </div>
        </div>

        <div class="lem-kpi">
            <div class="lem-kpi-label">
                Residenti con almeno 65 anni
            </div>

            <div class="lem-kpi-value">
                {anziani}%
            </div>

            <div class="lem-kpi-delta">
                <strong>{delta_anziani} punti percentuali</strong>
                rispetto al 2024
            </div>
        </div>

        <div class="lem-kpi">
            <div class="lem-kpi-label">
                Indice di vecchiaia
            </div>

            <div class="lem-kpi-value">
                {indice}
            </div>

            <div class="lem-kpi-delta">
                <strong>{delta_indice} punti</strong>
                rispetto al 2024
            </div>
        </div>

    </div>
    """)


# ============================================================
# GRAFICO EVOLUZIONE DELLA POPOLAZIONE
# ============================================================

def crea_grafico_popolazione(serie, petrolio, grafico_base, numero):

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=serie["Anno"],
        y=serie["Residenti"],
        mode="lines+markers",
        line=dict(color=petrolio, width=3),
        marker=dict(
            size=8,
            color="white",
            line=dict(color=petrolio, width=2.5)
        ),
        customdata=serie["Residenti"].apply(numero),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "%{customdata} residenti"
            "<extra></extra>"
        )
    ))

    # Adattiamo la scala ai dati del territorio
    minimo = serie["Residenti"].min()
    massimo = serie["Residenti"].max()

    margine = max(
        (massimo - minimo) * 0.2,
        massimo * 0.0015
    )

    fig = grafico_base(fig)

    fig.update_layout(
        xaxis=dict(
            dtick=1,
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            range=[minimo - margine, massimo + margine],
            gridcolor="#E9EFF2",
            tickformat=",d",
            zeroline=False
        )
    )

    return fig


# ============================================================
# GRAFICO CONFRONTO TRA PROVINCE
# ============================================================

def crea_grafico_confronto_province(
    storico,
    territorio,
    petrolio,
    grigio,
    grafico_base
):

    # Escludiamo il totale regionale
    province = storico[
        storico["Territorio"] != "Liguria"
    ].copy()

    # Confrontiamo popolazione 2019 e 2025
    confronto = province.pivot(
        index="Territorio",
        columns="Anno",
        values="Residenti"
    )

    # Calcoliamo la variazione percentuale
    confronto["Variazione"] = (
        (confronto[2025] / confronto[2019] - 1) * 100
    )

    confronto = confronto.sort_values("Variazione")

    # Evidenziamo la provincia selezionata

    colori = [
        "#D65F55" if valore < 0
        else petrolio if valore > 0
        else grigio
        for valore in confronto["Variazione"]
    ]


    opacita = [
        1.0 if territorio == "Liguria" or nome == territorio
        else 0.45
        for nome in confronto.index
    ]


    # Creiamo il grafico
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=confronto["Variazione"],
        y=confronto.index,
        orientation="h",
        marker_color=colori,
        marker_opacity=opacita,
        text=[
            f"{v:+.2f}%".replace(".", ",")
            for v in confronto["Variazione"]
        ],
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Variazione: %{x:.2f}%"
            "<extra></extra>"
        )
    ))

    fig = grafico_base(fig)

    fig.update_layout(
        bargap=0.5,
        margin=dict(l=85, r=30, t=20, b=45),

        xaxis=dict(
            range=[
                min(-0.5, confronto["Variazione"].min() * 1.5),
                max(0.5, confronto["Variazione"].max() * 1.5)
            ],
            ticksuffix="%",
            gridcolor="#E9EFF2",
            zeroline=True,
            zerolinecolor="#94A3B8"
        ),

        yaxis=dict(
            autorange="reversed",
            showgrid=False
        )
    )

    return fig


# ============================================================
# GRAFICO EVOLUZIONE DELL'INDICE DI VECCHIAIA
# ============================================================

def crea_grafico_invecchiamento(
    invecchiamento,
    territorio,
    petrolio,
    grigio,
    grafico_base
):

    # Dati del territorio selezionato
    indici = invecchiamento[
        invecchiamento["Territorio"] == territorio
    ].sort_values("Anno")

    fig = go.Figure()

    # Aggiungiamo il riferimento regionale
    # solo quando viene selezionata una provincia
    if territorio != "Liguria":

        regionale = invecchiamento[
            invecchiamento["Territorio"] == "Liguria"
        ].sort_values("Anno")

        fig.add_trace(go.Scatter(
            x=regionale["Anno"],
            y=regionale["Indice di vecchiaia"],
            mode="lines",
            name="Liguria",
            line=dict(
                color=grigio,
                width=2,
                dash="dash"
            ),
            hovertemplate=(
                "Liguria · %{x}<br>"
                "Indice: %{y:.2f}"
                "<extra></extra>"
            )
        ))

    # Andamento del territorio selezionato
    fig.add_trace(go.Scatter(
        x=indici["Anno"],
        y=indici["Indice di vecchiaia"],
        mode="lines+markers",
        name=territorio,
        line=dict(
            color=petrolio,
            width=3
        ),
        marker=dict(
            size=8,
            color="white",
            line=dict(
                color=petrolio,
                width=2.5
            )
        ),
        hovertemplate=(
            "%{x}<br>"
            "Indice di vecchiaia: %{y:.2f}"
            "<extra></extra>"
        )
    ))

    # Applichiamo lo stile comune
    fig = grafico_base(fig, altezza=440)

    fig.update_layout(
        showlegend=(territorio != "Liguria"),

        xaxis=dict(
            dtick=1,
            showgrid=False
        ),

        yaxis=dict(
            gridcolor="#E9EFF2",
            zeroline=False
        ),

        legend=dict(
            orientation="h",
            y=1.12,
            x=0
        )
    )

    return fig


# ============================================================
# GRAFICO PIRAMIDE DEMOGRAFICA
# ============================================================

def crea_grafico_piramide(
    dati_eta,
    territorio,
    residenti,
    petrolio,
    sabbia,
    grafico_base,
    numero
):

    # Selezioniamo le età effettive
    # Escludiamo le righe riepilogative (999)
    dati_piramide = dati_eta[
        dati_eta["Età"].between(0, 100)
    ].copy()

    # Selezioniamo la provincia richiesta
    if territorio != "Liguria":
        dati_piramide = dati_piramide[
            dati_piramide["Provincia"] == territorio
        ].copy()

    # Costruiamo le fasce quinquennali
    fasce = [
        f"{i}-{i+4}"
        for i in range(0, 100, 5)
    ] + ["100+"]

    dati_piramide["Fascia"] = pd.cut(
        dati_piramide["Età"],
        bins=list(range(0, 101, 5)) + [float("inf")],
        labels=fasce,
        right=False
    )

    # Aggregazione per fascia e sesso
    piramide = (
        dati_piramide
        .groupby("Fascia", observed=True)[
            ["Totale maschi", "Totale femmine"]
        ]
        .sum()
        .reindex(fasce, fill_value=0)
    )

    # Controlliamo la coerenza dei dati
    totale_piramide = int(piramide.to_numpy().sum())

    if totale_piramide != residenti:
        st.error(
            "Errore di coerenza nei dati della piramide."
        )
        st.stop()

    # Creiamo la figura Plotly
    fig = go.Figure()

    # Uomini: valori negativi per mostrarli a sinistra
    fig.add_trace(go.Bar(
        x=-piramide["Totale maschi"],
        y=piramide.index,
        name="Uomini",
        orientation="h",
        marker_color="#4C78A8",
        customdata=piramide["Totale maschi"].apply(numero),
        hovertemplate=(
            "Uomini · %{y}<br>"
            "%{customdata} residenti"
            "<extra></extra>"
        )
    ))

    # Donne: valori positivi a destra
    fig.add_trace(go.Bar(
        x=piramide["Totale femmine"],
        y=piramide.index,
        name="Donne",
        orientation="h",
        marker_color="#A477B5",
        customdata=piramide["Totale femmine"].apply(numero),
        hovertemplate=(
            "Donne · %{y}<br>"
            "%{customdata} residenti"
            "<extra></extra>"
        )
    ))

    # Calcoliamo una scala simmetrica e arrotondata
    massimo = piramide[
        ["Totale maschi", "Totale femmine"]
    ].max().max()

    limite_iniziale = massimo * 1.15

    ordine = 10 ** math.floor(
        math.log10(limite_iniziale)
    )

    limite = math.ceil(
        limite_iniziale / ordine
    ) * ordine

    tacche = [
        -limite,
        -limite / 2,
        0,
        limite / 2,
        limite
    ]

    # Applichiamo lo stile comune
    fig = grafico_base(fig, altezza=440)

    fig.update_layout(
        barmode="relative",
        bargap=0.15,

        margin=dict(
            l=55,
            r=20,
            t=35,
            b=40
        ),

        showlegend=True,

        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=1.13
        ),

        xaxis=dict(
            range=[-limite, limite],
            tickvals=tacche,
            ticktext=[
                numero(abs(v))
                for v in tacche
            ],
            gridcolor="#E9EFF2",
            zeroline=True,
            zerolinecolor="#94A3B8"
        ),

        yaxis=dict(
            categoryorder="array",
            categoryarray=fasce,
            showgrid=False
        )
    )

    return fig
