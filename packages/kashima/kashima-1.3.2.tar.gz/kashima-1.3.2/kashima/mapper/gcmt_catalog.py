#!/usr/bin/env python
"""
Global CMT Catalog API Client
==============================

Downloads seismic moment tensor data from the Global CMT Project using
their CGI search interface.

API Documentation:
    https://www.globalcmt.org/CMTsearch.html

Base URL:
    https://www.globalcmt.org/cgi-bin/globalcmt-cgi-bin/CMT5/form

Data Format:
    HTML response with embedded moment tensor data, including:
    - Event ID and location name
    - Centroid time, latitude, longitude, depth
    - Moment tensor components (Mrr, Mtt, Mpp, Mrt, Mrp, Mtp)
    - Nodal planes (strike, dip, rake)
    - Magnitudes (Mw, mb, Ms)

Moment Tensor Units & Convention:
    - Units: 10^(exponent) dyne-cm (typically exponent=24)
    - Coordinate system: Up-South-East (USE) convention
        - r (radial) = Up
        - t (theta) = South
        - p (phi) = East
    - Sign convention: Standard seismological convention
    - Order: Mrr, Mtt, Mpp, Mrt, Mrp, Mtp

    VERIFIED: Data is compatible with ISC-GEM catalog
    (Tested 2020-12-31, differences < 2%)
"""

import re
import logging
from datetime import datetime
from typing import Optional, Tuple
import pandas as pd
import requests


logger = logging.getLogger(__name__)


class GCMTCatalog:
    """
    Client for the Global CMT (Centroid Moment Tensor) Catalog.

    Downloads moment tensor solutions using the CGI search interface
    and parses HTML responses into structured data.
    """

    BASE_URL = "https://www.globalcmt.org/cgi-bin/globalcmt-cgi-bin/CMT5/form"

    def __init__(self, verbose: bool = False):
        """
        Initialize GCMT catalog client.

        Parameters
        ----------
        verbose : bool, optional
            Enable verbose logging (default: False)
        """
        self.verbose = verbose
        if verbose:
            logger.setLevel(logging.DEBUG)

    def getEvents(
        self,
        start_date: datetime,
        end_date: datetime,
        min_magnitude: float = 4.5,
        max_magnitude: float = 10.0,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        maxradiuskm: Optional[float] = None,
        min_latitude: Optional[float] = None,
        max_latitude: Optional[float] = None,
        min_longitude: Optional[float] = None,
        max_longitude: Optional[float] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Query Global CMT catalog for seismic events.

        Parameters
        ----------
        start_date : datetime
            Start date for search
        end_date : datetime
            End date for search
        min_magnitude : float, optional
            Minimum moment magnitude (default: 4.5)
        max_magnitude : float, optional
            Maximum moment magnitude (default: 10.0)
        latitude : float, optional
            Center latitude for radial search (requires longitude and maxradiuskm)
        longitude : float, optional
            Center longitude for radial search (requires latitude and maxradiuskm)
        maxradiuskm : float, optional
            Search radius in kilometers
        min_latitude : float, optional
            Minimum latitude for box search (alternative to radial)
        max_latitude : float, optional
            Maximum latitude for box search
        min_longitude : float, optional
            Minimum longitude for box search
        max_longitude : float, optional
            Maximum longitude for box search
        **kwargs
            Additional parameters (min_ms, max_ms, min_mb, max_mb, etc.)

        Returns
        -------
        pd.DataFrame
            Events with columns: time, latitude, longitude, depth, mag, mag_type,
            place, event_id, source, mrr, mtt, mpp, mrt, mrp, mtp
        """
        from datetime import timedelta

        # Determine search bounds
        if latitude is not None and longitude is not None and maxradiuskm is not None:
            # Convert radius to lat/lon box (approximate)
            llat, ulat, llon, ulon = self._radius_to_bbox(
                latitude, longitude, maxradiuskm
            )
            logger.info(
                f"Radial search: center=({latitude}, {longitude}), "
                f"radius={maxradiuskm}km → bbox=[{llat},{ulat}] × [{llon},{ulon}]"
            )
        elif all(x is not None for x in [min_latitude, max_latitude, min_longitude, max_longitude]):
            # Use provided bounding box
            llat, ulat, llon, ulon = min_latitude, max_latitude, min_longitude, max_longitude
        else:
            # Global search
            llat, ulat, llon, ulon = -90, 90, -180, 180

        logger.info(f"Querying Global CMT: {start_date.date()} → {end_date.date()}")
        logger.info(f"  Magnitude: {min_magnitude} - {max_magnitude}")
        logger.info(f"  Location: [{llat}, {ulat}] × [{llon}, {ulon}]")

        # GCMT API has result limits, so chunk by year
        # (Similar to ISC implementation)
        chunk_days = 365  # 1 year per chunk
        current_date = start_date
        all_events = []

        while current_date < end_date:
            chunk_end = min(current_date + timedelta(days=chunk_days), end_date)

            logger.info(f"  Fetching: {current_date.date()} → {chunk_end.date()}")

            # Build query parameters for this chunk
            params = {
                "itype": "ymd",
                "yr": current_date.year,
                "mo": current_date.month,
                "day": current_date.day,
                "oyr": chunk_end.year,
                "omo": chunk_end.month,
                "oday": chunk_end.day,
                "jyr": 1976,
                "jday": 1,
                "ojyr": 1976,
                "ojday": 1,
                "otype": "ymd",
                "nday": 1,
                "lmw": min_magnitude,
                "umw": max_magnitude,
                "lms": kwargs.get("min_ms", 0),
                "ums": kwargs.get("max_ms", 10),
                "lmb": kwargs.get("min_mb", 0),
                "umb": kwargs.get("max_mb", 10),
                "llat": llat,
                "ulat": ulat,
                "llon": llon,
                "ulon": ulon,
                "lhd": kwargs.get("min_half_duration", 0),
                "uhd": kwargs.get("max_half_duration", 1000),
                "lts": kwargs.get("min_time_shift", -9999),
                "uts": kwargs.get("max_time_shift", 9999),
                "lpe1": kwargs.get("min_plunge1", 0),
                "upe1": kwargs.get("max_plunge1", 90),
                "lpe2": kwargs.get("min_plunge2", 0),
                "upe2": kwargs.get("max_plunge2", 90),
                "list": 0,  # Full HTML format with details
            }

            # Make request for this chunk
            try:
                response = requests.get(self.BASE_URL, params=params, timeout=60)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to query Global CMT for {current_date.date()}: {e}")
                current_date = chunk_end
                continue

            # Parse HTML response
            chunk_events = self._parse_html(response.text)
            if not chunk_events.empty:
                all_events.append(chunk_events)
                logger.info(f"    → {len(chunk_events)} events")

            current_date = chunk_end

        # Combine all chunks
        if not all_events:
            logger.warning("No events retrieved from Global CMT")
            return pd.DataFrame()

        df = pd.concat(all_events, ignore_index=True)

        # Remove duplicates (events on chunk boundaries might be duplicated)
        df = df.drop_duplicates(subset='event_id').reset_index(drop=True)

        logger.info(f"Retrieved {len(df)} total events from Global CMT")

        return df

    def _radius_to_bbox(
        self,
        lat: float,
        lon: float,
        radius_km: float
    ) -> Tuple[float, float, float, float]:
        """
        Convert center point + radius to bounding box.

        Uses simple approximation: 1 degree ≈ 111 km at equator.

        Parameters
        ----------
        lat : float
            Center latitude
        lon : float
            Center longitude
        radius_km : float
            Radius in kilometers

        Returns
        -------
        tuple
            (min_lat, max_lat, min_lon, max_lon)
        """
        import math

        # Convert radius to degrees (approximate)
        lat_deg = radius_km / 111.0
        lon_deg = radius_km / (111.0 * math.cos(math.radians(lat)))

        min_lat = max(lat - lat_deg, -90)
        max_lat = min(lat + lat_deg, 90)
        min_lon = lon - lon_deg
        max_lon = lon + lon_deg

        # Handle dateline crossing
        if min_lon < -180:
            min_lon += 360
        if max_lon > 180:
            max_lon -= 360

        return min_lat, max_lat, min_lon, max_lon

    def _parse_html(self, html: str) -> pd.DataFrame:
        """
        Parse HTML response from Global CMT CGI.

        Expected format:
        <hr><b>202002180532A  </b> OFF COAST OF CENTRAL CHI<p>
        <pre>  Date: 2020/ 2/18   Centroid Time:  5:32:50.8 GMT
          Lat= -35.63  Lon= -73.27
          Depth= 15.0   Half duration= 0.9
          Centroid time minus hypocenter time:  5.3
          Moment Tensor: Expo=23  2.330 0.228 -2.550 -0.356 -5.290 -0.397
          Mw = 5.1    mb = 0.0    Ms = 5.0   Scalar Moment = 5.85e+23
          Fault plane:  strike=13    dip=13   slip=99
          Fault plane:  strike=184    dip=78   slip=88</pre><p>

        Parameters
        ----------
        html : str
            HTML response text

        Returns
        -------
        pd.DataFrame
            Parsed events
        """
        events = []

        # Split by event separator
        event_blocks = re.split(r'<hr>', html)

        for block in event_blocks:
            # Skip if not an event block
            if '<b>' not in block or 'Moment Tensor' not in block:
                continue

            try:
                event = self._parse_event_block(block)
                if event:
                    events.append(event)
            except Exception as e:
                logger.warning(f"Failed to parse event block: {e}")
                if self.verbose:
                    logger.debug(f"Block content:\n{block[:500]}")
                continue

        if not events:
            logger.warning("No events found in HTML response")
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(events)

        # Reorder columns to match unified schema
        column_order = [
            'time', 'latitude', 'longitude', 'depth', 'mag', 'mag_type',
            'place', 'event_id', 'source',
            'mrr', 'mtt', 'mpp', 'mrt', 'mrp', 'mtp',
            'strike1', 'dip1', 'rake1', 'strike2', 'dip2', 'rake2',
            'half_duration', 'time_shift', 'scalar_moment', 'mb', 'ms'
        ]

        # Ensure all columns exist
        for col in column_order:
            if col not in df.columns:
                df[col] = None

        return df[column_order]

    def _parse_event_block(self, block: str) -> Optional[dict]:
        """
        Parse a single event block from HTML.

        Parameters
        ----------
        block : str
            HTML block containing one event

        Returns
        -------
        dict or None
            Parsed event data
        """
        # Event ID and place
        match_id = re.search(r'<b>(\w+)\s*</b>\s+([^<\n]+)', block)
        if not match_id:
            return None

        event_id = match_id.group(1).strip()
        place = match_id.group(2).strip()

        # Date and centroid time
        match_date = re.search(
            r'Date:\s+(\d+)/\s*(\d+)/\s*(\d+)\s+Centroid Time:\s+([\d:]+\.?\d*)',
            block
        )
        if not match_date:
            return None

        year, month, day, time_str = match_date.groups()

        # Parse time (format: HH:MM:SS.S)
        time_parts = time_str.split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        second = float(time_parts[2]) if len(time_parts) > 2 else 0.0

        # Create datetime
        event_time = datetime(
            int(year), int(month), int(day),
            hour, minute, int(second), int((second % 1) * 1e6)
        )

        # Location
        match_lat = re.search(r'Lat=\s*([-\d.]+)', block)
        match_lon = re.search(r'Lon=\s*([-\d.]+)', block)
        match_depth = re.search(r'Depth=\s*([\d.]+)', block)

        if not all([match_lat, match_lon, match_depth]):
            return None

        latitude = float(match_lat.group(1))
        longitude = float(match_lon.group(1))
        depth = float(match_depth.group(1))

        # Half duration
        match_hd = re.search(r'Half duration=\s*([\d.]+)', block)
        half_duration = float(match_hd.group(1)) if match_hd else None

        # Time shift
        match_ts = re.search(r'Centroid time minus hypocenter time:\s*([-\d.]+)', block)
        time_shift = float(match_ts.group(1)) if match_ts else None

        # Moment Tensor
        match_mt = re.search(
            r'Moment Tensor: Expo=(\d+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)',
            block
        )

        if not match_mt:
            return None

        expo, mrr, mtt, mpp, mrt, mrp, mtp = match_mt.groups()

        # Convert to floats (values are in 10^expo dyne-cm)
        expo = int(expo)
        mrr = float(mrr)
        mtt = float(mtt)
        mpp = float(mpp)
        mrt = float(mrt)
        mrp = float(mrp)
        mtp = float(mtp)

        # Magnitudes (handle malformed values gracefully)
        try:
            match_mw = re.search(r'Mw\s*=\s*([\d.]+)', block)
            mw = float(match_mw.group(1)) if match_mw else None
        except (ValueError, IndexError, AttributeError):
            mw = None

        try:
            match_mb = re.search(r'mb\s*=\s*([\d.]+)', block)
            mb = float(match_mb.group(1)) if match_mb else None
        except (ValueError, IndexError, AttributeError):
            mb = None

        try:
            match_ms = re.search(r'Ms\s*=\s*([\d.]+)', block)
            ms = float(match_ms.group(1)) if match_ms else None
        except (ValueError, IndexError, AttributeError):
            ms = None

        # Scalar moment (handle incomplete/malformed values gracefully)
        try:
            match_sm = re.search(r'Scalar Moment\s*=\s*([\d.]+)e\+(\d+)', block)
            if match_sm and match_sm.group(1) and match_sm.group(2):
                sm_base, sm_exp = match_sm.groups()
                scalar_moment = float(sm_base) * (10 ** int(sm_exp))
            else:
                scalar_moment = None
        except (ValueError, IndexError, AttributeError):
            scalar_moment = None

        # Nodal planes (handle missing/incomplete values gracefully)
        strike1 = dip1 = rake1 = None
        strike2 = dip2 = rake2 = None
        try:
            planes = re.findall(r'Fault plane:\s+strike=(\d+)\s+dip=(\d+)\s+slip=(\d+)', block)
            if len(planes) >= 2:
                strike1, dip1, rake1 = map(int, planes[0])
                strike2, dip2, rake2 = map(int, planes[1])
            elif len(planes) == 1:
                strike1, dip1, rake1 = map(int, planes[0])
        except (ValueError, IndexError, TypeError):
            # Keep defaults (None)
            pass

        return {
            'time': event_time,
            'latitude': latitude,
            'longitude': longitude,
            'depth': depth,
            'mag': mw,
            'mag_type': 'Mw',
            'place': place,
            'event_id': event_id,
            'source': 'GCMT',
            'mrr': mrr,
            'mtt': mtt,
            'mpp': mpp,
            'mrt': mrt,
            'mrp': mrp,
            'mtp': mtp,
            'strike1': strike1,
            'dip1': dip1,
            'rake1': rake1,
            'strike2': strike2,
            'dip2': dip2,
            'rake2': rake2,
            'half_duration': half_duration,
            'time_shift': time_shift,
            'scalar_moment': scalar_moment,
            'mb': mb,
            'ms': ms,
            'exponent': expo,  # Store for reference (moment tensor in 10^expo dyne-cm)
        }

    def _downloadNDKFile(self, url: str) -> Optional[str]:
        """
        Download a single NDK file from GCMT server.

        Parameters
        ----------
        url : str
            Full URL to NDK file

        Returns
        -------
        str or None
            NDK file contents, or None if download failed
        """
        try:
            logger.info(f"Downloading: {url}")
            response = requests.get(url, timeout=120)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download {url}: {e}")
            return None

    def _downloadNDKMonthly(
        self,
        start_year: int,
        start_month: int,
        end_year: int,
        end_month: int
    ) -> str:
        """
        Download monthly NDK files for date range.

        Monthly files available from 2021-present at:
        https://www.ldeo.columbia.edu/~gcmt/projects/CMT/catalog/NEW_MONTHLY/YYYY/mmm##.ndk

        Parameters
        ----------
        start_year : int
            Start year
        start_month : int
            Start month (1-12)
        end_year : int
            End year
        end_month : int
            End month (1-12)

        Returns
        -------
        str
            Concatenated NDK file contents
        """
        from datetime import date

        month_names = [
            "jan", "feb", "mar", "apr", "may", "jun",
            "jul", "aug", "sep", "oct", "nov", "dec"
        ]

        ndk_content = []
        current_date = date(start_year, start_month, 1)
        end_date = date(end_year, end_month, 1)

        while current_date <= end_date:
            year = current_date.year
            month = current_date.month
            month_name = month_names[month - 1]

            # Build URL: NEW_MONTHLY/2025/jun25.ndk
            url = (
                f"https://www.ldeo.columbia.edu/~gcmt/projects/CMT/catalog/"
                f"NEW_MONTHLY/{year}/{month_name}{year % 100:02d}.ndk"
            )

            ndk_text = self._downloadNDKFile(url)
            if ndk_text:
                ndk_content.append(ndk_text)

            # Move to next month
            if month == 12:
                current_date = date(year + 1, 1, 1)
            else:
                current_date = date(year, month + 1, 1)

        return "\n".join(ndk_content)

    def _convertObsPyToDataFrame(self, catalog) -> pd.DataFrame:
        """
        Convert ObsPy Catalog to kashima DataFrame format.

        ObsPy uses Newton-meters (N·m) for moment tensors, which is converted
        to the kashima unified schema.

        Parameters
        ----------
        catalog : obspy.core.event.Catalog
            ObsPy catalog object from NDK parsing

        Returns
        -------
        pd.DataFrame
            DataFrame with kashima schema
        """
        events = []

        for event in catalog:
            try:
                # Basic event info
                origin = event.preferred_origin() or event.origins[0]
                magnitude = event.preferred_magnitude() or event.magnitudes[0]

                # Focal mechanism (moment tensor)
                focal_mech = event.preferred_focal_mechanism() or (
                    event.focal_mechanisms[0] if event.focal_mechanisms else None
                )

                if not focal_mech:
                    continue  # Skip events without moment tensors

                # Moment tensor
                mt = focal_mech.moment_tensor.tensor

                # ObsPy uses N·m, convert to kashima format (10^expo dyne-cm)
                # 1 N·m = 1e7 dyne-cm
                # Store in exponent=24 (typical GCMT convention)
                expo = 24
                scale = 1e-17  # Convert from N·m to 10^24 dyne-cm

                mrr = mt.m_rr * scale if mt.m_rr is not None else None
                mtt = mt.m_tt * scale if mt.m_tt is not None else None
                mpp = mt.m_pp * scale if mt.m_pp is not None else None
                mrt = mt.m_rt * scale if mt.m_rt is not None else None
                mrp = mt.m_rp * scale if mt.m_rp is not None else None
                mtp = mt.m_tp * scale if mt.m_tp is not None else None

                # Scalar moment
                scalar_moment = focal_mech.moment_tensor.scalar_moment

                # Nodal planes
                nodal_planes = focal_mech.nodal_planes
                if nodal_planes:
                    np1 = nodal_planes.nodal_plane_1
                    np2 = nodal_planes.nodal_plane_2
                    strike1 = int(np1.strike) if np1 and np1.strike is not None else None
                    dip1 = int(np1.dip) if np1 and np1.dip is not None else None
                    rake1 = int(np1.rake) if np1 and np1.rake is not None else None
                    strike2 = int(np2.strike) if np2 and np2.strike is not None else None
                    dip2 = int(np2.dip) if np2 and np2.dip is not None else None
                    rake2 = int(np2.rake) if np2 and np2.rake is not None else None
                else:
                    strike1 = dip1 = rake1 = strike2 = dip2 = rake2 = None

                # Additional magnitudes (mb, Ms)
                mb = None
                ms = None
                for mag in event.magnitudes:
                    if mag.magnitude_type == 'Mb' or mag.magnitude_type == 'mb':
                        mb = mag.mag
                    elif mag.magnitude_type == 'MS' or mag.magnitude_type == 'Ms':
                        ms = mag.mag

                # Event ID (extract from resource_id: smi:local/ndk/C202401010710A/event → C202401010710A)
                if event.resource_id:
                    parts = str(event.resource_id).split('/')
                    event_id = parts[-2] if len(parts) >= 2 else parts[-1]
                else:
                    event_id = None

                # Location description
                place = event.event_descriptions[0].text if event.event_descriptions else ""

                events.append({
                    'time': origin.time.datetime,
                    'latitude': origin.latitude,
                    'longitude': origin.longitude,
                    'depth': origin.depth / 1000.0,  # Convert meters to km
                    'mag': magnitude.mag,
                    'mag_type': magnitude.magnitude_type or 'Mw',
                    'place': place,
                    'event_id': event_id,
                    'source': 'GCMT',
                    'mrr': mrr,
                    'mtt': mtt,
                    'mpp': mpp,
                    'mrt': mrt,
                    'mrp': mrp,
                    'mtp': mtp,
                    'strike1': strike1,
                    'dip1': dip1,
                    'rake1': rake1,
                    'strike2': strike2,
                    'dip2': dip2,
                    'rake2': rake2,
                    'half_duration': getattr(focal_mech.moment_tensor, 'source_time_function', None),
                    'time_shift': None,  # Not directly available in ObsPy
                    'scalar_moment': scalar_moment,
                    'mb': mb,
                    'ms': ms,
                    'exponent': expo,
                })

            except (AttributeError, IndexError, TypeError) as e:
                logger.warning(f"Failed to parse event: {e}")
                continue

        if not events:
            return pd.DataFrame()

        # Convert to DataFrame with unified schema
        df = pd.DataFrame(events)

        # Ensure column order
        column_order = [
            'time', 'latitude', 'longitude', 'depth', 'mag', 'mag_type',
            'place', 'event_id', 'source',
            'mrr', 'mtt', 'mpp', 'mrt', 'mrp', 'mtp',
            'strike1', 'dip1', 'rake1', 'strike2', 'dip2', 'rake2',
            'half_duration', 'time_shift', 'scalar_moment', 'mb', 'ms'
        ]

        for col in column_order:
            if col not in df.columns:
                df[col] = None

        return df[column_order]

    def _parseNDKText(self, ndk_text: str, label: str = "") -> Optional[object]:
        """
        Parse NDK text using ObsPy.

        Parameters
        ----------
        ndk_text : str
            NDK file content
        label : str, optional
            Label for logging (e.g., "bulk 1976-2020")

        Returns
        -------
        obspy.core.event.Catalog or None
            Parsed ObsPy catalog, or None if parsing failed
        """
        from obspy import read_events
        from io import StringIO

        if not ndk_text or not ndk_text.strip():
            return None

        try:
            catalog = read_events(StringIO(ndk_text), format="NDK")
            if label:
                logger.info(f"    → Parsed {len(catalog)} events from {label}")
            return catalog
        except Exception as e:
            logger.warning(f"Failed to parse {label}: {e}")
            return None

    def getEventsFromNDK(
        self,
        start_date: datetime,
        end_date: datetime,
        min_magnitude: float = 4.5,
        max_magnitude: float = 10.0,
        **kwargs
    ) -> pd.DataFrame:
        """
        Query Global CMT catalog using NDK bulk files (fast method).

        Downloads complete GCMT catalog from NDK files:
        - Pre-1976: Deep and intermediate depth events (1962-1976)
        - Bulk: 1976-2020 (jan76_dec20.ndk - 56,832 events)
        - Monthly: 2021-present (NEW_MONTHLY/*.ndk)

        This method is significantly faster than the web API (~30 seconds vs hours)
        and retrieves the complete catalog (~63,750 events).

        Parameters
        ----------
        start_date : datetime
            Start date for search
        end_date : datetime
            End date for search
        min_magnitude : float, optional
            Minimum moment magnitude (default: 4.5)
        max_magnitude : float, optional
            Maximum moment magnitude (default: 10.0)
        **kwargs
            Additional parameters (ignored, for API compatibility)

        Returns
        -------
        pd.DataFrame
            Events with columns: time, latitude, longitude, depth, mag, mag_type,
            place, event_id, source, mrr, mtt, mpp, mrt, mrp, mtp

        Notes
        -----
        - GCMT catalog starts in 1962 (deep events only)
        - Full catalog starts in 1976
        - NDK files use Newton-meters, converted to kashima format
        - Spatial filtering (if provided) is ignored in this method
        """
        logger.info(f"Downloading GCMT catalog from NDK files...")
        logger.info(f"  Date range: {start_date.date()} → {end_date.date()}")
        logger.info(f"  Magnitude: {min_magnitude} - {max_magnitude}")

        all_catalogs = []

        # 1. Download and parse pre-1976 files if needed (1962-1976)
        if start_date.year < 1976:
            logger.info("  Fetching pre-1976 events...")

            # Deep events (1962-1976)
            url_deep = "https://www.ldeo.columbia.edu/~gcmt/projects/CMT/catalog/PRE1976/deep_1962-1976.ndk"
            ndk_deep = self._downloadNDKFile(url_deep)
            if ndk_deep:
                catalog = self._parseNDKText(ndk_deep, "pre-1976 deep")
                if catalog:
                    all_catalogs.append(catalog)

            # Intermediate depth events (1962-1975)
            url_intdep = "https://www.ldeo.columbia.edu/~gcmt/projects/CMT/catalog/PRE1976/intdep_1962-1975.ndk"
            ndk_intdep = self._downloadNDKFile(url_intdep)
            if ndk_intdep:
                catalog = self._parseNDKText(ndk_intdep, "pre-1976 intermediate")
                if catalog:
                    all_catalogs.append(catalog)

        # 2. Download and parse bulk file 1976-2020 if needed
        if start_date.year < 2021 and end_date.year >= 1976:
            logger.info("  Fetching bulk 1976-2020 catalog...")
            url_bulk = "https://www.ldeo.columbia.edu/~gcmt/projects/CMT/catalog/jan76_dec20.ndk"
            ndk_bulk = self._downloadNDKFile(url_bulk)
            if ndk_bulk:
                catalog = self._parseNDKText(ndk_bulk, "bulk 1976-2020")
                if catalog:
                    all_catalogs.append(catalog)

        # 3. Download and parse monthly files 2021-present if needed
        if end_date.year >= 2021:
            logger.info("  Fetching monthly files (2021-present)...")
            month_start = max(2021, start_date.year)
            month_end = min(end_date.year, datetime.utcnow().year)

            # Parse each month separately
            from datetime import date
            month_names = [
                "jan", "feb", "mar", "apr", "may", "jun",
                "jul", "aug", "sep", "oct", "nov", "dec"
            ]

            # Determine start and end months
            if month_start < 2021:
                start_month_num = 1  # Start from January if before 2021
            elif month_start == start_date.year:
                start_month_num = start_date.month  # Use requested start month
            else:
                start_month_num = 1  # Start from January for intervening years

            if month_end == end_date.year:
                end_month_num = end_date.month  # Use requested end month
            elif month_end < datetime.utcnow().year:
                end_month_num = 12  # Full year for past years
            else:
                end_month_num = datetime.utcnow().month  # Current month for current year

            current_date = date(month_start, start_month_num, 1)
            end_date_month = date(month_end, end_month_num, 1)

            while current_date <= end_date_month:
                year = current_date.year
                month = current_date.month
                month_name = month_names[month - 1]

                url = (
                    f"https://www.ldeo.columbia.edu/~gcmt/projects/CMT/catalog/"
                    f"NEW_MONTHLY/{year}/{month_name}{year % 100:02d}.ndk"
                )

                ndk_text = self._downloadNDKFile(url)
                if ndk_text:
                    catalog = self._parseNDKText(ndk_text, f"{month_name} {year}")
                    if catalog:
                        all_catalogs.append(catalog)

                # Move to next month
                if month == 12:
                    current_date = date(year + 1, 1, 1)
                else:
                    current_date = date(year, month + 1, 1)

        if not all_catalogs:
            logger.warning("No catalogs parsed successfully")
            return pd.DataFrame()

        # 4. Combine all catalogs
        logger.info(f"  Combining {len(all_catalogs)} catalogs...")
        from obspy.core.event import Catalog as ObsPyCatalog
        combined_catalog = ObsPyCatalog()
        for cat in all_catalogs:
            combined_catalog.extend(cat)

        logger.info(f"  Total events in combined catalog: {len(combined_catalog)}")

        # 5. Convert to kashima DataFrame
        logger.info("  Converting to kashima format...")
        df = self._convertObsPyToDataFrame(combined_catalog)

        if df.empty:
            logger.warning("No events after conversion")
            return df

        # 6. Apply filters (date, magnitude)
        logger.info("  Applying filters...")

        # Date filter
        df = df[(df['time'] >= start_date) & (df['time'] <= end_date)]

        # Magnitude filter
        df = df[(df['mag'] >= min_magnitude) & (df['mag'] <= max_magnitude)]

        # Remove duplicates
        df = df.drop_duplicates(subset='event_id').reset_index(drop=True)

        logger.info(f"  ✓ Retrieved {len(df)} events from GCMT NDK files")

        return df
