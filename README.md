# pendelweer-data

Elke ochtend haalt GitHub Actions de uurverwachting van 9 weermodellen op voor één punt
(50.95 N, 5.25 O) en zet ze in `data/`: ECMWF, ECMWF-AI, ICON, GFS, AROME, HARMONIE (KNMI en DMI),
UKMO en GEM.

- `data/<model>.csv`: uurwaarden (temperatuur, neerslag, sneeuw, wind, windstoten, dauwpunt)
- `data/daily.csv`: neerslag per dag, zonsopkomst en -ondergang
- `data/meta.json`: tijdstip van ophalen en welke modellen gelukt zijn

Weerdata: [Open-Meteo.com](https://open-meteo.com/), licentie CC BY 4.0.
