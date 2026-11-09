#!/usr/bin/env python3
"""Haalt de uurverwachting van 9 weermodellen op bij Open-Meteo voor een punt tussen
Hasselt en Lummen en schrijft per model een CSV in data/. Draait via GitHub Actions.
Weerdata: Open-Meteo.com, CC BY 4.0."""
import csv, datetime as dt, json, os, sys, time, urllib.parse, urllib.request

LAT, LON = 50.95, 5.25
MODELS = ["ecmwf_ifs025", "ecmwf_aifs025_single", "icon_seamless", "gfs_seamless", "meteofrance_seamless",
          "knmi_seamless", "dmi_seamless", "ukmo_seamless", "gem_seamless"]
HOURLY = ["temperature_2m", "precipitation", "snowfall", "wind_speed_10m", "wind_direction_10m",
          "wind_gusts_10m", "dew_point_2m"]
API = "https://api.open-meteo.com/v1/forecast"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def get(params, tries=3):
    url = API + "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            if i == tries - 1:
                raise
            print(f"poging {i + 1} mislukt: {e}", file=sys.stderr)
            time.sleep(5 * (i + 1))


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def main():
    os.makedirs(OUT, exist_ok=True)
    ok = []
    for m in MODELS:
        try:
            j = get({"latitude": LAT, "longitude": LON, "hourly": ",".join(HOURLY), "models": m,
                     "timezone": "Europe/Brussels", "past_days": 1, "forecast_days": 4})
        except Exception as e:  # noqa: BLE001
            print(f"{m}: mislukt ({e})", file=sys.stderr)
            continue
        h = j.get("hourly") or {}
        times = h.get("time") or []
        if not times or all(v is None for v in h.get("temperature_2m") or [None]):
            print(f"{m}: geen data", file=sys.stderr)
            continue
        cols = [h.get(k) or [None] * len(times) for k in HOURLY]
        write_csv(os.path.join(OUT, f"{m}.csv"), ["time"] + HOURLY,
                  [[t] + ["" if c[i] is None else c[i] for c in cols] for i, t in enumerate(times)])
        ok.append(m)
    d = get({"latitude": LAT, "longitude": LON, "daily": "precipitation_sum,sunrise,sunset",
             "timezone": "Europe/Brussels", "past_days": 3, "forecast_days": 4})["daily"]
    keys = ["time", "precipitation_sum", "sunrise", "sunset"]
    write_csv(os.path.join(OUT, "daily.csv"), keys,
              [["" if d[k][i] is None else d[k][i] for k in keys] for i in range(len(d["time"]))])
    meta = {"fetched_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "lat": LAT, "lon": LON, "models": ok}
    with open(os.path.join(OUT, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)
    print("OK:", ", ".join(ok))
    sys.exit(0 if len(ok) >= 3 else 1)


if __name__ == "__main__":
    main()
