"""High-level helpers for tiled GeoTIFF downloads.

The module provides two thread-friendly wrappers:

* **get_geotiff** – download a single manifest, auto-tiling on EE pixel-count
  errors.
* **get_cube** – iterate over a ``RequestSet`` (or similar) and build a local
  raster “cube” in parallel.

The core download/split logic lives in *cubexpress.downloader* and
*cubexpress.geospatial*; here we merely orchestrate it.
"""

from __future__ import annotations

import pathlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any
import ee
from tqdm import tqdm


from cubexpress.downloader import download_manifest, download_manifests
from cubexpress.geospatial import quadsplit_manifest, calculate_cell_size
from cubexpress.request import table_to_requestset
import pandas as pd
from cubexpress.geotyping import RequestSet


def get_geotiff(
    manifest: Dict[str, Any],
    full_outname: pathlib.Path | str,
    nworks: int,
) -> None:
    """
    Download a single GeoTIFF from *manifest*, auto-tiling on EE pixel-count errors.
    Parameters
    ----------
    manifest
        EE download manifest (dict).
    full_outname
        Full path to output GeoTIFF.
    nworks
        Number of workers for internal tiling (if needed).
    """
    
    try:
        download_manifest(
            ulist=manifest, 
            full_outname=full_outname
        )
    except ee.ee_exception.EEException as err:
        size = manifest["grid"]["dimensions"]["width"]
        cell_w, cell_h, power = calculate_cell_size(str(err), size)
        tiled = quadsplit_manifest(manifest, cell_w, cell_h, power)
        
        download_manifests(
            manifests=tiled,
            full_outname=full_outname,
            max_workers=nworks # Here we are going to change (option 2)
        )

def get_cube(
    requests: pd.DataFrame | RequestSet,
    outfolder: pathlib.Path | str,
    nworks: int | tuple[int, int] = 4
) -> None:
    """
    Download every request in *requests* to *outfolder* using a thread pool.

    Each row in ``requests._dataframe`` must expose ``manifest`` and ``id``.
    Resulting files are named ``{id}.tif``.

    Parameters
    ----------
    requests
        A ``RequestSet`` or object with an internal ``_dataframe`` attribute.
    outfolder
        Folder where the GeoTIFFs will be written (created if absent).
    nworks : int | tuple[int, int]
        Worker configuration (default: 4):
        
        - **If int:** Number of workers for images (rows).
          Internal tiling is sequential (nworks_inner=1).
        - **If tuple[int, int]:** Specifies (nworks_outer, nworks_inner)
          for nested parallelism.
          
    Examples
    --------
    Sequential tiling, 4 parallel images:
    
    >>> get_cube(requests, "output/", nworks=4)
    
    Parallel tiling with nested workers:
    
    >>> get_cube(requests, "output/", nworks=(4, 2))
    """
    
    # Determine outer and inner worker counts
    if isinstance(nworks, int):
        nworks_outer = nworks
        nworks_inner = 1
    elif isinstance(nworks, (list, tuple)):
        if len(nworks) != 2:
            raise ValueError(
                f"nworks must have exactly 2 elements (outer, inner), got {len(nworks)}"
            )
        nworks_outer, nworks_inner = nworks
        
        # Validate positive integers
        if not (isinstance(nworks_outer, int) and isinstance(nworks_inner, int)):
            raise TypeError(
                f"nworks elements must be integers, got ({type(nworks_outer)}, {type(nworks_inner)})"
            )
        if nworks_outer <= 0 or nworks_inner <= 0:
            raise ValueError(
                f"nworks values must be positive, got ({nworks_outer}, {nworks_inner})"
            )
    else:
        raise TypeError(
            f"nworks must be int or tuple[int, int], got {type(nworks)}"
        )
    
    # Ensure output folder exists
    outfolder = pathlib.Path(outfolder).expanduser().resolve()
    outfolder.mkdir(parents=True, exist_ok=True)
    dataframe = requests._dataframe if isinstance(requests, RequestSet) else requests
    
    # Download each request in parallel
    with ThreadPoolExecutor(max_workers=nworks_outer) as executor:
        futures = {
            executor.submit(
                get_geotiff,
                manifest=row.manifest,
                full_outname=pathlib.Path(outfolder) / f"{row.id}.tif",
                nworks=nworks_inner
            ): row.id for _, row in dataframe.iterrows()
        }

        # Show progress bar
        for future in tqdm(
            as_completed(futures), 
            total=len(futures),
            desc=f"Downloading images (outer={nworks_outer}, inner={nworks_inner})",
            unit="image",
            leave=True
        ):
            try:
                future.result()
            except Exception as exc:
                print(f"Download error for {futures[future]}: {exc}")