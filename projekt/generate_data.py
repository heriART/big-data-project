"""
generate_data.py — Generátor datových souborů pro EcoHome EDA projekt.

Vytvoří:
  1. data/real_weather.csv        — hodinová meteo data pro Prahu (2023), stažená z Open-Meteo API
  2. data/synthetic_smart_meters.parquet — syntetická data pro 1000 domácností (2023)

Spuštění: python generate_data.py
"""

import subprocess
import importlib.util
import sys
import os
from pathlib import Path

# Fix Windows console encoding for Czech characters
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# === Kontrola a instalace závislostí ===
def ensure(pkg: str, imp: str | None = None) -> None:
    if importlib.util.find_spec(imp or pkg) is None:
        print(f"Instaluji {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

ensure("requests")
ensure("pandas")
ensure("numpy")
ensure("pyarrow")   # potřeba pro Parquet export

import requests
import pandas as pd
import numpy as np

# === Konstanty ===
YEAR = 2023
LAT, LON = 50.0755, 14.4378          # Praha
DATA_DIR = Path("data")
WEATHER_CSV = DATA_DIR / "real_weather.csv"
METERS_PARQUET = DATA_DIR / "synthetic_smart_meters.parquet"
N_HOUSEHOLDS = 1_000
RNG = np.random.default_rng(42)       # reprodukovatelný generátor náhodných čísel

DATA_DIR.mkdir(exist_ok=True)         # vytvoření složky data/ pokud neexistuje


# ╔══════════════════════════════════════════════════════════════╗
# ║  1. POČASÍ — Open-Meteo API (fallback: syntetická data)     ║
# ╚══════════════════════════════════════════════════════════════╝

def fetch_weather_api() -> pd.DataFrame:
    """Stáhne hodinová meteo data z Open-Meteo API pro Prahu za rok 2023."""
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": LAT,
        "longitude": LON,
        "start_date": f"{YEAR}-01-01",
        "end_date": f"{YEAR}-12-31",
        "hourly": "temperature_2m,cloud_cover,precipitation,wind_speed_10m,shortwave_radiation",
        "timezone": "Europe/Prague",
    }
    print("Stahuji počasí z Open-Meteo API...")
    resp = requests.get(url, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()["hourly"]

    df = pd.DataFrame({
        "timestamp":        pd.to_datetime(data["time"]),
        "teplota":          data["temperature_2m"],           # °C
        "oblacnost":        data["cloud_cover"],              # %
        "srazky":           data["precipitation"],            # mm
        "vitr":             data["wind_speed_10m"],           # m/s
        "solarni_iradiace": data["shortwave_radiation"],      # W/m²
    })
    return df


def generate_weather_synthetic() -> pd.DataFrame:
    """Syntetický fallback — generuje realistická hodinová meteo data."""
    print("API selhalo, generuji syntetická meteo data...")
    timestamps = pd.date_range(f"{YEAR}-01-01", f"{YEAR}-12-31 23:00", freq="h", tz="Europe/Prague")
    n = len(timestamps)
    day_of_year = timestamps.dayofyear.values
    hour = timestamps.hour.values

    # Sezónní teplota: sinusoida s denním cyklem + šum
    seasonal = 10 * np.sin(2 * np.pi * (day_of_year - 80) / 365)   # roční cyklus, peak v červenci
    diurnal = 3 * np.sin(2 * np.pi * (hour - 6) / 24)              # denní cyklus
    teplota = seasonal + diurnal + RNG.normal(0, 2, n)

    oblacnost = np.clip(50 + 20 * np.sin(2 * np.pi * day_of_year / 365) + RNG.normal(0, 20, n), 0, 100)
    srazky = np.where(RNG.random(n) < 0.08, RNG.exponential(1.5, n), 0.0)   # 8 % hodin prší
    vitr = np.abs(4 + RNG.normal(0, 2, n))
    solarni_iradiace = np.clip(
        (800 * np.sin(np.pi * np.clip((hour - 5) / 14, 0, 1))     # denní oblouk
         * (1 - oblacnost / 130)                                     # tlumení oblačností
         * (0.6 + 0.4 * np.sin(2 * np.pi * (day_of_year - 80) / 365))  # sezónní modulace
         + RNG.normal(0, 20, n)),
        0, None
    )

    return pd.DataFrame({
        "timestamp":        timestamps.tz_localize(None),
        "teplota":          np.round(teplota, 1),
        "oblacnost":        np.round(oblacnost, 1),
        "srazky":           np.round(srazky, 1),
        "vitr":             np.round(vitr, 1),
        "solarni_iradiace": np.round(solarni_iradiace, 1),
    })


# Stažení dat z API, pokud selže → syntetický fallback
try:
    df_weather = fetch_weather_api()
    print(f"Staženo {len(df_weather)} záznamů z API.")
except Exception as e:
    print(f"Chyba API: {e}")
    df_weather = generate_weather_synthetic()
    print(f"Vygenerováno {len(df_weather)} syntetických záznamů.")

# Zajistíme timezone-naive timestamp pro konzistenci
df_weather["timestamp"] = pd.to_datetime(df_weather["timestamp"]).dt.tz_localize(None)

# Uložení CSV
df_weather.to_csv(WEATHER_CSV, index=False)
print(f"Uloženo: {WEATHER_CSV}  ({len(df_weather)} řádků)")


# ╔══════════════════════════════════════════════════════════════╗
# ║  2. SMART METERY — syntetická data (1000 domácností)         ║
# ╚══════════════════════════════════════════════════════════════╝

print(f"\nGeneruji syntetická smart meter data pro {N_HOUSEHOLDS} domácností...")

# Hodinové timestampy za celý rok — stejné jako počasí
timestamps = pd.to_datetime(df_weather["timestamp"].values)
n_hours = len(timestamps)
hour_arr = timestamps.hour.values           # numpy pole hodin (0–23)
doy_arr = timestamps.dayofyear.values       # numpy pole den v roce (1–365)

# Oblačnost z meteo dat — použijeme pro korelaci solární výroby
oblacnost_arr = df_weather["oblacnost"].values

rows = []  # seznam řádků pro výsledný DataFrame

for hid in range(1, N_HOUSEHOLDS + 1):
    if hid % 200 == 0:
        print(f"  ... domácnost {hid}/{N_HOUSEHOLDS}")

    # --- Spotřeba [kWh] ---
    # Bazální spotřeba s denním profilem (kachní křivka)
    base = 0.5 + RNG.uniform(-0.1, 0.1)     # bazální úroveň domácnosti

    # Denní profil: špička 18–21h, menší špička ráno
    hourly_profile = np.where(
        (hour_arr >= 18) & (hour_arr < 21),
        base * (2.5 + RNG.normal(0, 0.3, n_hours)),     # večerní špička (2.5× základ)
        np.where(
            (hour_arr >= 6) & (hour_arr < 9),
            base * (1.5 + RNG.normal(0, 0.2, n_hours)),  # ranní špička (1.5× základ)
            np.where(
                (hour_arr >= 0) & (hour_arr < 6),
                base * (0.4 + RNG.normal(0, 0.05, n_hours)),  # noční minimum
                base * (1.0 + RNG.normal(0, 0.15, n_hours))   # zbytek dne
            )
        )
    )

    # Sezónní modulace: vyšší spotřeba v zimě (topení/osvětlení)
    seasonal_factor = 1.0 + 0.3 * np.cos(2 * np.pi * (doy_arr - 1) / 365)  # max v lednu
    spotreba = np.clip(hourly_profile * seasonal_factor, 0, None)

    # --- Solární výroba [kWh] ---
    # Koreluje inverzně s oblačností, jen přes den, sezónní modulace
    solar_potential = np.clip(
        (1.2 * np.sin(np.pi * np.clip((hour_arr - 5) / 14, 0, 1))  # denní oblouk (0 v noci)
         * (1 - oblacnost_arr / 120)                                  # inverzní závislost na oblačnosti
         * (0.5 + 0.5 * np.sin(2 * np.pi * (doy_arr - 80) / 365))   # sezónní max v létě
         + RNG.normal(0, 0.05, n_hours)),                             # malý šum
        0, None
    )

    # Škálování dle „velikosti" panelů domácnosti
    panel_scale = RNG.uniform(0.6, 1.4)    # variabilita mezi domácnostmi
    solarni_vyroba = solar_potential * panel_scale

    # --- Zanesení šumu a výpadků ---
    # 5 % řádků → NaN (simulace výpadků senzorů)
    nan_mask = RNG.random(n_hours) < 0.05
    spotreba_noisy = spotreba.copy()
    solar_noisy = solarni_vyroba.copy()

    # Polovina NaN do spotřeby, polovina do solární výroby
    nan_spotreba = nan_mask & (RNG.random(n_hours) < 0.5)
    nan_solar = nan_mask & ~nan_spotreba
    spotreba_noisy[nan_spotreba] = np.nan
    solar_noisy[nan_solar] = np.nan

    # Extrémní outliery ve spotřebě (~0.5 % řádků) — chyby měření
    outlier_mask = RNG.random(n_hours) < 0.005
    spotreba_noisy[outlier_mask] = spotreba_noisy[outlier_mask] * RNG.uniform(5, 15, outlier_mask.sum())

    rows.append(pd.DataFrame({
        "timestamp":       timestamps,
        "household_id":    hid,
        "spotreba":        np.round(spotreba_noisy, 4),
        "solarni_vyroba":  np.round(solar_noisy, 4),
    }))

# Sloučení všech domácností do jednoho DataFrame
df_meters = pd.concat(rows, ignore_index=True)

# Uložení jako Parquet (sloupcový formát — efektivní pro analytiku)
df_meters.to_parquet(METERS_PARQUET, index=False, engine="pyarrow")
print(f"Uloženo: {METERS_PARQUET}  ({len(df_meters)} řádků, {N_HOUSEHOLDS} domácností)")

# === Závěrečná kontrola ===
print("\n=== SOUHRN ===")
print(f"  {WEATHER_CSV}: {len(df_weather)} řádků, sloupce: {list(df_weather.columns)}")
print(f"  {METERS_PARQUET}: {len(df_meters)} řádků, sloupce: {list(df_meters.columns)}")
print(f"  NaN ve spotřebě:        {df_meters['spotreba'].isna().sum()} ({df_meters['spotreba'].isna().mean()*100:.1f} %)")
print(f"  NaN v solární výrobě:    {df_meters['solarni_vyroba'].isna().sum()} ({df_meters['solarni_vyroba'].isna().mean()*100:.1f} %)")
print("Hotovo!")
