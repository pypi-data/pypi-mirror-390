"""
ISC Bulletin Event Catalogue wrapper
=====================================

Downloads basic earthquake events from the ISC Bulletin API.

API Documentation: http://www.isc.ac.uk/iscbulletin/search/webservices/catalogue/

Output schema matches USGS/GCMT format:
    time | latitude | longitude | depth | mag | mag_type | place | event_id |
    source | mrr | mtt | mpp | mrt | mrp | mtp

Note: Basic event catalogue does NOT include moment tensors (mrr, mtt, etc.).
      For moment tensors, use the ISC Focal Mechanisms endpoint separately.
"""

from __future__ import annotations

import logging
import random
import time
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import requests

from .utils import stream_read_csv_bbox

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# ──────────────────────────────────────────────────────────────────────
#  Local CSV helper
# ──────────────────────────────────────────────────────────────────────
def load_isc_csv(
    csv_path: str | Path,
    bbox: Tuple[float, float, float, float] | None = None,
) -> pd.DataFrame:
    """Load ISC Bulletin CSV from disk with bbox filtering."""
    usecols = [
        "EVENTID",
        "AUTHOR",
        "DATE",
        "TIME",
        "LAT",
        "LON",
        "DEPTH",
        "DEPFIX",
        "AUTHOR",
        "TYPE",
        "MAG",
    ]
    dtypes = {
        "EVENTID": "string",
        "AUTHOR": "string",
        "LAT": "float64",
        "LON": "float64",
        "DEPTH": "float32",
        "DEPFIX": "string",
        "TYPE": "string",
        "MAG": "float32",
    }

    df = stream_read_csv_bbox(
        csv_path,
        bbox=bbox,
        lat_col="LAT",
        lon_col="LON",
        chunksize=50_000,
        dtype_map=dtypes,
        usecols=usecols,
    )

    # Combine DATE and TIME columns
    df["time"] = pd.to_datetime(
        df["DATE"].astype(str) + " " + df["TIME"].astype(str),
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce"
    )

    df = df.rename(
        columns={
            "LAT": "latitude",
            "LON": "longitude",
            "DEPTH": "depth",
            "MAG": "mag",
            "TYPE": "mag_type",
            "EVENTID": "event_id",
        }
    ).assign(
        source="ISC",
        place=pd.NA,
        mrr=np.nan,
        mtt=np.nan,
        mpp=np.nan,
        mrt=np.nan,
        mrp=np.nan,
        mtp=np.nan,
    )

    return df.reindex(
        columns=[
            "time",
            "latitude",
            "longitude",
            "depth",
            "mag",
            "mag_type",
            "place",
            "event_id",
            "source",
            "mrr",
            "mtt",
            "mpp",
            "mrt",
            "mrp",
            "mtp",
        ]
    )


__all__ = ["load_isc_csv"]


# ──────────────────────────────────────────────────────────────────────
#  Online catalogue wrapper
# ──────────────────────────────────────────────────────────────────────
class ISCBulletinCatalog:
    """Fetch earthquake events from the ISC Bulletin web service."""

    SCHEMA = [
        "time",
        "latitude",
        "longitude",
        "depth",
        "mag",
        "mag_type",
        "place",
        "event_id",
        "source",
        "mrr",
        "mtt",
        "mpp",
        "mrt",
        "mrp",
        "mtp",
    ]

    def __init__(
        self,
        min_magnitude: float = 4.5,
        verbose: bool = True,
        url: str = "http://www.isc.ac.uk/cgi-bin/web-db-run",
        timeout: int = 60,
        bulletin_type: str = "COMPREHENSIVE",
    ):
        """
        Parameters
        ----------
        min_magnitude : float
            Minimum magnitude threshold (default: 4.5)
        verbose : bool
            Enable logging output (default: True)
        url : str
            ISC Bulletin API endpoint
        timeout : int
            Request timeout in seconds (default: 60)
        bulletin_type : str
            'COMPREHENSIVE' (all data) or 'REVIEWED' (analyst-reviewed, 24mo delay)
        """
        self.min_magnitude = min_magnitude
        self.verbose = verbose
        self.url = url
        self.timeout = timeout
        self.bulletin_type = bulletin_type.upper()
        self.dataframe: pd.DataFrame | None = None

    # ------------------------------------------------------------------
    def getEvents(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        *,
        min_latitude: float | None = None,
        max_latitude: float | None = None,
        min_longitude: float | None = None,
        max_longitude: float | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        maxradiuskm: float | None = None,
        min_depth: float | None = None,
        max_depth: float | None = None,
        min_magnitude: float | None = None,
        max_magnitude: float | None = None,
        magnitude_type: str | None = None,
        **extra: Any,
    ) -> pd.DataFrame:
        """
        Download events from ISC Bulletin.

        Parameters
        ----------
        start_date : datetime
            Start of time range (default: 1904-01-01)
        end_date : datetime
            End of time range (default: now)
        latitude, longitude, maxradiuskm : float
            Circular search region
        min_latitude, max_latitude, min_longitude, max_longitude : float
            Rectangular search region
        min_magnitude, max_magnitude : float
            Magnitude range
        min_depth, max_depth : float
            Depth range in km

        Returns
        -------
        pd.DataFrame
            Events in unified schema
        """
        if start_date is None:
            start_date = datetime(1904, 1, 1)  # ISC Bulletin starts 1904
        if end_date is None:
            end_date = datetime.utcnow()
        if start_date >= end_date:
            raise ValueError("start_date must be before end_date")

        # ISC Bulletin has no documented limit, but use chunks for safety
        delta_days = 365 * 1  # 1 year per chunk (ISC is slow for large queries)
        current_date = start_date
        frames: List[pd.DataFrame] = []

        logger.setLevel(logging.INFO if self.verbose else logging.WARNING)
        if self.verbose:
            logger.info("Starting ISC Bulletin download …")

        while current_date < end_date:
            interval_end = min(current_date + timedelta(days=delta_days), end_date)
            frame = self._fetch_chunk(
                current_date,
                interval_end,
                min_latitude=min_latitude,
                max_latitude=max_latitude,
                min_longitude=min_longitude,
                max_longitude=max_longitude,
                latitude=latitude,
                longitude=longitude,
                maxradiuskm=maxradiuskm,
                min_depth=min_depth,
                max_depth=max_depth,
                min_magnitude=min_magnitude,
                max_magnitude=max_magnitude,
                magnitude_type=magnitude_type,
                **extra,
            )

            if not frame.empty:
                frames.append(frame)

            current_date = interval_end

        if not frames:
            logger.warning("No data retrieved.")
            self.dataframe = pd.DataFrame(columns=self.SCHEMA)
            return self.dataframe

        common = set.intersection(*(set(f.columns) for f in frames))
        self.dataframe = (
            pd.concat(frames, ignore_index=True)[list(common)]
            .drop_duplicates(subset="event_id")
            .reset_index(drop=True)
        )
        return self.dataframe

    # ------------------------------------------------------------------
    def _fetch_chunk(
        self,
        start: datetime,
        end: datetime,
        *,
        min_latitude,
        max_latitude,
        min_longitude,
        max_longitude,
        latitude,
        longitude,
        maxradiuskm,
        min_depth,
        max_depth,
        min_magnitude,
        max_magnitude,
        magnitude_type,
        **extra: Any,
    ) -> pd.DataFrame:
        """Fetch one time chunk from ISC Bulletin API."""
        params: Dict[str, Any] = {
            "out_format": "CATCSV",
            "request": self.bulletin_type,
            "start_year": start.year,
            "start_month": start.month,
            "start_day": start.day,
            "start_time": start.strftime("%H:%M:%S"),
            "end_year": end.year,
            "end_month": end.month,
            "end_day": end.day,
            "end_time": end.strftime("%H:%M:%S"),
        }

        # Geographic search
        if latitude is not None and longitude is not None and maxradiuskm is not None:
            params.update({
                "searchshape": "CIRC",
                "ctr_lat": latitude,
                "ctr_lon": longitude,
                "radius": maxradiuskm,
                "max_dist_units": "km",
            })
        elif (min_latitude is not None and max_latitude is not None and
              min_longitude is not None and max_longitude is not None):
            params.update({
                "searchshape": "RECT",
                "bot_lat": min_latitude,
                "top_lat": max_latitude,
                "left_lon": min_longitude,
                "right_lon": max_longitude,
            })
        else:
            params["searchshape"] = "GLOBAL"

        # Magnitude filter
        if min_magnitude is not None or self.min_magnitude is not None:
            params["min_mag"] = min_magnitude if min_magnitude is not None else self.min_magnitude
        if max_magnitude is not None:
            params["max_mag"] = max_magnitude
        if magnitude_type is not None:
            params["req_mag_type"] = magnitude_type
        else:
            params["req_mag_type"] = "Any"
        params["req_mag_agcy"] = "Any"

        # Depth filter
        if min_depth is not None:
            params["min_dep"] = min_depth
        if max_depth is not None:
            params["max_dep"] = max_depth

        params.update(extra)

        retries = 0
        while retries < 5:
            try:
                if self.verbose:
                    logger.info(
                        f"ISC {start.strftime('%Y-%m-%d')} → {end.strftime('%Y-%m-%d')} "
                        f"(CSV, try {retries + 1})"
                    )
                resp = requests.get(self.url, params=params, timeout=self.timeout)
                resp.raise_for_status()
                return self._parse_csv(resp.text)
            except requests.exceptions.HTTPError as e:
                wait = random.uniform(2, 5) * (2**retries)
                logger.warning(f"{e} – retrying in {wait:.1f}s")
            except (
                requests.exceptions.RequestException,
                pd.errors.EmptyDataError,
                pd.errors.ParserError,
            ) as e:
                wait = random.uniform(2, 5) * (2**retries)
                logger.warning(f"{e} – retrying in {wait:.1f}s")
            time.sleep(wait)
            retries += 1

        logger.error("Max retries reached – returning empty frame")
        return pd.DataFrame(columns=self.SCHEMA)

    # ------------------------------------------------------------------
    @classmethod
    def _parse_csv(cls, text: str) -> pd.DataFrame:
        """
        Parse ISC Bulletin CSV format.

        ISC API returns HTML with CSV embedded in <pre> tags.
        Expected CSV columns: EVENTID,AUTHOR,DATE,TIME,LAT,LON,DEPTH,DEPFIX,AUTHOR,TYPE,MAG
        """
        if not text.strip():
            return pd.DataFrame(columns=cls.SCHEMA)

        # Check if response contains "No events were found"
        if "No events were found" in text:
            logger.info("ISC Bulletin: No events found for this query")
            return pd.DataFrame(columns=cls.SCHEMA)

        # Extract CSV from HTML response
        # CSV starts after the header line "EVENTID,TYPE,AUTHOR..." and ends at "STOP"
        lines = text.split('\n')
        csv_lines = []
        in_csv = False

        for line in lines:
            # Start collecting CSV after header line
            if line.strip().startswith("EVENTID"):
                csv_lines.append(line)
                in_csv = True
                continue

            # Stop at STOP marker
            if line.strip() == "STOP":
                break

            # Collect data lines
            if in_csv and line.strip():
                csv_lines.append(line)

        if not csv_lines:
            logger.warning("ISC Bulletin: Could not extract CSV data from response")
            return pd.DataFrame(columns=cls.SCHEMA)

        # Parse the extracted CSV manually since rows have variable columns
        # ISC returns multiple magnitude columns (AUTHOR,TYPE,MAG repeated)
        # Format: EVENTID,TYPE,AUTHOR,DATE,TIME,LAT,LON,DEPTH,DEPFIX,AUTHOR,TYPE,MAG,AUTHOR,TYPE,MAG,...

        header_line = csv_lines[0]
        data_lines = csv_lines[1:]

        # Parse each line manually
        parsed_events = []
        for line in data_lines:
            if not line.strip():
                continue

            fields = line.split(',')
            if len(fields) < 9:
                continue

            # Extract basic event info (first 9 columns)
            event_data = {
                "EVENTID": fields[0].strip(),
                "event_type": fields[1].strip(),
                "event_author": fields[2].strip(),
                "DATE": fields[3].strip(),
                "TIME": fields[4].strip(),
                "LAT": fields[5].strip(),
                "LON": fields[6].strip(),
                "DEPTH": fields[7].strip(),
                "DEPFIX": fields[8].strip(),
            }

            # Extract magnitudes from remaining fields (triplets: AUTHOR, TYPE, MAG)
            mags = []
            for i in range(9, len(fields), 3):
                if i + 2 < len(fields):
                    try:
                        mag_author = fields[i].strip()
                        mag_type = fields[i + 1].strip().upper()
                        mag_val = float(fields[i + 2].strip())
                        if mag_val and not np.isnan(mag_val):
                            mags.append((mag_type, mag_val))
                    except (ValueError, TypeError, IndexError):
                        continue

            # Select best magnitude based on preference: Mw > MS > mb > others
            selected_mag = None
            selected_type = None
            for pref_type in ['MW', 'MWPPSM', 'MS', 'MB']:
                for mag_type, mag_val in mags:
                    if pref_type in mag_type:
                        selected_mag = mag_val
                        selected_type = mag_type
                        break
                if selected_mag:
                    break

            # If no preferred type found, use first magnitude
            if selected_mag is None and mags:
                selected_type, selected_mag = mags[0]

            event_data["TYPE"] = selected_type if selected_type else np.nan
            event_data["MAG"] = selected_mag if selected_mag else np.nan

            parsed_events.append(event_data)

        # Convert to DataFrame
        df = pd.DataFrame(parsed_events)

        # Convert numeric columns
        df["LAT"] = pd.to_numeric(df["LAT"], errors='coerce')
        df["LON"] = pd.to_numeric(df["LON"], errors='coerce')
        df["DEPTH"] = pd.to_numeric(df["DEPTH"], errors='coerce')
        df["MAG"] = pd.to_numeric(df["MAG"], errors='coerce')

        # Check if we got valid data
        if df.empty or "EVENTID" not in df.columns:
            logger.warning("ISC returned empty or invalid data")
            return pd.DataFrame(columns=cls.SCHEMA)

        # Combine DATE and TIME
        df["time"] = pd.to_datetime(
            df["DATE"].astype(str) + " " + df["TIME"].astype(str),
            format="%Y-%m-%d %H:%M:%S",
            errors="coerce"
        )

        df = df.rename(
            columns={
                "LAT": "latitude",
                "LON": "longitude",
                "DEPTH": "depth",
                "MAG": "mag",
                "TYPE": "mag_type",
                "EVENTID": "event_id",
            }
        ).assign(
            source="ISC",
            place=pd.NA,
            mrr=np.nan,
            mtt=np.nan,
            mpp=np.nan,
            mrt=np.nan,
            mrp=np.nan,
            mtp=np.nan,
        )

        return df.reindex(columns=cls.SCHEMA)
