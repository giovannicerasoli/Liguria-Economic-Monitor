from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

# Individuiamo il dataset
progetto = Path(__file__).resolve().parent.parent

file = progetto / "data" / "processed" / "liguria_popolazione_2025.csv"

liguria = pd.read_csv(
    file,
    sep=";",
    encoding="utf-8-sig",
    dtype={"Codice comune": str}
)

# Escludiamo i totali comunali
dati_eta = liguria[liguria["Età"] != 999].copy()

# Sommiamo uomini e donne per singola età
piramide = (
    dati_eta
    .groupby("Età")[["Totale maschi", "Totale femmine"]]
    .sum()
    .reset_index()
    .sort_values("Età")
)

# Calcoliamo la popolazione complessiva per età
piramide["Totale"] = (
    piramide["Totale maschi"]
    + piramide["Totale femmine"]
)

print("PRIME 10 ETÀ:")
print(piramide.head(10).to_string(index=False))

print("\nULTIME 10 ETÀ:")
print(piramide.tail(10).to_string(index=False))

print("\nCONTROLLO TOTALI:")
print("Uomini:", piramide["Totale maschi"].sum())
print("Donne:", piramide["Totale femmine"].sum())
print("Popolazione totale:", piramide["Totale"].sum())

# Salviamo il dataset per la futura dashboard
output = progetto / "data" / "processed" / "popolazione_eta_sesso_2025.csv"

piramide.to_csv(
    output,
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("\nDataset per piramide demografica salvato!")


# Creiamo la piramide demografica
fig = go.Figure()

# Uomini: valori negativi solo per visualizzarli a sinistra
fig.add_trace(go.Bar(
    y=piramide["Età"],
    x=-piramide["Totale maschi"],
    name="Uomini",
    orientation="h",
    marker_color="#287B95",
    customdata=piramide["Totale maschi"],
    hovertemplate=(
        "Età: %{y}<br>"
        "Uomini: %{customdata:,.0f}<extra></extra>"
    )
))

# Donne: valori positivi, visualizzati a destra
fig.add_trace(go.Bar(
    y=piramide["Età"],
    x=piramide["Totale femmine"],
    name="Donne",
    orientation="h",
    marker_color="#BF627E",
    hovertemplate=(
        "Età: %{y}<br>"
        "Donne: %{x:,.0f}<extra></extra>"
    )
))

# Scala simmetrica per uomini e donne
massimo = max(
    piramide["Totale maschi"].max(),
    piramide["Totale femmine"].max()
)

limite = ((int(massimo) + 4999) // 5000) * 5000
tacche = list(range(-limite, limite + 1, 5000))

fig.update_layout(
    title="Struttura per età e sesso della Liguria — 2025",
    barmode="relative",
    template="plotly_white",
    height=850,
    bargap=0.08,
    font=dict(family="Arial", size=13),
    xaxis=dict(
        title="Residenti",
        range=[-limite, limite],
        tickvals=tacche,
        ticktext=[
            f"{abs(v):,}".replace(",", ".")
            for v in tacche
        ],
        showgrid=True,
        gridcolor="#EDF1F5"
    ),
    yaxis=dict(
        title="Età",
        range=[-1, 101],
        dtick=10
    ),
    legend=dict(
        orientation="h",
        x=0.5,
        xanchor="center",
        y=1.05
    ),
    paper_bgcolor="white",
    plot_bgcolor="white"
)

fig.show(renderer="browser")
