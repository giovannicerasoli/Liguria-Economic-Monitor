"""Punto di ingresso di Liguria Economic Monitor.

Gestisce il tema, la navigazione e il caricamento dei dati. Le analisi
sono definite nei rispettivi moduli.
"""

from pathlib import Path

import pandas as pd
import streamlit as st
import base64
from modules.demografia import mostra_demografia
from modules.economia import mostra_economia
from modules.turismo import mostra_turismo


# Configurazione dell'applicazione
st.set_page_config(
    page_title="Liguria Economic Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PROGETTO = Path(__file__).resolve().parent.parent
DATI = PROGETTO / "data" / "processed"


@st.cache_data
def carica_dati(nome):
    return pd.read_csv(DATI / nome, sep=";", encoding="utf-8-sig")


# Stile condiviso tra tutti i moduli (il file CSS esistente resta invariato)
css = (Path(__file__).resolve().parent / "styles.css").read_text(
    encoding="utf-8"
)
st.html(f"<style>{css}</style>")


# ============================================================
# SFONDO GRAFICO DELLA DASHBOARD
# ============================================================

percorso_sfondo = (
    Path(__file__).resolve().parent
    / "assets"
    / "lem_sfondo_dashboard.png"
)

sfondo_base64 = base64.b64encode(
    percorso_sfondo.read_bytes()
).decode("utf-8")

st.html(f"""
<style>
.stApp {{
    background-color: #E9F3F6 !important;
    background-image:
        url("data:image/png;base64,{sfondo_base64}") !important;
    background-position: center center !important;
    background-size: cover !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}}
</style>
""")


# ============================================================
# BARRA SUPERIORE: BRAND, MODULI E TERRITORIO
# ============================================================

territori = [
    "Liguria",
    "Genova",
    "Imperia",
    "Savona",
    "La Spezia"
]


def segnala_cambio_modulo():
    """Richiede il ritorno in alto solo quando cambia modulo."""
    st.session_state["_lem_torna_in_alto"] = True


with st.container(key="lem_sticky_header"):

    col_brand, col_moduli, col_filtro = st.columns(
        [2.4, 3, 1.5],
        gap="small",
        vertical_alignment="center"
    )

    # SINISTRA: nome dell'osservatorio


    # SINISTRA: logo e nome dell'osservatorio

    with col_brand:

        percorso_logo = (
            Path(__file__).resolve().parent
            / "assets"
            / "lem_logo_header.png"
        )

        col_logo, col_nome = st.columns(
            [1.4, 4],
            gap="small",
            vertical_alignment="center"
        )


        with col_logo:
            logo_base64 = base64.b64encode(
                percorso_logo.read_bytes()
            ).decode("utf-8")

            st.html(
                f'<img src="data:image/png;base64,{logo_base64}" '
                f'alt="Logo Liguria Economic Monitor" '
                f'style="width:115px;height:auto;display:block;">'
            )


        with col_nome:
            st.markdown("### Liguria Economic Monitor")
            st.caption("Osservatorio economico-statistico")




    # CENTRO: navigazione tra i moduli
    with col_moduli:
        modulo = st.segmented_control(
            "Sezione dell'osservatorio",
            options=[
                "Demografia",
                "Economia e imprese",
                "Turismo"
            ],
            default="Demografia",
            selection_mode="single",
            required=True,
            label_visibility="collapsed",
            key="modulo",
            on_change=segnala_cambio_modulo
        )


    # DESTRA: filtro territoriale
    with col_filtro:
        territorio = st.selectbox(
            "Territorio di analisi",
            options=territori,
            index=0,
            key="territorio",
            filter_mode=None,
            accept_new_options=False
        )


# ============================================================
# VISUALIZZAZIONE DEL MODULO SELEZIONATO
# ============================================================


if modulo == "Demografia":
    storico = carica_dati("serie_storica_popolazione_2019_2025.csv")
    invecchiamento = carica_dati("evoluzione_invecchiamento_2019_2025.csv")
    dati_eta = carica_dati("liguria_popolazione_2025.csv")
    mostra_demografia(territorio, storico, invecchiamento, dati_eta)
elif modulo == "Economia e imprese":
    mostra_economia(territorio)
elif modulo == "Turismo":
    mostra_turismo(territorio)


# ============================================================
# RITORNO IN ALTO SOLO QUANDO SI CAMBIA MODULO
# ============================================================

if st.session_state.pop("_lem_torna_in_alto", False):

    st.html(
        """
        <script>
            requestAnimationFrame(() => {

                const pagina = document.querySelector(
                    'section[data-testid="stMain"]'
                );

                if (pagina) {
                    pagina.scrollTo({
                        top: 0,
                        behavior: "auto"
                    });
                } else {
                    window.scrollTo({
                        top: 0,
                        behavior: "auto"
                    });
                }

            });
        </script>
        """,
        unsafe_allow_javascript=True
    )


# ============================================================
# CREDITI DEL PROGETTO - CONDIVISI DA TUTTI I MODULI
# ============================================================


# ============================================================
# BARRA INFERIORE FISSA - CREDITI DEL PROGETTO
# ============================================================

with st.container(key="lem_fixed_footer"):

    st.html("""
    <div class="lem-fixed-footer-content">

        <div class="lem-footer-left">

            
<div class="lem-footer-author">
    <span>
        Un progetto di
        <strong>Giovanni Giacomo Cerasoli</strong>
    </span>

    
<a
    href="https://www.linkedin.com/in/giovanni-giacomo-cerasoli-072900223/"
    target="_blank"
    rel="noopener noreferrer"
    class="lem-footer-linkedin"
    title="Profilo LinkedIn"
    aria-label="Profilo LinkedIn di Giovanni Giacomo Cerasoli"
>
    <span style="
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        background-color: #0A66C2;
        color: #FFFFFF;
        border-radius: 3px;
        font-family: Arial, sans-serif;
        font-size: 15px;
        font-weight: 700;
        line-height: 1;
    ">in</span>
</a>

</div>


            <div class="lem-footer-description">
                Analisi, elaborazione e visualizzazione
                di dati economici e territoriali della Liguria.
            </div>

        </div>

        <div class="lem-footer-sources">
            Fonti statistiche: ISTAT,
            Unioncamere–InfoCamere e altre fonti
            ufficiali indicate nelle rispettive sezioni.
        </div>

    </div>
    """)

