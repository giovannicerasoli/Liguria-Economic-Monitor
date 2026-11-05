from pathlib import Path
import pandas as pd
import plotly.express as px

# Individuiamo il dataset elaborato
cartella_progetto = Path(__file__).resolve().parent.parent
percorso_file = cartella_progetto / "data" / "processed" / "liguria_popolazione_2025.csv"

# Carichiamo il dataset
liguria = pd.read_csv(
    percorso_file,
    sep=";",
    encoding="utf-8-sig",
    dtype={"Codice comune": str}
)

# Selezioniamo le righe con il totale di ogni comune
totali_comunali = liguria[liguria["Età"] == 999].copy()

# Controlliamo il numero di comuni
print("Comuni individuati:", len(totali_comunali))
print("Comuni distinti:", totali_comunali["Codice comune"].nunique())

# Calcoliamo la popolazione per provincia
popolazione_province = (
    totali_comunali
    .groupby("Provincia")[["Totale maschi", "Totale femmine", "Totale"]]
    .sum()
)

# Verifichiamo la coerenza dei totali
controllo = (
    popolazione_province["Totale maschi"]
    + popolazione_province["Totale femmine"]
    == popolazione_province["Totale"]
)

print("\nPOPOLAZIONE RESIDENTE PER PROVINCIA:")
print(popolazione_province)

print("\nCONTROLLO COERENZA:")
print(controllo)

print("\nPOPOLAZIONE TOTALE DELLA LIGURIA:")
print(popolazione_province["Totale"].sum())


# Calcoliamo il peso percentuale di ogni provincia
popolazione_province["Quota regionale (%)"] = (
    popolazione_province["Totale"]
    / popolazione_province["Totale"].sum()
    * 100
).round(2)

# Calcoliamo la percentuale di donne per provincia
popolazione_province["Donne (%)"] = (
    popolazione_province["Totale femmine"]
    / popolazione_province["Totale"]
    * 100
).round(2)

# Visualizziamo i nuovi indicatori
print("\nINDICATORI DEMOGRAFICI:")
print(
    popolazione_province[
        ["Totale", "Quota regionale (%)", "Donne (%)"]
    ]
)


# Prepariamo i dati per il grafico
dati_grafico = popolazione_province.reset_index()

# Ordiniamo le province per numero di abitanti
dati_grafico = dati_grafico.sort_values(
    "Totale",
    ascending=False
)

# Prepariamo le etichette con il separatore delle migliaia
dati_grafico["Etichetta"] = dati_grafico["Totale"].apply(
    lambda x: f"{x:,}".replace(",", ".")
)


# Creiamo un grafico orizzontale
fig = px.bar(
    dati_grafico,
    x="Totale",
    y="Provincia",
    orientation="h",
    text="Etichetta",
    color_discrete_sequence=["#236B80"],
    custom_data=["Quota regionale (%)"]
)

# Personalizziamo le barre
fig.update_traces(
    textposition="outside",
    textfont=dict(size=15, color="#243746"),
    marker_line_width=0,
    hovertemplate=(
        "<b>%{y}</b><br>"
        "Residenti: %{x}<br>"
        "Quota regionale: %{customdata[0]:.2f}%"
        "<extra></extra>"
    )
)

# Impostiamo un design moderno
fig.update_layout(
    title=dict(
        text="La popolazione della Liguria",
        font=dict(size=25, color="#172B3A"),
        x=0.03
    ),
    font=dict(family="Arial", size=14),
    paper_bgcolor="white",
    plot_bgcolor="white",
    height=480,
    margin=dict(l=120, r=110, t=120, b=80),
    showlegend=False,
    bargap=0.45,
    xaxis=dict(
        visible=False,
        range=[0, dati_grafico["Totale"].max() * 1.2]
    ),
    yaxis=dict(
        title="",
        categoryorder="total ascending",
        tickfont=dict(size=15, color="#243746")
    )
)

# Aggiungiamo una descrizione
fig.add_annotation(
    text="Residenti per provincia · 1° gennaio 2025",
    xref="paper", yref="paper",
    x=0, y=1.12,
    showarrow=False,
    font=dict(size=14, color="#64748B")
)

# Aggiungiamo la fonte
fig.add_annotation(
    text="Fonte: ISTAT | Elaborazione: Liguria Economic Monitor",
    xref="paper", yref="paper",
    x=0, y=-0.15,
    showarrow=False,
    font=dict(size=11, color="#64748B")
)

fig.show(renderer="browser")
