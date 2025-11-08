import numpy as np
import pytest

pytest.importorskip("meshio", reason="requires meshio>=5.0")

from pyCFS.data import extras
import meshio


def test_read_meshio_triangle(tmp_path):
    # build a minimal triangle in the XY plane (3D points are fine, too)
    pts = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    cells = [("triangle", np.array([[0, 1, 2]], dtype=int))]

    m = meshio.Mesh(points=pts, cells=cells)
    mesh_file = tmp_path / "tri.msh"
    m.write(str(mesh_file))

    mesh = extras.meshio_io.read_meshio(str(mesh_file))

    # region presence
    region_names = [r.Name for r in mesh.Regions]
    assert "meshio_import" in region_names

    # Coordinates should be preserved (meshio_io pads/truncates to (N,3); here already (3,3))
    assert mesh.Coordinates.shape == (3, 3)
    assert np.allclose(mesh.Coordinates, pts)

    # Connectivity is converted to 1-based indexing
    expected_conn = cells[0][1] + 1  # -> [[1, 2, 3]]
    assert mesh.Connectivity.shape == expected_conn.shape
    assert np.array_equal(mesh.Connectivity, expected_conn)

    # element dimensionality inferred from cell type
    assert mesh.MeshInfo.Dimension == 2


def test_read_meshio_tetra(tmp_path):
    pts = np.array(
        [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]],
        dtype=float,
    )
    cells = [("tetra", np.array([[0, 1, 2, 3]], dtype=int))]

    m = meshio.Mesh(points=pts, cells=cells)
    mesh_file = tmp_path / "tet.vtk"
    m.write(str(mesh_file))

    mesh = extras.meshio_io.read_meshio(str(mesh_file))

    assert mesh.Coordinates.shape == (4, 3)
    assert np.allclose(mesh.Coordinates, pts)

    expected_conn = cells[0][1] + 1  # -> [[1, 2, 3, 4]]
    assert mesh.Connectivity.shape == expected_conn.shape
    assert np.array_equal(mesh.Connectivity, expected_conn)

    assert mesh.MeshInfo.Dimension == 3

    # sanity check
    mesh.check_mesh()
