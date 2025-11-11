from __future__ import annotations

import hashlib
import json
import os
import pathlib
from typing import Final

# Folder where per-location parquet files are stored.
_CACHE_DIR: Final[pathlib.Path] = pathlib.Path(
    os.getenv("CUBEXPRESS_CACHE", "~/.cubexpress_cache")
).expanduser()
_CACHE_DIR.mkdir(exist_ok=True)


def _cache_key(
    lon: float,
    lat: float,
    edge_size: int | tuple[int, int],
    scale: int,
    collection: str,
) -> pathlib.Path:
    """
    Return deterministic parquet path for the given query parameters.
    """
    lon_r, lat_r = round(lon, 4), round(lat, 4)
    
    # Normalize edge_size to tuple for consistent hashing
    if isinstance(edge_size, int):
        edge_tuple = (edge_size, edge_size)
    else:
        edge_tuple = edge_size
    
    raw = json.dumps([lon_r, lat_r, edge_tuple, scale, collection]).encode()
    digest = hashlib.md5(raw).hexdigest()
    return _CACHE_DIR / f"{digest}.parquet"