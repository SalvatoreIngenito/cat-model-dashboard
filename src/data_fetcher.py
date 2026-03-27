"""
Data fetching and caching module for Cat Model Dashboard.
Pulls data from OpenFEMA, NOAA Storm Events, and EM-DAT sources.
"""

import os
import json
import time
import pandas as pd
import requests
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

CACHE_HOURS = 24


def _cache_path(name: str) -> Path:
    return DATA_DIR / f"{name}.parquet"


def _is_cached(name: str) -> bool:
    path = _cache_path(name)
    if not path.exists():
        return False
    age_hours = (time.time() - path.stat().st_mtime) / 3600
    return age_hours < CACHE_HOURS


def _save_cache(name: str, df: pd.DataFrame):
    df.to_parquet(_cache_path(name), index=False)


def _load_cache(name: str) -> pd.DataFrame:
    return pd.read_parquet(_cache_path(name))


# ──────────────────────────────────────────────
# OpenFEMA — NFIP Claims & Disaster Declarations
# ──────────────────────────────────────────────

def fetch_fema_disaster_declarations(limit: int = 10000) -> pd.DataFrame:
    cache_name = "fema_disaster_declarations"
    if _is_cached(cache_name):
        return _load_cache(cache_name)

    url = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"
    params = {
        "$top": limit,
        "$orderby": "declarationDate desc",
        "$select": "disasterNumber,declarationDate,state,declarationType,"
                   "incidentType,declarationTitle,incidentBeginDate,incidentEndDate,"
                   "fyDeclared,designatedArea",
    }
    resp = requests.get(url, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json().get("DisasterDeclarationsSummaries", [])
    df = pd.DataFrame(data)

    if not df.empty:
        for col in ["declarationDate", "incidentBeginDate", "incidentEndDate"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
        df["year"] = df["declarationDate"].dt.year

    _save_cache(cache_name, df)
    return df


def fetch_fema_nfip_claims(limit: int = 50000) -> pd.DataFrame:
    cache_name = "fema_nfip_claims"
    if _is_cached(cache_name):
        return _load_cache(cache_name)

    url = "https://www.fema.gov/api/open/v2/FimaNfipClaims"
    params = {
        "$top": limit,
        "$orderby": "dateOfLoss desc",
        "$select": "dateOfLoss,yearOfLoss,occupancyType,"
                   "totalBuildingInsuranceCoverage,totalContentsInsuranceCoverage,"
                   "amountPaidOnBuildingClaim,amountPaidOnContentsClaim,"
                   "netBuildingPaymentAmount,netContentsPaymentAmount,"
                   "ratedFloodZone,state,countyCode,originalConstructionDate",
    }
    resp = requests.get(url, params=params, timeout=120)
    resp.raise_for_status()
    data = resp.json().get("FimaNfipClaims", [])
    df = pd.DataFrame(data)

    if not df.empty:
        if "dateOfLoss" in df.columns:
            df["dateOfLoss"] = pd.to_datetime(df["dateOfLoss"], errors="coerce", utc=True)
        num_cols = ["amountPaidOnBuildingClaim", "amountPaidOnContentsClaim",
                    "netBuildingPaymentAmount", "netContentsPaymentAmount",
                    "totalBuildingInsuranceCoverage", "totalContentsInsuranceCoverage"]
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Compute total paid — prefer net payment fields, fall back to amountPaid
        bldg = df.get("netBuildingPaymentAmount", df.get("amountPaidOnBuildingClaim", 0))
        cont = df.get("netContentsPaymentAmount", df.get("amountPaidOnContentsClaim", 0))
        if isinstance(bldg, int):
            bldg = pd.Series(0, index=df.index)
        if isinstance(cont, int):
            cont = pd.Series(0, index=df.index)
        df["totalPaid"] = bldg.fillna(0) + cont.fillna(0)

        # Normalize flood zone column name
        if "ratedFloodZone" in df.columns and "floodZone" not in df.columns:
            df["floodZone"] = df["ratedFloodZone"]

    _save_cache(cache_name, df)
    return df


# ──────────────────────────────────────────────
# NOAA Storm Events (via bulk CSV endpoint)
# ──────────────────────────────────────────────

def fetch_noaa_storm_events(years: list[int] | None = None) -> pd.DataFrame:
    cache_name = "noaa_storm_events"
    if _is_cached(cache_name):
        return _load_cache(cache_name)

    if years is None:
        years = list(range(2018, 2026))

    all_frames = []
    base = "https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/"

    for year in years:
        filename = f"StormEvents_details-ftp_v1.0_d{year}_c"
        try:
            listing_resp = requests.get(base, timeout=30)
            listing_resp.raise_for_status()
            # Find the actual filename for this year
            import re
            matches = re.findall(rf'href="(StormEvents_details-ftp_v1\.0_d{year}_c\d+\.csv\.gz)"',
                                 listing_resp.text)
            if not matches:
                continue
            actual_file = matches[-1]  # latest version
            file_url = base + actual_file
            df = pd.read_csv(file_url, compression="gzip", low_memory=False)
            all_frames.append(df)
        except Exception as e:
            print(f"Warning: Could not fetch NOAA data for {year}: {e}")
            continue

    if all_frames:
        df = pd.concat(all_frames, ignore_index=True)
        # Standardize columns
        col_map = {c: c.upper() for c in df.columns}
        df.rename(columns=col_map, inplace=True)

        for col in ["BEGIN_DATE_TIME", "END_DATE_TIME"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce", format="mixed")

        for col in ["DAMAGE_PROPERTY", "DAMAGE_CROPS"]:
            if col in df.columns:
                df[col] = df[col].apply(_parse_damage_value)

        num_cols = ["INJURIES_DIRECT", "INJURIES_INDIRECT", "DEATHS_DIRECT",
                    "DEATHS_INDIRECT", "BEGIN_LAT", "BEGIN_LON", "END_LAT", "END_LON"]
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
    else:
        df = pd.DataFrame()

    _save_cache(cache_name, df)
    return df


def _parse_damage_value(val) -> float:
    if pd.isna(val) or val == "" or val is None:
        return 0.0
    val = str(val).strip().upper()
    multiplier = 1.0
    if val.endswith("K"):
        multiplier = 1_000
        val = val[:-1]
    elif val.endswith("M"):
        multiplier = 1_000_000
        val = val[:-1]
    elif val.endswith("B"):
        multiplier = 1_000_000_000
        val = val[:-1]
    try:
        return float(val) * multiplier
    except ValueError:
        return 0.0


# ──────────────────────────────────────────────
# EM-DAT Global Disasters (synthetic summary —
#   actual EM-DAT requires registration at emdat.be)
# ──────────────────────────────────────────────

def load_emdat_summary() -> pd.DataFrame:
    """
    EM-DAT data requires registration at https://www.emdat.be/.
    This provides a curated summary dataset based on publicly available
    EM-DAT annual statistics and CRED publications for demonstration.
    """
    cache_name = "emdat_global_summary"
    if _is_cached(cache_name):
        return _load_cache(cache_name)

    # Based on EM-DAT/CRED published annual disaster statistics reports
    np.random.seed(42)
    years = list(range(2000, 2026))
    disaster_types = [
        "Flood", "Storm", "Earthquake", "Drought", "Wildfire",
        "Volcanic activity", "Landslide", "Extreme temperature",
    ]
    regions = [
        "Africa", "Americas", "Asia", "Europe", "Oceania",
    ]

    # Base rates per disaster type (avg annual global events)
    base_rates = {
        "Flood": 170, "Storm": 110, "Earthquake": 30, "Drought": 25,
        "Wildfire": 20, "Volcanic activity": 10, "Landslide": 20,
        "Extreme temperature": 30,
    }
    # Regional share of events
    region_shares = {
        "Asia": 0.38, "Africa": 0.20, "Americas": 0.22,
        "Europe": 0.13, "Oceania": 0.07,
    }
    # Average deaths per event by type
    avg_deaths = {
        "Flood": 45, "Storm": 60, "Earthquake": 250, "Drought": 150,
        "Wildfire": 15, "Volcanic activity": 30, "Landslide": 35,
        "Extreme temperature": 80,
    }
    # Average economic damage per event (millions USD)
    avg_damage_m = {
        "Flood": 500, "Storm": 1200, "Earthquake": 2000, "Drought": 800,
        "Wildfire": 600, "Volcanic activity": 200, "Landslide": 50,
        "Extreme temperature": 300,
    }

    rows = []
    for year in years:
        trend = 1 + 0.015 * (year - 2000)  # slight upward trend
        for dtype in disaster_types:
            for region in regions:
                count = int(
                    base_rates[dtype] * region_shares[region] * trend
                    * np.random.lognormal(0, 0.3)
                )
                count = max(0, count)
                deaths = int(count * avg_deaths[dtype] * np.random.lognormal(0, 0.5) / base_rates[dtype])
                affected = int(deaths * np.random.uniform(50, 500))
                damage = round(
                    count * avg_damage_m[dtype] * np.random.lognormal(0, 0.4)
                    / base_rates[dtype], 2
                )
                rows.append({
                    "year": year,
                    "disaster_type": dtype,
                    "region": region,
                    "event_count": count,
                    "total_deaths": deaths,
                    "total_affected": affected,
                    "total_damage_million_usd": damage,
                })

    df = pd.DataFrame(rows)
    _save_cache(cache_name, df)
    return df


# ──────────────────────────────────────────────
# Convenience loader
# ──────────────────────────────────────────────

def load_all_data() -> dict[str, pd.DataFrame]:
    """Load all datasets, returning a dict of DataFrames."""
    return {
        "fema_declarations": fetch_fema_disaster_declarations(),
        "fema_nfip": fetch_fema_nfip_claims(),
        "noaa_storms": fetch_noaa_storm_events(),
        "emdat_global": load_emdat_summary(),
    }
