# Liguria Economic Monitor

**Osservatorio economico-statistico interattivo della Liguria**

Un progetto personale di analisi, elaborazione e visualizzazione di dati territoriali, sviluppato con Python, Pandas, Plotly e Streamlit.

**[Accedi alla dashboard interattiva](https://liguria-economic-monitor.streamlit.app/)**

## Il progetto

Liguria Economic Monitor nasce con l'obiettivo di rendere accessibili e interpretabili i principali fenomeni demografici ed economici della Liguria attraverso dati provenienti da fonti statistiche ufficiali.

Il progetto integra diverse basi di dati, sviluppa indicatori statistici e presenta i risultati attraverso una dashboard interattiva, consentendo confronti temporali e territoriali tra la regione e le quattro province liguri: Genova, Imperia, Savona e La Spezia.

Le analisi coprono prevalentemente il periodo **2019–2025**.

## Ambiti di analisi

### Demografia

Analisi della popolazione residente e delle trasformazioni demografiche del territorio.

- Evoluzione della popolazione residente dal 2019 al 2025.
- Variazioni demografiche regionali e provinciali.
- Struttura della popolazione per età e sesso.
- Indice di vecchiaia e incidenza della popolazione anziana.
- Piramide demografica riferita al 2025.

### Tessuto imprenditoriale

Studio dell'evoluzione e della composizione del sistema imprenditoriale ligure attraverso i dati Unioncamere–InfoCamere, Movimprese.

- Evoluzione delle imprese attive e registrate.
- Saldo tra iscrizioni e cessazioni non d'ufficio.
- Confronti territoriali tra le province.
- Distribuzione delle imprese attive per settore economico.
- Individuazione dei settori con le maggiori crescite e contrazioni tra il 2019 e il 2025.

### Mercato del lavoro

Analisi dei principali indicatori del mercato del lavoro attraverso i dati ISTAT.

- Evoluzione dei tassi di occupazione, disoccupazione e inattività.
- Variazioni temporali espresse in punti percentuali.
- Confronto tra le quattro province liguri.
- Analisi dei differenziali occupazionali tra uomini e donne.

Gli indicatori utilizzati si riferiscono alla fascia di età **15–64 anni**.

### Turismo

Studio dei flussi turistici e della stagionalità delle presenze sul territorio ligure.

- Evoluzione annuale di arrivi e presenze.
- Permanenza media dei turisti.
- Distribuzione dei flussi tra province e tipologie ricettive.
- Provenienza dei turisti in base alla residenza in Italia o all'estero.
- Analisi mensile della stagionalità turistica.
- Concentrazione delle presenze nel periodo estivo.

## Fonti statistiche

Il progetto utilizza dati provenienti da fonti ufficiali:

- **ISTAT** — popolazione residente, struttura demografica, Rilevazione sulle forze di lavoro e movimento dei clienti negli esercizi ricettivi.
- **Unioncamere–InfoCamere, Movimprese** — consistenza e dinamica delle imprese.

I dati sono stati raccolti, organizzati ed elaborati per ottenere serie storiche territoriali e indicatori confrontabili.

Le elaborazioni e le visualizzazioni sono realizzate autonomamente nell'ambito del progetto.

## Metodologia e avvertenze

Le analisi adottano criteri coerenti con la natura dei diversi indicatori.

Per la demografia vengono confrontati gli stock di popolazione residente al 1° gennaio dei rispettivi anni.

Per il tessuto imprenditoriale, le variazioni dello stock delle imprese attive sono distinte dal saldo tra iscrizioni e cessazioni. Le distribuzioni settoriali escludono le imprese non classificate.

Per il mercato del lavoro, le differenze tra tassi sono espresse in punti percentuali. Gli indicatori derivano da stime campionarie.

**Discontinuità statistica del turismo nel 2025:** dal 2025 la copertura statistica degli alloggi in affitto include anche strutture gestite in forma non imprenditoriale. Questo cambiamento introduce una discontinuità che richiede cautela nei confronti temporali con gli anni precedenti.

Per questa ragione, nei grafici storici interessati il dato del 2025 viene rappresentato separatamente dalla serie 2019–2024.

Inoltre, l'interpretazione delle dinamiche turistiche del 2020 e del 2021 deve considerare gli effetti della pandemia e delle restrizioni agli spostamenti.

## Tecnologie utilizzate

| Tecnologia | Utilizzo |
|---|---|
| Python | Elaborazione dei dati e sviluppo dell'applicazione |
| Pandas | Pulizia, aggregazione e analisi dei dataset |
| Plotly | Realizzazione di grafici interattivi |
| Streamlit | Sviluppo della dashboard e dei filtri |
| Git e GitHub | Versionamento e pubblicazione del codice |
| Streamlit Community Cloud | Distribuzione online dell'applicazione |

## Struttura del progetto

La repository è organizzata nelle seguenti cartelle:

- `dashboard/` — applicazione Streamlit, moduli tematici, foglio di stile e risorse grafiche.
- `data/processed/` — dataset elaborati utilizzati dalla dashboard.
- `scripts/` — script Python per la preparazione e l'analisi dei dati.
- `.streamlit/` — configurazione dell'applicazione.
- `requirements.txt` — dipendenze Python necessarie all'esecuzione.

I dati sorgente originali, conservati localmente in `data/raw/`, non sono inclusi nel repository. I dati elaborati necessari al funzionamento della dashboard sono invece disponibili in `data/processed/`.

## Esecuzione in locale

Per eseguire la dashboard sul proprio computer:

1. Clonare il repository GitHub.
2. Installare le dipendenze con `pip install -r requirements.txt`.
3. Avviare l'applicazione dalla cartella principale del progetto con `streamlit run dashboard/app.py`.

La dashboard sarà disponibile all'indirizzo locale indicato da Streamlit.

## Obiettivi e competenze

Liguria Economic Monitor è stato sviluppato come progetto personale per applicare competenze statistiche e informatiche a un caso concreto di analisi territoriale.

Il lavoro comprende l'acquisizione e l'organizzazione di dati da fonti differenti, il controllo della loro coerenza, la costruzione di indicatori, l'analisi di serie storiche e la progettazione di visualizzazioni interattive.

L'obiettivo è trasformare dati statistici complessi in informazioni comprensibili, mantenendo attenzione alla qualità dei dati, alla correttezza metodologica e alla chiarezza comunicativa.

## Autore

**Giovanni Giacomo Cerasoli**

Laureato magistrale in Scienze Statistiche ed Economiche.

[Profilo LinkedIn](https://www.linkedin.com/in/giovanni-giacomo-cerasoli-072900223/)

[Dashboard Liguria Economic Monitor](https://liguria-economic-monitor.streamlit.app/)

*Progetto personale indipendente, non affiliato agli enti produttori dei dati utilizzati.*