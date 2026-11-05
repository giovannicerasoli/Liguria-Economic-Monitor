
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# LIGURIA ECONOMIC MONITOR - MERCATO DEL LAVORO
# Fonte: ISTAT, Rilevazione sulle forze di lavoro
# ============================================================

BLU = "#20394B"
PETROLIO = "#008F9C"
VERDE = "#269477"
ROSSO = "#D65F55"
GRIGIO = "#526779"



# ============================================================
# CARICAMENTO DATI
# ============================================================

@st.cache_data
def carica_mercato_lavoro():

    progetto = Path(__file__).resolve().parents[2]

    percorso = (
        progetto
        / "data"
        / "processed"
        / "mercato_lavoro_tassi_totale_2019_2025.csv"
    )

    dati = pd.read_csv(
        percorso,
        sep=";",
        encoding="utf-8-sig"
    )

    dati["Anno"] = dati["Anno"].astype(int)

    return dati


@st.cache_data
def carica_mercato_lavoro_sesso():
    """Carica i tassi ISTAT distinti per sesso."""

    progetto = Path(__file__).resolve().parents[2]

    percorso = (
        progetto
        / "data"
        / "processed"
        / "mercato_lavoro_tassi_2019_2025.csv"
    )

    dati = pd.read_csv(
        percorso,
        sep=";",
        encoding="utf-8-sig"
    )

    dati["Anno"] = dati["Anno"].astype(int)

    return dati


# ============================================================
# FORMATTAZIONE
# ============================================================

def formatta_percentuale(valore):
    return f"{valore:.1f}".replace(".", ",") + "%"


def formatta_punti(valore):
    return f"{valore:+.1f}".replace(".", ",") + " punti percentuali"

def formatta_punti_estesi(valore):
    return f"{valore:+.1f}".replace(".", ",") + " punti percentuali"


def colore_variazione(valore, aumento_favorevole=True):

    if valore == 0:
        return GRIGIO

    miglioramento = (
        valore > 0 if aumento_favorevole
        else valore < 0
    )

    return VERDE if miglioramento else ROSSO


# ============================================================
# GRAFICO - EVOLUZIONE DEL TASSO DI OCCUPAZIONE
# ============================================================

def crea_grafico_occupazione(storico, territorio):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=storico["Anno"],
            y=storico["Tasso occupazione"],
            mode="lines+markers",
            name="Tasso di occupazione",
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
                "Tasso di occupazione: %{y:.1f}%"
                "<extra></extra>"
            )
        )
    )

    minimo = storico["Tasso occupazione"].min()
    massimo = storico["Tasso occupazione"].max()

    fig.update_layout(
        title=None,
        height=400,
        margin=dict(l=50, r=30, t=20, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            size=13,
            color=BLU
        ),
        showlegend=False,
        hovermode="x unified",
        xaxis=dict(
            title=None,
            tickmode="linear",
            dtick=1,
            showgrid=False
        ),
        yaxis=dict(
            title=None,
            ticksuffix="%",
            range=[
                minimo - 1,
                massimo + 1
            ],
            gridcolor="#E4EBEF",
            zeroline=False,
            automargin=True
        )
    )

    return fig


# ============================================================
# GRAFICO - EVOLUZIONE DEL TASSO DI DISOCCUPAZIONE
# ============================================================

def crea_grafico_disoccupazione(storico, territorio):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=storico["Anno"],
            y=storico["Tasso disoccupazione"],
            mode="lines+markers",
            name="Tasso di disoccupazione",
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
                "Tasso di disoccupazione: %{y:.1f}%"
                "<extra></extra>"
            )
        )
    )

    minimo = storico["Tasso disoccupazione"].min()
    massimo = storico["Tasso disoccupazione"].max()

    fig.update_layout(
        title=None,
        height=400,
        margin=dict(l=50, r=30, t=20, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            size=13,
            color=BLU
        ),
        showlegend=False,
        hovermode="x unified",
        xaxis=dict(
            title=None,
            tickmode="linear",
            dtick=1,
            showgrid=False
        ),
        yaxis=dict(
            title=None,
            ticksuffix="%",
            range=[
                max(0, minimo - 1),
                massimo + 1
            ],
            gridcolor="#E4EBEF",
            zeroline=False,
            automargin=True
        )
    )

    return fig


# ============================================================
# GRAFICO - VARIAZIONE OCCUPAZIONE PER PROVINCIA
# ============================================================

def crea_grafico_province_lavoro(dati, territorio):

    province = dati[
        (dati["Territorio"] != "Liguria")
        & dati["Anno"].isin([2019, 2025])
    ].copy()

    confronto = province.pivot(
        index="Territorio",
        columns="Anno",
        values="Tasso occupazione"
    )

    confronto["Variazione"] = (
        confronto[2025] - confronto[2019]
    ).round(1)

    confronto = confronto.sort_values(
        "Variazione", ascending=False
    )

    valori = confronto["Variazione"]

    colori = [
        PETROLIO if valore > 0
        else ROSSO if valore < 0
        else GRIGIO
        for valore in valori
    ]

    opacita = [
        1.0 if territorio == "Liguria" or nome == territorio
        else 0.4
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
                f"{v:+.1f}".replace(".", ",") + " punti percentuali"
                for v in valori
            ],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Variazione occupazione: %{x:+.1f} punti percentuali"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        title=None,
        height=400,
        margin=dict(l=95, r=65, t=20, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13, color=BLU),
        showlegend=False,
        xaxis=dict(
            title=None,
            range=[
                min(0, valori.min() - 1),
                max(0, valori.max()) + 2
            ],
            gridcolor="#E4EBEF",
            zeroline=True,
            zerolinecolor=GRIGIO
        ),
        yaxis=dict(
            title=None,
            autorange="reversed",
            automargin=True
        )
    )

    return fig


# ============================================================
# GRAFICO - OCCUPAZIONE PER SESSO
# ============================================================

def crea_grafico_genere_lavoro(dati, territorio):

    selezione = dati[
        (dati["Territorio"] == territorio)
        & (dati["Anno"] == 2025)
        & dati["Sesso"].isin(["Maschi", "Femmine"])
    ]

    tassi = selezione.set_index(
        "Sesso"
    )["Tasso occupazione"]

    uomini = float(tassi["Maschi"])
    donne = float(tassi["Femmine"])

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=[uomini, donne],
            y=["Uomini", "Donne"],
            orientation="h",
            marker_color=[
                "#4C78A8",
                "#A477B5"
            ],
            text=[
                formatta_percentuale(uomini),
                formatta_percentuale(donne)
            ],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Tasso di occupazione: %{x:.1f}%"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        title=None,
        height=400,
        margin=dict(l=90, r=50, t=20, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13, color=BLU),
        showlegend=False,
        xaxis=dict(
            title=None,
            range=[0, 100],
            ticksuffix="%",
            gridcolor="#E4EBEF",
            zeroline=False
        ),
        yaxis=dict(
            title=None,
            autorange="reversed",
            automargin=True
        )
    )

    return fig


# ============================================================
# PAGINA MERCATO DEL LAVORO
# ============================================================


# ============================================================
# GRAFICO - EVOLUZIONE DEL TASSO DI INATTIVITÀ
# ============================================================

def crea_grafico_inattivita(storico, territorio):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=storico["Anno"],
            y=storico["Tasso inattivita"],
            mode="lines+markers",
            name="Tasso di inattività",
            line=dict(color=PETROLIO, width=3),
            marker=dict(
                size=8,
                color="white",
                line=dict(color=PETROLIO, width=2.5)
            ),
            hovertemplate=(
                "Anno: %{x}<br>"
                "Tasso di inattività: %{y:.1f}%"
                "<extra></extra>"
            )
        )
    )

    minimo = storico["Tasso inattivita"].min()
    massimo = storico["Tasso inattivita"].max()

    fig.update_layout(
        title=None,
        height=400,
        margin=dict(l=50, r=30, t=20, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13, color=BLU),
        showlegend=False,
        hovermode="x unified",
        xaxis=dict(
            title=None,
            tickmode="linear",
            dtick=1,
            showgrid=False
        ),
        yaxis=dict(
            title=None,
            ticksuffix="%",
            range=[max(0, minimo - 1), massimo + 1],
            gridcolor="#E4EBEF",
            zeroline=False,
            automargin=True
        )
    )

    return fig


def mostra_lavoro(territorio):

    dati = carica_mercato_lavoro()

    storico = (
        dati[dati["Territorio"] == territorio]
        .sort_values("Anno")
        .copy()
    )

    if storico.empty:
        st.error(f"Nessun dato disponibile per {territorio}.")
        return

    corrente = storico.loc[storico["Anno"] == 2025]
    precedente = storico.loc[storico["Anno"] == 2024]

    if corrente.empty or precedente.empty:
        st.error("Mancano i dati del 2024 o del 2025.")
        return

    corrente = corrente.iloc[0]
    precedente = precedente.iloc[0]

    # ========================================================
    # INDICATORI
    # ========================================================

    occupazione = float(corrente["Tasso occupazione"])
    disoccupazione = float(corrente["Tasso disoccupazione"])
    inattivita = float(corrente["Tasso inattivita"])

    delta_occupazione = (
        occupazione - precedente["Tasso occupazione"]
    )

    delta_disoccupazione = (
        disoccupazione - precedente["Tasso disoccupazione"]
    )

    delta_inattivita = (
        inattivita - precedente["Tasso inattivita"]
    )

    colore_occ = colore_variazione(
        delta_occupazione,
        aumento_favorevole=True
    )

    colore_dis = colore_variazione(
        delta_disoccupazione,
        aumento_favorevole=False
    )

    colore_ina = colore_variazione(
        delta_inattivita,
        aumento_favorevole=False
    )

    # ========================================================
    # INTESTAZIONE
    # ========================================================

    ambito = (
        "in Liguria"
        if territorio == "Liguria"
        else f"nella provincia di {territorio}"
    )

    st.html(f"""
    <div class="lem-header">

        <div class="lem-brand">
            LIGURIA ECONOMIC MONITOR / MERCATO DEL LAVORO
        </div>

        <h1>Il mercato del lavoro attraverso i dati</h1>

        <p>
            Occupazione, disoccupazione e inattività
            {ambito} · 2019–2025
        </p>

    </div>
    """)

    # ========================================================
    # KPI
    # ========================================================

    st.html(f"""
    <div class="lem-section">
        <h2>{territorio} in numeri</h2>
        <span>Mercato del lavoro · 2025</span>
    </div>

    <div class="lem-kpis">

        <div class="lem-kpi">
            <div class="lem-kpi-label">
                Tasso di occupazione
            </div>

            <div class="lem-kpi-value">
                {formatta_percentuale(occupazione)}
            </div>

            <div class="lem-kpi-delta">
                <strong style="color: {colore_occ} !important;">
                    {formatta_punti(delta_occupazione)}
                </strong>
                rispetto al 2024
            </div>
        </div>

        <div class="lem-kpi">
            <div class="lem-kpi-label">
                Tasso di disoccupazione
            </div>

            <div class="lem-kpi-value">
                {formatta_percentuale(disoccupazione)}
            </div>

            <div class="lem-kpi-delta">
                <strong style="color: {colore_dis} !important;">
                    {formatta_punti(delta_disoccupazione)}
                </strong>
                rispetto al 2024
            </div>
        </div>

        <div class="lem-kpi">
            <div class="lem-kpi-label">
                Tasso di inattività
            </div>

            <div class="lem-kpi-value">
                {formatta_percentuale(inattivita)}
            </div>

            <div class="lem-kpi-delta">
                <strong style="color: {colore_ina} !important;">
                    {formatta_punti(delta_inattivita)}
                </strong>
                rispetto al 2024
            </div>
        </div>

    </div>
    """)

    st.caption(
        "Fonte: ISTAT, Rilevazione sulle forze di lavoro. "
        "Tassi riferiti alla fascia 15–64 anni. "
        "Variazioni espresse in punti percentuali."
    )

    # ========================================================
    # 01 / EVOLUZIONE DEL MERCATO DEL LAVORO
    # ========================================================

    st.html("""
    <div class="lem-section">
        <h2>01 / Evoluzione del mercato del lavoro</h2>
        <span>Serie storiche · 2019–2025</span>
    </div>
    """)


    indicatore_temporale = st.segmented_control(
        "Secondo indicatore temporale",
        options=["Disoccupazione", "Inattività"],
        default="Disoccupazione",
        required=True,
        selection_mode="single",
        key="indicatore_temporale_lavoro"
    )

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        with st.container(border=True, key="lem_chart_lavoro_1"):

            st.markdown("**Evoluzione del tasso di occupazione**")
            st.caption(f"{territorio} · 2019–2025")

            fig = crea_grafico_occupazione(
                storico,
                territorio
            )

            st.plotly_chart(
                fig,
                width="stretch",
                theme=None,
                config={"displayModeBar": False}
            )

            st.caption(
                "Tasso di occupazione della popolazione "
                "tra 15 e 64 anni. Valori annuali."
            )


    with col2:
        with st.container(border=True, key="lem_chart_lavoro_2"):

            st.markdown(
                f"**Evoluzione del tasso di "
                f"{indicatore_temporale.lower()}**"
            )

            st.caption(f"{territorio} · 2019–2025")

            if indicatore_temporale == "Disoccupazione":
                fig_secondo = crea_grafico_disoccupazione(
                    storico, territorio
                )
            else:
                fig_secondo = crea_grafico_inattivita(
                    storico, territorio
                )

            st.plotly_chart(
                fig_secondo,
                width="stretch",
                theme=None,
                config={"displayModeBar": False}
            )

            st.caption(
                f"Tasso di {indicatore_temporale.lower()} "
                "della popolazione tra 15 e 64 anni. "
                "Valori annuali."
            )


    # ========================================================
    # 02 / DIFFERENZE TERRITORIALI E DI GENERE
    # ========================================================

    st.html("""
    <div class="lem-section">
        <h2>02 / Differenze territoriali e di genere</h2>
        <span>Confronto provinciale e per sesso</span>
    </div>
    """)

    col3, col4 = st.columns(2, gap="medium")

    with col3:
        with st.container(border=True, key="lem_chart_lavoro_3"):

            st.markdown("**Evoluzione dell'occupazione per provincia**")
            st.caption("Variazione 2019–2025 · punti percentuali")

            fig_province = crea_grafico_province_lavoro(
                dati,
                territorio
            )

            st.plotly_chart(
                fig_province,
                width="stretch",
                theme=None,
                config={"displayModeBar": False}
            )

            st.caption(
                "Variazione del tasso di occupazione "
                "15–64 anni nelle quattro province liguri."
            )

    with col4:
        with st.container(border=True, key="lem_chart_lavoro_4"):

            st.markdown("**Occupazione maschile e femminile**")
            st.caption(f"{territorio} · 2025 · età 15–64 anni")

            dati_sesso = carica_mercato_lavoro_sesso()

            fig_genere = crea_grafico_genere_lavoro(
                dati_sesso,
                territorio
            )

            st.plotly_chart(
                fig_genere,
                width="stretch",
                theme=None,
                config={"displayModeBar": False}
            )

            st.caption(
                "Tassi di occupazione distinti per sesso. "
                "Fonte: ISTAT, Rilevazione sulle forze di lavoro."
            )


    # ========================================================
    # INTERPRETAZIONE AUTOMATICA DEI DATI
    # ========================================================

    dati_2019 = storico.loc[
        storico["Anno"] == 2019
    ].iloc[0]

    # Variazioni tra 2019 e 2025, in punti percentuali
    variazione_occ = (
        occupazione - dati_2019["Tasso occupazione"]
    )

    variazione_dis = (
        disoccupazione - dati_2019["Tasso disoccupazione"]
    )

    variazione_ina = (
        inattivita - dati_2019["Tasso inattivita"]
    )

    # Tassi di occupazione per sesso nel 2025
    dati_sesso = carica_mercato_lavoro_sesso()

    genere_2025 = dati_sesso[
        (dati_sesso["Territorio"] == territorio)
        & (dati_sesso["Anno"] == 2025)
    ]

    genere_2025 = genere_2025.set_index("Sesso")

    occupazione_uomini = float(
        genere_2025.loc["Maschi", "Tasso occupazione"]
    )

    occupazione_donne = float(
        genere_2025.loc["Femmine", "Tasso occupazione"]
    )

    divario = occupazione_uomini - occupazione_donne

    # Descrizione territoriale
    luogo = (
        "in Liguria"
        if territorio == "Liguria"
        else f"nella provincia di {territorio}"
    )

    # Riquadro interpretativo
    st.html(f"""
    <div class="lem-insight">

        <h3>Cosa raccontano i dati</h3>

        <p>
            Tra il 2019 e il 2025, {luogo},
            il tasso di occupazione ha registrato
            una variazione di
            <strong>{formatta_punti_estesi(variazione_occ)}</strong>,
            mentre quello di disoccupazione
            è variato di
            <strong>{formatta_punti_estesi(variazione_dis)}</strong>.
            Il tasso di inattività è cambiato di
            <strong>{formatta_punti_estesi(variazione_ina)}</strong>.
        </p>

        <p>
            Nel 2025 il tasso di occupazione maschile
            è pari al
            <strong>{formatta_percentuale(occupazione_uomini)}</strong>,
            contro il
            <strong>{formatta_percentuale(occupazione_donne)}</strong>
            di quello femminile.
            Il divario a favore degli uomini è di
            <strong>{formatta_punti_estesi(divario)}</strong>.
        </p>

        <p>
            Occupazione, disoccupazione e inattività
            devono essere interpretate congiuntamente:
            un tasso di disoccupazione contenuto
            non implica necessariamente
            un'elevata partecipazione al mercato del lavoro.
        </p>

    </div>
    """)

    # ========================================================
    # FOOTER E NOTE METODOLOGICHE
    # ========================================================

    st.html("""
    <div class="lem-footer">

        <div>
            Liguria Economic Monitor · Modulo Mercato del lavoro
        </div>

        <div>
            Fonte: ISTAT, Rilevazione sulle forze di lavoro.
        </div>

        <div>
            Elaborazioni statistiche su dati annuali 2019–2025.
            I tassi si riferiscono alla fascia 15–64 anni.
            Le variazioni sono espresse in punti percentuali.
            I valori derivano da stime campionarie.
        </div>

    </div>
    """)
