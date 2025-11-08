"""
Load meshes via meshio into PyCFS's CFSMeshData format.
"""

from __future__ import annotations

import importlib
from os import PathLike
from typing import Optional

import numpy as np

# Fail fast when this optional submodule is imported without its dependency.
if importlib.util.find_spec("meshio") is None:
    raise ModuleNotFoundError(
        "Missing dependency for submodule pyCFS.data.extras.meshio_io. "
        "Install with: pip install -U 'pyCFS[data_extra]'."
    )
import meshio  # type: ignore[import-not-found]

from pyCFS.data.io._CFSMeshDataModule import CFSMeshData


# Map meshio cell type strings to an element "dimension"
# This drives how CFSMeshData will classify elements.
_DIM_BY_CELLTYPE: dict[str, int] = {
    # 1D
    "line": 1,
    "line2": 1,
    "line3": 1,
    # 2D
    "triangle": 2,
    "triangle6": 2,
    "quad": 2,
    "quad8": 2,
    "quad9": 2,
    "polygon": 2,
    # 3D
    "tetra": 3,
    "tetra10": 3,
    "hexahedron": 3,
    "hexahedron20": 3,
    "hexahedron27": 3,
    "wedge": 3,
    "wedge15": 3,
    "wedge18": 3,
    "pyramid": 3,
    "pyramid13": 3,
    "pyramid14": 3,
}


def _infer_dimension(cell_type: str) -> int:
    """Return 1, 2, or 3 for a given meshio cell type; default to 3 if unknown."""
    return _DIM_BY_CELLTYPE.get(cell_type, 3)


def _ensure_xyz(points: np.ndarray) -> np.ndarray:
    """
    Normalize coordinates to shape (N, 3).

    - If (N, 2): pad with a zero z-column
    - If (N, M>=3): take the first 3 columns
    """
    if points.ndim != 2:
        raise ValueError("Coordinates must be a 2D array of shape (N, D).")
    if points.shape[1] == 2:
        z = np.zeros((points.shape[0], 1), dtype=points.dtype)
        return np.hstack((points, z))
    if points.shape[1] >= 3:
        return points[:, :3]
    raise ValueError("Coordinates must have at least 2 columns (x, y).")


def read_meshio(filename: str | PathLike[str], cell_type: Optional[str] = None) -> CFSMeshData:
    """
    Read a mesh file with meshio and convert it to CFSMeshData.

    Parameters
    ----------
    filename : str or PathLike
        Path to a mesh readable by meshio (e.g., ``.msh``, ``.vtk``, ``.vtu``).
    cell_type : str, optional
        If provided, select a specific block by meshio cell type name
        (e.g., ``"triangle"``, ``"tetra"``, ``"quad"``). If omitted, the first
        block in the file is used.

    Returns
    -------
    CFSMeshData
        Mesh data in PyCFS format.

    Raises
    ------
    ImportError
        If ``meshio`` is not installed.
    ValueError
        If the file contains no cells, the requested ``cell_type`` is missing,
        coordinates are invalid/non-finite, or connectivity indices are invalid.

    Examples
    --------
    >>> from pyCFS.data.extras import read_meshio
    >>> mesh = read_meshio("surface.vtk", cell_type="triangle")
    """
    # meshio availability is already guarded at import-time; keep a defensive check:
    if meshio is None:  # pragma: no cover
        raise ImportError("meshio is not installed; `pip install -U 'pyCFS[data_extra]'` to use read_meshio().")

    m = meshio.read(filename)
    if not hasattr(m, "points") or not hasattr(m, "cells_dict"):
        raise ValueError("meshio reader returned an unexpected object (missing points/cells_dict).")

    # --- coordinates ---
    points = np.asarray(m.points, dtype=float)
    if points.size == 0:
        raise ValueError("Empty coordinate array in mesh.")
    if not np.all(np.isfinite(points)):
        raise ValueError("Coordinates must be finite (no NaN/Inf).")
    points = _ensure_xyz(points)  # (N, 3)

    # --- cells / connectivity ---
    cells_dict = m.cells_dict
    if not cells_dict:
        raise ValueError("No cells found in mesh.")

    if cell_type is not None:
        conn = cells_dict.get(cell_type)
        if conn is None:
            raise ValueError(f"Cell type '{cell_type}' not found. Available: {list(cells_dict.keys())}")
        chosen_type = cell_type
    else:
        chosen_type, conn = next(iter(cells_dict.items()))

    conn = np.asarray(conn, dtype=int)
    if conn.size == 0:
        raise ValueError("Selected cell block has empty connectivity.")
    if np.min(conn) < 0:
        raise ValueError("Connectivity contains negative node indices.")
    if np.max(conn) >= points.shape[0]:
        raise ValueError(f"Connectivity index {int(np.max(conn))} out of bounds for {points.shape[0]} coordinates.")

    # Convert meshio's 0-based to PyCFS's 1-based indexing
    conn_cfs = conn + 1

    # Derive element dimension from cell type (tri -> 2D, tet -> 3D, ...)
    element_dimension = _infer_dimension(chosen_type)

    # Build CFSMeshData (classification by element_dimension) and sanity-check
    mesh = CFSMeshData.from_coordinates_connectivity(
        coordinates=points,
        connectivity=conn_cfs,
        element_dimension=element_dimension,
        region_name="meshio_import",
    )
    mesh.check_mesh()

    return mesh


# TODO: Support multiple mesh regions (multiple cell blocks) -> multiple Regions.
