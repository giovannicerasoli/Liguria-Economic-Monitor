
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# CONFIGURAZIONE
# ============================================================

RADICE = Path(__file__).resolve().parents[2]
CARTELLA_DATI = RADICE / "data" / "processed"

BLU = "#20394B"
TURCHESE = "#008F9C"
AMBRA = "#E0A13A"
GRIGIO = "#526779"

TERRITORI = ["Liguria", "Genova", "Imperia", "Savona", "La Spezia"]


def intero(valore):
    return f"{int(valore):,}".replace(",", ".")


def decimale(valore):
    return f"{valore:.2f}".replace(".", ",")


def percentuale(valore):
    return f"{valore:+.2f}".replace(".", ",") + "%"




@st.cache_data
def carica_dati_turismo():
    indicatori = pd.read_csv(
        CARTELLA_DATI / "indicatori_turismo_2019_2025.csv",
        encoding="utf-8-sig"
    )

    dettaglio = pd.read_csv(
        CARTELLA_DATI / "turismo_movimento_annuale_2019_2025.csv",
        encoding="utf-8-sig"
    )

    provenienza = pd.read_csv(
        CARTELLA_DATI / "turismo_provenienza_2019_2025.csv",
        encoding="utf-8-sig"
    )

    stagionalita = pd.read_csv(
        CARTELLA_DATI / "turismo_stagionalita_2019_2025.csv",
        encoding="utf-8-sig"
    )

    return indicatori, dettaglio, provenienza, stagionalita




def grafico_storico(dati, indicatore):
    fig = go.Figure()

    confrontabili = dati[dati["Anno"] <= 2024]
    anno_2025 = dati[dati["Anno"] == 2025]

    fig.add_trace(go.Scatter(
        x=confrontabili["Anno"],
        y=confrontabili[indicatore],
        mode="lines+markers",
        name="2019-2024",
        line=dict(color=TURCHESE, width=3),
        marker=dict(
            size=8,
            color="white",
            line=dict(color=TURCHESE, width=2)
        ),
        hovertemplate=(
            "Anno %{x}<br>"
            + indicatore + ": %{y:,.0f}"
            + "<extra></extra>"
        )
    ))

    # Punto separato: il 2025 non è direttamente
    # confrontabile con la serie precedente.
    fig.add_trace(go.Scatter(
        x=anno_2025["Anno"],
        y=anno_2025[indicatore],
        mode="markers",
        name="2025 - discontinuità",
        marker=dict(
            size=12,
            color=AMBRA,
            line=dict(color=BLU, width=1)
        ),
        hovertemplate=(
            "Anno %{x} - discontinuità statistica<br>"
            + indicatore + ": %{y:,.0f}"
            + "<extra></extra>"
        )
    ))

    fig.update_layout(
        height=320,
        margin=dict(l=15, r=15, t=20, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=BLU, size=12),
        showlegend=False,
        hovermode="closest"
    )

    fig.update_xaxes(
        tickvals=list(range(2019, 2026)),
        showgrid=False,
        zeroline=False
    )

    fig.update_yaxes(
        rangemode="tozero",
        tickformat="~s",
        gridcolor="#E5EBEF",
        zeroline=False
    )

    return fig


def grafico_province(indicatori, territorio):
    province = indicatori[
        (indicatori["Anno"] == 2025)
        & (indicatori["Territorio"] != "Liguria")
    ].sort_values("Presenze", ascending=False)

    colori = [
        AMBRA if nome == territorio and territorio != "Liguria"
        else TURCHESE
        for nome in province["Territorio"]
    ]

    fig = go.Figure(go.Bar(
        x=province["Territorio"],
        y=province["Presenze"],
        marker_color=colori,
        text=[intero(v) for v in province["Presenze"]],
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{x}<br>%{y:,.0f} presenze<extra></extra>"
    ))

    fig.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=35, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=BLU, size=12),
        showlegend=False
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#E5EBEF",
        rangemode="tozero",
        tickformat="~s"
    )

    return fig


def grafico_tipologie(dettaglio, territorio):
    tipi = dettaglio[
        (dettaglio["Territorio"] == territorio)
        & (dettaglio["Anno"] == 2025)
        & (
            dettaglio["Codice tipologia"].isin(
                ["HOTELLIKE", "OTHER"]
            )
        )
    ].copy()

    ordine = {"HOTELLIKE": 0, "OTHER": 1}
    tipi["_ordine"] = tipi["Codice tipologia"].map(ordine)
    tipi = tipi.sort_values("_ordine")

    totale = tipi["Presenze"].sum()

    etichette = [
        "Alberghieri" if codice == "HOTELLIKE"
        else "Extralberghieri"
        for codice in tipi["Codice tipologia"]
    ]

    quote = tipi["Presenze"] / totale * 100

    fig = go.Figure(go.Bar(
        x=etichette,
        y=tipi["Presenze"],
        marker_color=[BLU, TURCHESE],
        text=[
            f"{q:.1f}%".replace(".", ",")
            for q in quote
        ],
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{x}<br>%{y:,.0f} presenze<extra></extra>"
    ))

    fig.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=35, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=BLU, size=12),
        showlegend=False
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#E5EBEF",
        rangemode="tozero",
        tickformat="~s"
    )

    return fig


# ============================================================
# MODULO TURISMO
# ============================================================


def grafico_quota_arrivi_esteri(dati):
    dati = dati.sort_values("Anno")

    storica = dati[dati["Anno"] <= 2024]
    anno_2025 = dati[dati["Anno"] == 2025]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=storica["Anno"],
        y=storica["Quota arrivi esteri (%)"],
        mode="lines+markers",
        line=dict(color=TURCHESE, width=3),
        marker=dict(
            size=9,
            color="white",
            line=dict(color=TURCHESE, width=2)
        ),
        name="2019–2024",
        hovertemplate=(
            "%{x}<br>"
            "Arrivi esteri: %{y:.2f}%"
            "<extra></extra>"
        )
    ))

    fig.add_trace(go.Scatter(
        x=anno_2025["Anno"],
        y=anno_2025["Quota arrivi esteri (%)"],
        mode="markers",
        marker=dict(
            size=13,
            color=AMBRA,
            line=dict(color=BLU, width=1)
        ),
        name="2025 - discontinuità",
        hovertemplate=(
            "%{x} - discontinuità statistica<br>"
            "Arrivi esteri: %{y:.2f}%"
            "<extra></extra>"
        )
    ))

    fig.update_layout(
        height=320,
        margin=dict(l=15, r=15, t=20, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=BLU, size=12),
        showlegend=False
    )

    fig.update_xaxes(
        tickvals=list(range(2019, 2026)),
        showgrid=False
    )

    fig.update_yaxes(
        range=[0, 100],
        ticksuffix="%",
        gridcolor="#E5EBEF",
        zeroline=False
    )

    return fig


def grafico_provenienza_province(provenienza, territorio):

    dati = provenienza[
        (provenienza["Anno"] == 2024)
        & (provenienza["Territorio"] != "Liguria")
    ].copy()

    dati = dati.sort_values(
        "Quota arrivi esteri (%)",
        ascending=True
    )

    colori = [
        AMBRA if nome == territorio else TURCHESE
        for nome in dati["Territorio"]
    ]

    etichette = [
        f"{valore:.2f}%".replace(".", ",")
        for valore in dati["Quota arrivi esteri (%)"]
    ]

    fig = go.Figure(go.Bar(
        x=dati["Quota arrivi esteri (%)"],
        y=dati["Territorio"],
        orientation="h",
        marker_color=colori,
        text=etichette,
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "%{y}<br>"
            "Quota arrivi esteri: %{x:.2f}%"
            "<extra></extra>"
        )
    ))

    fig.update_layout(
        height=320,
        margin=dict(l=15, r=35, t=20, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=BLU, size=12),
        showlegend=False,
        bargap=0.40
    )

    fig.update_xaxes(
        range=[0, 100],
        ticksuffix="%",
        gridcolor="#E5EBEF",
        zeroline=False
    )

    fig.update_yaxes(
        showgrid=False,
        automargin=True
    )

    return fig

def grafico_stagionalita_mensile(stagionalita, territorio, anno):

    dati = stagionalita[
        (stagionalita["Anno"] == anno)
        & (stagionalita["Territorio"] == territorio)
    ].sort_values("Mese")

    massimo = dati["Presenze"].max()

    colori = [
        AMBRA if valore == massimo else TURCHESE
        for valore in dati["Presenze"]
    ]

    fig = go.Figure(go.Bar(
        x=dati["Mese"],
        y=dati["Presenze"],
        marker_color=colori,
        customdata=dati["Nome mese"],
        hovertemplate=(
            "%{customdata}<br>"
            "Presenze: %{y:,.0f}"
            "<extra></extra>"
        )
    ))

    fig.update_layout(
        height=340,
        margin=dict(l=15, r=15, t=20, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=BLU, size=12),
        showlegend=False,
        bargap=0.25
    )

    fig.update_xaxes(
        tickvals=list(range(1, 13)),
        ticktext=[
            "Gen", "Feb", "Mar", "Apr",
            "Mag", "Giu", "Lug", "Ago",
            "Set", "Ott", "Nov", "Dic"
        ],
        showgrid=False
    )

    fig.update_yaxes(
        tickformat="~s",
        gridcolor="#E5EBEF",
        rangemode="tozero",
        zeroline=False
    )

    return fig


def grafico_confronto_stagionalita(stagionalita, territorio, anno):

    province = ["Genova", "Imperia", "Savona", "La Spezia"]

    colori = {
        "Genova": "#4C78A8",
        "Imperia": "#8B70B5",
        "Savona": "#008F9C",
        "La Spezia": "#D9A441"
    }

    dati = stagionalita[
        (stagionalita["Anno"] == anno)
        & (stagionalita["Territorio"].isin(province))
    ].copy()

    fig = go.Figure()

    for provincia in province:

        serie = dati[
            dati["Territorio"] == provincia
        ].sort_values("Mese")

        evidenziata = provincia == territorio

        fig.add_trace(go.Scatter(
            x=serie["Mese"],
            y=serie["Quota presenze annuali (%)"],
            customdata=serie["Nome mese"],
            mode="lines+markers",
            name=provincia,
            line=dict(
                color=colori[provincia],
                width=4 if evidenziata else 2.5
            ),
            marker=dict(
                size=8 if evidenziata else 6
            ),
            hovertemplate=(
                "%{customdata}<br>"
                "Quota presenze: %{y:.2f}%"
                "<extra>%{fullData.name}</extra>"
            )
        ))

    fig.update_layout(
        height=340,
        margin=dict(l=15, r=15, t=15, b=65),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=BLU, size=12),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="center",
            x=0.5,
            font=dict(size=11)
        )
    )

    fig.update_xaxes(
        tickvals=list(range(1, 13)),
        ticktext=[
            "Gen", "Feb", "Mar", "Apr",
            "Mag", "Giu", "Lug", "Ago",
            "Set", "Ott", "Nov", "Dic"
        ],
        showgrid=False
    )

    fig.update_yaxes(
        ticksuffix="%",
        rangemode="tozero",
        gridcolor="#E5EBEF",
        zeroline=False
    )

    return fig


def grafico_concentrazione_estiva(stagionalita, territorio):

    territori = (
        ["Liguria"]
        if territorio == "Liguria"
        else [territorio, "Liguria"]
    )

    dati = stagionalita[
        stagionalita["Territorio"].isin(territori)
    ].copy()

    # Presenze dei mesi di giugno, luglio e agosto.
    dati["Presenze estive"] = dati["Presenze"].where(
        dati["Mese"].isin([6, 7, 8]),
        0
    )

    riepilogo = (
        dati.groupby(
            ["Territorio", "Anno"],
            as_index=False
        )
        .agg(
            presenze_annue=("Presenze", "sum"),
            presenze_estive=("Presenze estive", "sum")
        )
    )

    riepilogo["Quota estiva (%)"] = (
        riepilogo["presenze_estive"]
        / riepilogo["presenze_annue"]
        * 100
    ).round(2)

    fig = go.Figure()

    for indice, nome in enumerate(territori):

        serie = riepilogo[
            riepilogo["Territorio"] == nome
        ].sort_values("Anno")

        storica = serie[serie["Anno"] <= 2024]
        anno_2025 = serie[serie["Anno"] == 2025]

        colore = TURCHESE if nome == territorio else BLU

        fig.add_trace(go.Scatter(
            x=storica["Anno"],
            y=storica["Quota estiva (%)"],
            mode="lines+markers",
            name=(
                nome if nome == territorio
                else "Liguria (riferimento)"
            ),
            line=dict(
                color=colore,
                width=3 if nome == territorio else 2,
                dash="solid" if nome == territorio else "dash"
            ),
            marker=dict(
                size=8,
                color="white",
                line=dict(color=colore, width=2)
            ),
            hovertemplate=(
                "Anno %{x}<br>"
                "Presenze estive: %{y:.2f}%"
                "<extra>" + nome + "</extra>"
            )
        ))

        # Il 2025 non viene collegato alla serie storica.
        fig.add_trace(go.Scatter(
            x=anno_2025["Anno"],
            y=anno_2025["Quota estiva (%)"],
            mode="markers",
            name="2025 - discontinuità",
            showlegend=(indice == 0),
            marker=dict(
                size=13,
                color=AMBRA,
                symbol="circle" if indice == 0 else "diamond",
                line=dict(color=colore, width=2)
            ),
            hovertemplate=(
                "Anno 2025 - discontinuità<br>"
                "Presenze estive: %{y:.2f}%"
                "<extra>" + nome + "</extra>"
            )
        ))

    fig.update_layout(
        height=360,
        margin=dict(l=20, r=20, t=25, b=75),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=BLU, size=12),
        hovermode="closest",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.20,
            xanchor="center",
            x=0.5,
            font=dict(size=11)
        )
    )

    fig.update_xaxes(
        tickvals=list(range(2019, 2026)),
        showgrid=False,
        zeroline=False
    )

    fig.update_yaxes(
        ticksuffix="%",
        rangemode="tozero",
        gridcolor="#E5EBEF",
        zeroline=False
    )

    return fig


def mostra_turismo(territorio="Liguria"):

    if territorio not in TERRITORI:
        territorio = "Liguria"

    indicatori, dettaglio, provenienza, stagionalita = carica_dati_turismo()

    serie = indicatori[
        indicatori["Territorio"] == territorio
    ].sort_values("Anno")

    dati_2025 = serie[serie["Anno"] == 2025].iloc[0]
    dati_2019 = serie[serie["Anno"] == 2019].iloc[0]
    dati_2024 = serie[serie["Anno"] == 2024].iloc[0]

    arrivi = int(dati_2025["Arrivi"])
    presenze = int(dati_2025["Presenze"])
    permanenza = float(dati_2025["Permanenza media"])

    # ========================================================
    # INTESTAZIONE
    # ========================================================

    titolo_turismo = (
        "Il turismo in Liguria"
        if territorio == "Liguria"
        else f"Il turismo — {territorio}"
    )

    st.html(f"""
    <div class="lem-header">
        <div class="lem-brand">
            LIGURIA ECONOMIC MONITOR / TURISMO
        </div>
        <h1>{titolo_turismo}</h1>
        <p>
            Arrivi, presenze e strutture ricettive
            &middot; 2019–2025
        </p>
    </div>
    """)

    # ========================================================
    # KPI
    # ========================================================

    st.html("""
    <div class="lem-section">
        <h2>Il turismo in numeri</h2>
        <span>Anno 2025</span>
    </div>
    """)

    st.html(f"""
    <div class="lem-kpis">

        <div class="lem-kpi">
            <div class="lem-kpi-label">
                Arrivi turistici
            </div>
            <div class="lem-kpi-value">
                {intero(arrivi)}
            </div>
            <div class="lem-kpi-delta">
                Clienti arrivati nelle strutture ricettive
            </div>
        </div>

        <div class="lem-kpi">
            <div class="lem-kpi-label">
                Presenze turistiche
            </div>
            <div class="lem-kpi-value">
                {intero(presenze)}
            </div>
            <div class="lem-kpi-delta">
                Pernottamenti registrati
            </div>
        </div>

        <div class="lem-kpi">
            <div class="lem-kpi-label">
                Permanenza media
            </div>
            <div class="lem-kpi-value">
                {decimale(permanenza)}
            </div>
            <div class="lem-kpi-delta">
                Notti per arrivo
            </div>
        </div>

    </div>
    """)

    # ========================================================
    # PRIMA RIGA: SERIE STORICHE
    # ========================================================

    st.html("""
    <div class="lem-section">
        <h2>01 / Evoluzione del turismo</h2>
        <span>2019–2025</span>
    </div>
    """)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        with st.container(border=True, key="lem_chart_turismo_1"):
            st.markdown("**Evoluzione degli arrivi**")
            st.plotly_chart(
                grafico_storico(serie, "Arrivi"),
                use_container_width=True,
                config={"displayModeBar": False}
            )

    with col2:
        with st.container(border=True, key="lem_chart_turismo_2"):
            st.markdown("**Evoluzione delle presenze**")
            st.plotly_chart(
                grafico_storico(serie, "Presenze"),
                use_container_width=True,
                config={"displayModeBar": False}
            )

    st.caption(
        "Il punto ambra identifica il 2025, rappresentato "
        "separatamente a causa della discontinuità statistica "
        "negli alloggi in affitto."
    )

    # ========================================================
    # SECONDA RIGA: TERRITORI E RICETTIVITÀ
    # ========================================================

    st.html("""
    <div class="lem-section">
        <h2>02 / Distribuzione del turismo</h2>
        <span>Anno 2025</span>
    </div>
    """)

    col3, col4 = st.columns(2, gap="medium")

    with col3:
        with st.container(border=True, key="lem_chart_turismo_3"):
            st.markdown("**Presenze nelle province liguri**")
            st.plotly_chart(
                grafico_province(indicatori, territorio),
                use_container_width=True,
                config={"displayModeBar": False}
            )

    with col4:
        with st.container(border=True, key="lem_chart_turismo_4"):
            st.markdown("**Presenze per tipologia ricettiva**")
            st.plotly_chart(
                grafico_tipologie(dettaglio, territorio),
                use_container_width=True,
                config={"displayModeBar": False}
            )


    # ========================================================
    # PROVENIENZA DEI TURISTI
    # ========================================================

    st.html("""
    <div class="lem-section">
        <h2>03 / Provenienza dei turisti</h2>
        <span>2019–2025</span>
    </div>
    """)

    dati_provenienza = provenienza[
        provenienza["Territorio"] == territorio
    ].copy()


    col5, col6 = st.columns(2, gap="medium")

    with col5:
        with st.container(border=True, key="lem_chart_turismo_5"):
            st.markdown(
                "**Evoluzione della quota di arrivi esteri**"
            )

            st.plotly_chart(
                grafico_quota_arrivi_esteri(dati_provenienza),
                use_container_width=True,
                config={"displayModeBar": False}
            )

    with col6:
        with st.container(border=True, key="lem_chart_turismo_6"):
            st.markdown(
                "**Arrivi esteri per provincia — 2024**"
            )

            st.plotly_chart(
                grafico_provenienza_province(
                    provenienza,
                    territorio
                ),
                use_container_width=True,
                config={"displayModeBar": False}
            )


    st.caption(
        "La provenienza è determinata dalla residenza "
        "dei clienti, non dalla cittadinanza. "
        "Il dato 2025 è mostrato separatamente "
        "per la discontinuità statistica."
    )


    # ========================================================
    # ANALISI AUTOMATICA
    # ========================================================

    var_arrivi = (
        dati_2024["Arrivi"] / dati_2019["Arrivi"] - 1
    ) * 100

    var_presenze = (
        dati_2024["Presenze"] / dati_2019["Presenze"] - 1
    ) * 100



    frase_arrivi = (
        f"una crescita del {decimale(var_arrivi)}%"
        if var_arrivi > 0
        else f"un calo del {decimale(abs(var_arrivi))}%"
        if var_arrivi < 0
        else "una variazione nulla"
    )

    frase_presenze = (
        f"una crescita del {decimale(var_presenze)}%"
        if var_presenze > 0
        else f"un calo del {decimale(abs(var_presenze))}%"
        if var_presenze < 0
        else "una variazione nulla"
    )



    # ========================================================
    # ANALISI DELLA PROVENIENZA DEI TURISTI
    # ========================================================

    quota_estera_2019 = float(
        dati_provenienza.loc[
            dati_provenienza["Anno"] == 2019,
            "Quota arrivi esteri (%)"
        ].iloc[0]
    )

    quota_estera_2024 = float(
        dati_provenienza.loc[
            dati_provenienza["Anno"] == 2024,
            "Quota arrivi esteri (%)"
        ].iloc[0]
    )

    variazione_quota = (
        quota_estera_2024 - quota_estera_2019
    )

    if variazione_quota > 0:
        evoluzione_estera = (
            f"è aumentata di "
            f"{decimale(variazione_quota)} punti percentuali"
        )
    elif variazione_quota < 0:
        evoluzione_estera = (
            f"è diminuita di "
            f"{decimale(abs(variazione_quota))} punti percentuali"
        )
    else:
        evoluzione_estera = "è rimasta invariata"





    # ========================================================
    # STAGIONALITÀ TURISTICA
    # ========================================================

    col_titolo, col_anno = st.columns(
        [4, 1.2],
        gap="medium",
        vertical_alignment="center"
    )

    with col_titolo:
        st.html("""
        <div class="lem-section">
            <h2>04 / Stagionalità turistica</h2>
            <span>Analisi mensile · 2019–2025</span>
        </div>
        """)


    with col_anno:
        anno_stagionalita = st.selectbox(
            "Anno di analisi",
            options=list(range(2019, 2026)),
            index=5,
            key="anno_stagionalita_turismo",
            filter_mode=None,
            accept_new_options=False
        )


    # --------------------------------------------------------
    # DUE GRAFICI MENSILI
    # --------------------------------------------------------

    col7, col8 = st.columns(2, gap="medium")

    with col7:
        with st.container(border=True, key="lem_chart_turismo_7"):
            st.markdown(
                "**Distribuzione mensile delle presenze**"
            )

            st.plotly_chart(
                grafico_stagionalita_mensile(
                    stagionalita,
                    territorio,
                    anno_stagionalita
                ),
                use_container_width=True,
                config={"displayModeBar": False}
            )

    with col8:
        with st.container(border=True, key="lem_chart_turismo_8"):
            st.markdown(
                "**Stagionalità a confronto tra province**"
            )

            st.plotly_chart(
                grafico_confronto_stagionalita(
                    stagionalita,
                    territorio,
                    anno_stagionalita
                ),
                use_container_width=True,
                config={"displayModeBar": False}
            )

    st.caption(
        f"Anno {anno_stagionalita}. "
        "A sinistra, presenze mensili del territorio "
        "selezionato; a destra, distribuzione percentuale "
        "delle presenze annuali nelle quattro province."
    )

    if anno_stagionalita == 2025:
        st.caption(
            "Attenzione: nel 2025 cambia la copertura "
            "statistica degli alloggi in affitto. "
            "Il confronto con gli anni precedenti "
            "richiede cautela."
        )

    # --------------------------------------------------------
    # TERZO GRAFICO: EVOLUZIONE DELLA CONCENTRAZIONE ESTIVA
    # --------------------------------------------------------

    with st.container(border=True, key="lem_chart_turismo_9"):

        st.markdown(
            "**Evoluzione della concentrazione estiva "
            "delle presenze — 2019–2025**"
        )

        st.plotly_chart(
            grafico_concentrazione_estiva(
                stagionalita,
                territorio
            ),
            use_container_width=True,
            config={"displayModeBar": False}
        )


    st.caption(
        "Quota percentuale delle presenze registrate "
        "tra giugno e agosto sul totale annuale. "
        "Quando è selezionata una provincia viene "
        "mostrata anche la Liguria come riferimento. "
        "I dati del 2020 e del 2021 risentono "
        "dell'emergenza pandemica e delle restrizioni "
        "agli spostamenti. "
        "Il 2025 è rappresentato separatamente "
        "per la discontinuità statistica."
    )


    # --------------------------------------------------------
    # CALCOLI PER L'ANALISI AUTOMATICA
    # --------------------------------------------------------

    dati_anno = stagionalita[
        (stagionalita["Anno"] == anno_stagionalita)
        & (stagionalita["Territorio"] == territorio)
    ].copy()

    mese_picco = dati_anno.loc[
        dati_anno["Presenze"].idxmax()
    ]

    presenze_estive = dati_anno.loc[
        dati_anno["Mese"].isin([6, 7, 8]),
        "Presenze"
    ].sum()

    quota_estiva = (
        presenze_estive
        / dati_anno["Presenze"].sum()
        * 100
    )


    luogo_stagionalita = (
        "in Liguria"
        if territorio == "Liguria"
        else f"nella provincia di {territorio}"
    )

    testo_stagionalita = (
        f"Nel {anno_stagionalita}, il mese con il maggior "
        f"numero di presenze {luogo_stagionalita} è "
        f"{mese_picco['Nome mese']}, con "
        f"{intero(mese_picco['Presenze'])} pernottamenti, "
        f"pari al "
        f"{decimale(mese_picco['Quota presenze annuali (%)'])}% "
        f"del totale annuale. "
        f"Tra giugno e agosto si concentra il "
        f"{decimale(quota_estiva)}% delle presenze."
    )


    if anno_stagionalita == 2025:
        testo_stagionalita += (
            " Il dato 2025 risente della discontinuità "
            "statistica negli alloggi in affitto."
        )

    elif anno_stagionalita != 2019:

        dati_2019 = stagionalita[
            (stagionalita["Anno"] == 2019)
            & (stagionalita["Territorio"] == territorio)
        ]

        quota_estiva_2019 = (
            dati_2019.loc[
                dati_2019["Mese"].isin([6, 7, 8]),
                "Presenze"
            ].sum()
            / dati_2019["Presenze"].sum()
            * 100
        )

        differenza = quota_estiva - quota_estiva_2019

        if abs(differenza) < 0.005:
            testo_stagionalita += (
                " La concentrazione estiva è invariata "
                "rispetto al 2019."
            )

        else:
            direzione = (
                "superiore" if differenza > 0
                else "inferiore"
            )

            testo_stagionalita += (
                f" La concentrazione estiva è "
                f"{direzione} di "
                f"{decimale(abs(differenza))} "
                f"punti percentuali rispetto al 2019."
            )




    st.html(f"""
    <div class="lem-insight">
        <h3>Lettura dei dati</h3>

        <p>
            Tra il 2019 e il 2024, {territorio} registra
            {frase_arrivi} degli arrivi e
            {frase_presenze} delle presenze turistiche.
            Nel 2025 si rilevano {intero(arrivi)} arrivi
            e {intero(presenze)} presenze,
            con una permanenza media di
            {decimale(permanenza)} notti.
        </p>

        <p style="margin-top: 12px;">
            Nel 2024, il {decimale(quota_estera_2024)}%
            degli arrivi riguarda clienti residenti
            all'estero. Rispetto al 2019, la quota
            del turismo internazionale
            {evoluzione_estera}.
        </p>

        <p style="margin-top: 12px;">
            {testo_stagionalita}
        </p>

        <p style="margin-top: 12px;">
            Il confronto diretto tra il 2024 e il 2025
            richiede cautela per il cambiamento
            nella rilevazione degli alloggi in affitto.
        </p>
    </div>
    """)


    # ========================================================
    # FONTE E NOTE METODOLOGICHE
    # ========================================================

    st.html("""
    <div class="lem-footer">
        Fonte: ISTAT, Movimento dei clienti negli esercizi
        ricettivi per tipo di esercizio, dati annuali e mensili.
        Elaborazioni Liguria Economic Monitor.

        Gli indicatori di provenienza si riferiscono alla
        residenza dei clienti, non alla cittadinanza.

        Dal 2025 la rilevazione degli alloggi in affitto
        include anche quelli gestiti in forma non
        imprenditoriale, introducendo una discontinuità
        nelle serie degli esercizi extralberghieri e
        nei totali.
    </div>
    """)
