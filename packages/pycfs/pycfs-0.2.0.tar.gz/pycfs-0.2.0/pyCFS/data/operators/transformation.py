"""
Module containing methods for mesh/data transformation operations.
"""

#    Fit Geometry
#
#      Processing Tool for CFS HDF5 files
#
#      This script fits a region to a target region by means of rotation and translation transformations based on
#      minimizing the squared distance of all source nodes to the respective nearest neighbor on the target mesh.
#
# Usage
#   python transformation.py --file-target filename_target.cfs --file-src filename_src.cfs --file-out filename_out.cfs
#   # Fits all regions in "filename_src.cfs" to all regions in "filename_target.cfs" with initially no transformation
#   python transformation.py ... --regions-target region1,region2
#   # Fits all regions in "filename_src.cfs" to "region1" and "region2" in "filename_target.cfs"
#   python transformation.py ... --regions-src region1,region2
#   # Fits regions "region1" and "region2" in "filename_src.cfs" to all regions in "filename_target.cfs"
#   python transformation.py ... --init-param 0,1,0,0,3.14,0
#   # Fits all regions in "filename_src.cfs" to all regions in "filename_target.cfs" with initial transformation
#     parameters [x,y,z,rx,ry,rz] with Euler parameters in 'XYZ' sequence (for more than 1 source region add
#     additional initial transformation parameters)
#
# Input Parameters
#   * filename_src - filename of HDF5 file source
#   * filename_out - filename of HDF5 file output
#   * filename_target - filename of HDF5 file target
#   * regions_target - (optional) list of region names to be targeted
#   * regions_fit - (optional) list of region names to be fitted
#   * transform_param_init - (optional) initial transformation parameters
#
# Return Value
#   None
#
# About
#   * Created:  Aug 2022
#   * Authors:  Andreas Wurzinger
##################################################################################
from __future__ import annotations

from typing import Optional, List, Dict, Tuple

import numpy as np
import scipy.optimize
from scipy.spatial import KDTree
from scipy.spatial import transform

from pyCFS.data import io, v_def
from pyCFS.data.io.cfs_types import cfs_element_type, check_history
from pyCFS.data.util import (
    renumber_connectivity,
    reshape_connectivity,
    vprint,
    apply_dict_vectorized,
)


def extrude_mesh_region(
    mesh: io.CFSMeshData,
    region: str | io.CFSRegData,
    extrude_vector: np.ndarray,
    num_layers: int = 1,
    created_region: Optional[str] = None,
    result_data: Optional[io.CFSResultContainer] = None,
) -> Tuple[io.CFSMeshData, io.CFSResultContainer | None]:
    """
    Extrudes a mesh region along a specified vector.

    Parameters
    ----------
    mesh : io.CFSMeshData
        The mesh data containing the region to be extruded.
    region : str or io.CFSRegData
        The region to be extruded.
    extrude_vector : np.ndarray
        The vector along which to extrude the region.
    num_layers : int, optional
        The number of layers to extrude, by default 1.
    created_region : str, optional
        The name of the created region, by default None.
    result_data : io.CFSResultContainer, optional
        The result data to be processed, by default None.

    Returns
    -------
    Tuple[io.CFSMeshData, io.CFSResultContainer or None]
        The extruded mesh data and optionally the result data.
    """
    # TODO process result data
    if created_region is None:
        created_region = f"{region}_extruded"

    coord = mesh.get_region_coordinates(region=region)
    conn = mesh.get_region_connectivity(region=region)
    el_types = mesh.get_region_element_types(region=region)

    el_type_conversion_dict = {
        cfs_element_type.TRIA3: cfs_element_type.WEDGE6,
        cfs_element_type.QUAD4: cfs_element_type.HEXA8,
        cfs_element_type.LINE2: cfs_element_type.QUAD4,
    }

    if not all(item in el_type_conversion_dict for item in el_types.flatten()):
        raise NotImplementedError(f"Region contains unsupported element types. Supported types: {list(el_type_conversion_dict.keys())}")

    conn, _ = renumber_connectivity(conn)
    conn = reshape_connectivity(conn)

    coord_base = coord.copy()
    coord_layers = [coord_base]
    conn_layers: List[np.ndarray] = []
    for i in range(num_layers):
        layer_coord = coord_base + extrude_vector * ((i + 1) / num_layers)
        layer_conn = np.zeros((conn.shape[0], 8), dtype=np.uint32)  # Prepare for maximum number of nodes in cfs_element_type.HEXA8
        if i == 0:
            layer_conn[:, : conn.shape[1]] = conn
            num_nodes = np.count_nonzero(layer_conn, axis=1)

            for eid, nnum in enumerate(num_nodes):
                if nnum == 2:  # Flip connectivity for line elements
                    layer_conn[eid, nnum : 2 * nnum] = np.flip(layer_conn[eid, :nnum], axis=0) + coord_base.shape[0] * (i + 1)
                else:
                    layer_conn[eid, nnum : 2 * nnum] = layer_conn[eid, :nnum] + coord_base.shape[0] * (i + 1)

        else:
            layer_conn = conn_layers[-1].copy()
            num_nodes = np.count_nonzero(layer_conn, axis=1)
            for eid, nnum in enumerate(num_nodes):
                layer_conn[eid, :nnum] += coord_base.shape[0]

        coord_layers.append(layer_coord)
        conn_layers.append(layer_conn)

    coord = np.concatenate(coord_layers, axis=0)
    conn = np.concatenate(conn_layers, axis=0)
    el_types = np.tile(apply_dict_vectorized(data=el_types, dictionary=el_type_conversion_dict), num_layers)

    conn = reshape_connectivity(conn)

    mesh_gen = io.CFSMeshData.from_coordinates_connectivity(
        coordinates=coord,
        connectivity=conn,
        element_types=el_types,
        region_name=created_region,
        verbosity=mesh._Verbosity,
    )

    return mesh_gen, result_data


def revolve_mesh_region(
    mesh,
    region: str | io.CFSRegData,
    revolve_axis: np.ndarray,
    revolve_angle: float,
    num_layers: int = 1,
    created_region: Optional[str] = None,
    result_data: Optional[io.CFSResultContainer] = None,
) -> Tuple[io.CFSMeshData, io.CFSResultContainer | None]:
    """
    Revolves a mesh region around a specified axis.

    Parameters
    ----------
    mesh : io.CFSMeshData
        The mesh data containing the region to be revolved.
    region : str or io.CFSRegData
        The region to be revolved.
    revolve_axis : np.ndarray
        The axis around which to revolve the region.
    revolve_angle : float
        The angle by which to revolve the region.
    num_layers : int, optional
        The number of layers to revolve, by default 1.
    created_region : str, optional
        The name of the created region, by default None.
    result_data : io.CFSResultContainer, optional
        The result data to be processed, by default None.

    Returns
    -------
    Tuple[io.CFSMeshData, io.CFSResultContainer or None]
        The revolved mesh data and optionally the result data.
    """
    # TODO process result data
    if revolve_angle > 2 * np.pi:
        vprint(
            "Warning: Revolving angle exceeds 2*pi. Revolving angle is reduced to 2*pi.",
            verbose=mesh._Verbosity > v_def.release,
        )
        revolve_angle = 2 * np.pi

    if created_region is None:
        created_region = f"{region}_revolved"

    coord = mesh.get_region_coordinates(region=region)
    conn = mesh.get_region_connectivity(region=region)
    el_types = mesh.get_region_element_types(region=region)

    el_type_conversion_dict = {
        cfs_element_type.TRIA3: cfs_element_type.WEDGE6,
        cfs_element_type.QUAD4: cfs_element_type.HEXA8,
        cfs_element_type.LINE2: cfs_element_type.QUAD4,
    }

    if not all(item in el_type_conversion_dict for item in el_types.flatten()):
        raise NotImplementedError(f"Region contains unsupported element types. Supported types: {list(el_type_conversion_dict.keys())}")

    conn, _ = renumber_connectivity(conn)
    conn = reshape_connectivity(conn)

    coord_base = coord.copy()
    coord_layers = [coord_base]
    conn_layers: List[np.ndarray] = []
    for i in range(num_layers):
        r = transform.Rotation.from_rotvec(revolve_angle * revolve_axis * (i + 1) / num_layers)
        layer_coord = r.apply(coord_base)
        layer_conn = np.zeros((conn.shape[0], 8), dtype=np.uint32)  # Prepare for maximum number of nodes in cfs_element_type.HEXA8
        if i == 0:
            layer_conn[:, : conn.shape[1]] = conn
            num_nodes = np.count_nonzero(layer_conn, axis=1)

            for eid, nnum in enumerate(num_nodes):
                if nnum == 2:  # Flip connectivity for line elements
                    layer_conn[eid, nnum : 2 * nnum] = np.flip(layer_conn[eid, :nnum], axis=0) + coord_base.shape[0] * (i + 1)
                else:
                    layer_conn[eid, nnum : 2 * nnum] = layer_conn[eid, :nnum] + coord_base.shape[0] * (i + 1)
        elif i == num_layers - 1 and revolve_angle >= 2 * np.pi:
            layer_conn = conn_layers[-1].copy()
            num_nodes = np.array(np.count_nonzero(layer_conn, axis=1) / 2, dtype=int)
            for eid, nnum in enumerate(num_nodes):
                layer_conn[eid, :nnum] = layer_conn[eid, nnum : 2 * nnum]
                layer_conn[eid, nnum : 2 * nnum] = conn[eid, :nnum]
        else:
            layer_conn = conn_layers[-1].copy()
            num_nodes = np.count_nonzero(layer_conn, axis=1)
            for eid, nnum in enumerate(num_nodes):
                layer_conn[eid, :nnum] += coord_base.shape[0]

        coord_layers.append(layer_coord)
        conn_layers.append(layer_conn)

    coord = np.concatenate(coord_layers, axis=0)
    conn = np.concatenate(conn_layers, axis=0)
    el_types = np.tile(apply_dict_vectorized(data=el_types, dictionary=el_type_conversion_dict), num_layers)
    conn = reshape_connectivity(conn)

    mesh_gen = io.CFSMeshData.from_coordinates_connectivity(
        coordinates=coord,
        connectivity=conn,
        element_types=el_types,
        region_name=created_region,
        verbosity=mesh._Verbosity,
    )

    return mesh_gen, result_data


def calc_dsum(fitCoord, regCoord_kdtree: KDTree):
    """
    Calculate the squared sum of distances between fit coordinates and the nearest neighbors in the KDTree.

    Parameters
    ----------
    fitCoord : np.ndarray
        The coordinates to fit.
    regCoord_kdtree : KDTree
        The KDTree of the target coordinates.

    Returns
    -------
    float
        The squared sum of distances.
    """
    # TODO Possible improvement: Multiple nearest neighbors with Mahalanobis distance (with mean = 0)
    d, point_index = regCoord_kdtree.query(fitCoord, workers=1)

    return sum(d * d)


def transform_data(data: np.ndarray, translate_coords: np.ndarray, rotate_angles: np.ndarray, rotate_origin: np.ndarray | None = None) -> np.ndarray:
    """
    Transform a coordinate matrix (coord) based on transformation arguments (arg).

    Parameters
    ----------
    data : np.ndarray
        A 2D array representing the data, e.g., coordinates, to be transformed.
    translate_coords : np.ndarray
        Transformation arguments [X, Y, Z].
        Perform a translation into the respective Cartesian coordinate.
    rotate_angles : np.ndarray
        Transformation arguments [RX, RY, RZ].
        Rotate the result and are specified as Euler angles in radians.
    rot_origin: np.ndarray or None
        Allow to specify an origin [X0, Y0, Z0] for the rotation operation.

    Returns
    -------
    np.ndarray
        The transformed coordinates.
    """
    # Rotation
    if rotate_origin is not None:
        data -= rotate_origin
        r = transform.Rotation.from_euler("xyz", rotate_angles)
        data = r.apply(data)
        data += rotate_origin
    else:
        r = transform.Rotation.from_euler("xyz", rotate_angles)
        data = r.apply(data)
    # Translation
    data += translate_coords
    return data


def transform_mesh_data(
    mesh: io.CFSMeshData,
    translate_coords: np.ndarray,
    rotate_angles: np.ndarray,
    rotate_origin: np.ndarray | None = None,
    transform_regions: List[str | io.CFSRegData] = [],
):
    """
    Transforms the coordinates of the mesh based on the transformation arguments.

    Parameters
    ----------
    mesh : io.CFSMeshData
        CFSMesh object of the grid to transform.
    translate_coords : tuple of float, optional
        [X, Y, Z] translation in x/y/z coordinate axes.
    rotate_angles : np.array of float
        [RX, RY, RZ] rotation around an origin. RX, RY, RZ represent Euler angles in radians
        and are applied before the translation.
    rotate_origin : np.array of float, optional
        [X0, Y0, Z0] specify an origin for the rotation. The object gets translated to the
        rotate_origin, rotated, and translated back to the initial origin.
        By default assumed to be at [0, 0, 0].
    transform_regions : List[str, io.CFSRegData], optional
        List of regions to be transformed, by default an empty list, in which case all
        regions are considered.
    """
    if transform_regions:
        fit_nodes = mesh.get_multi_region_nodes(transform_regions)
        mesh.Coordinates[fit_nodes - 1, :] = transform_data(mesh.Coordinates[fit_nodes - 1, :], translate_coords, rotate_angles, rotate_origin)
    else:
        mesh.Coordinates = transform_data(mesh.Coordinates, translate_coords, rotate_angles, rotate_origin)


def transform_result_data(
    result_data: io.CFSResultContainer,
    rotate_angles: np.ndarray,
    rotate_origin: np.ndarray | None = None,
    transform_regions: List[str | io.CFSRegData] = [],
):
    """
    Rotates the non-scalar data of a CFSResultContainer object.

    Parameters
    ----------
    result_data : io.CFSResultContainer
        CFSResultContainer object to transform with mesh.
    rotate_angles : np.array of float
        [RX, RY, RZ] rotation around an origin. RX, RY, RZ represent Euler angles in radians
        and are applied before the translation.
    rotate_origin : np.array of float, optional
        [X0, Y0, Z0] specify an origin for the rotation. The object gets translated to the
        rotate_origin, rotated, and translated back to the initial origin.
        By default assumed to be at [0, 0, 0].
    transform_regions : List[str, io.CFSRegData], optional
        List of regions to be transformed, by default an empty list, in which case all
        regions are considered.
    """
    for data_array in result_data.Data:
        quantity = data_array.Quantity
        if check_history(data_array.ResType) and not data_array.shape[2] == 1:
            vprint(f"Warning: Quantity {quantity}: Transforming History data is not supported yet.", verbose=True)
            continue
        if data_array.shape[2] == 1:
            # do not process scalar data
            continue
        data_array.require_shape()
        if not transform_regions or data_array.Region in transform_regions:
            # Reshape to (k*l, m) for vectorized operation
            k, l, m = data_array.shape
            data_array[:, :, :] = transform_data(data_array.reshape(k * l, m), np.array([0.0, 0.0, 0.0]), rotate_angles, rotate_origin).reshape(
                k, l, m
            )


def transform_mesh(
    mesh: io.CFSMeshData,
    translate_coords: tuple = (0, 0, 0),
    rotate_angles: tuple = (0, 0, 0),
    rotate_origin: tuple = (0, 0, 0),
    regions: Optional[list] = None,
    result: io.CFSResultContainer | None = None,
):
    """
    Function that transforms the coordinates of a region by means of translation and
    rotation with respect to a specified origin.

    Parameters
    ----------
    mesh_src : io.CFSMeshData
        CFSMesh object of grid to transform.
    translate_coords : tuple of float, optional
        (X, Y, Z) translation in x/y/z coordinate axes, by default (0, 0, 0).
    rotate_angles : tuple of float, optional
        (RX, RY, RZ) rotation around an origin. RX, RY, RZ represent Euler angles in radians
        and are applied before the translation, by default (0, 0, 0).
    rotate_origin : tuple of float, optional
        (X0, Y0, Z0) specify an origin for the rotation. The object gets translated to the rotate_origin, rotated, and translated back to
        the initial origin, by default (0, 0, 0).
    regions : list of str, optional
        List of region names to be transformed. If not specified, all coordinates are used, by default None.
    result : io.CFSResultContainer | None
        result container object that is transformed along with the mesh transformation (rotating non-scalar data)
    """
    # get region coords
    if regions is None:
        regions = []

    # Transform mesh (coordinates only)
    transform_mesh_data(
        mesh=mesh,
        translate_coords=np.array(translate_coords),
        rotate_angles=np.array(rotate_angles),
        rotate_origin=np.array(rotate_origin),
        transform_regions=regions,
    )
    if result:
        # Rotate non-scalar results
        transform_result_data(
            result_data=result, rotate_angles=np.array(rotate_angles), rotate_origin=np.array(rotate_origin), transform_regions=regions
        )
        return mesh, result
    return mesh


def transform_mesh_file(
    filename_src: str,
    filename_out: str,
    translate_coords: tuple = (0, 0, 0),
    rotate_angles: tuple = (0, 0, 0),
    rotate_origin: tuple = (0, 0, 0),
    regions: Optional[list] = None,
    transform_results: bool = True,
):
    """
    Top-Level function that transforms the coordinates of a region by means of translation and
    rotation with respect to a specified origin and reads / writes from / to files.

    Parameters
    ----------
    filename_src : str
        Filename of the HDF5 file source.
    filename_out : str
        Filename of the HDF5 file output.
    translate_coords : tuple of float, optional
        (X, Y, Z) translation in x/y/z coordinate axes, by default (0, 0, 0).
    rotate_angles : tuple of float, optional
        (RX, RY, RZ) rotation around an origin. RX, RY, RZ represent Euler angles in radians
        and are applied before the translation, by default (0, 0, 0).
    rotate_origin : tuple of float, optional
        (X0, Y0, Z0) specify an origin for the rotation. The object gets translated to the rotate_origin, rotated, and translated back to
        the initial origin, by default (0, 0, 0).
    regions : list of str, optional
        List of region names to be transformed. If not specified, all coordinates are used, by default None.
    transform_results : bool, optional
        Whether the results of the mesh should be transformed as well, by default True.
    """
    # Read source coordinates
    with io.CFSReader(filename_src) as h5reader:
        mesh_data = h5reader.MeshData
        if transform_results:
            # gather result data if available
            try:
                result_data = h5reader.MultiStepData
            except KeyError:
                print("Ignoring result data, as it is not available in the source file.")
                result_data = None
        else:
            result_data = None

    # get region coords
    if regions is None:
        regions = []

    # Transform mesh (coordinates only)
    transform_mesh(mesh_data, translate_coords, rotate_angles, rotate_origin, regions, result_data)

    # write mesh
    with io.CFSWriter(filename_out) as h5writer:
        h5writer.create_file(mesh=mesh_data, result=result_data)


def read_coord(filename: str, regions=None):
    """
    Read global coordinate matrix and for each region.

    Parameters
    ----------
    filename : str
        The filename of the HDF5 file.
    regions : list of str, optional
        List of region names to read coordinates for, by default None.

    Returns
    -------
    Tuple[np.ndarray, List[np.ndarray]]
        The global coordinate matrix and a list of region coordinates.
    """
    if regions is None:
        regions = []
    # Read target node Coordinates
    with io.CFSReader(filename) as h5reader:
        mesh_data = h5reader.MeshData
        reg_coord = []
        for reg in regions:
            reg_coord.append(h5reader.get_mesh_region_coordinates(region=reg))

    node_coord = mesh_data.Coordinates

    return node_coord, reg_coord


def compute_fit_transform(
    target_coords: np.ndarray,
    src_coords: np.ndarray,
    transform_param_init: np.ndarray | None = None,
    use_stochastic_optimizer=False,
    random_seed: int | None = None,
    verbosity=v_def.release,
) -> np.ndarray:
    """
    Compute the transformation parameters to fit the source coordinates to the target coordinates,
    minimizing the squared distance of all source nodes to the respective nearest neighbor.

    Parameters
    ----------
    target_coords : np.ndarray
        The target coordinates.
    src_coords : List[np.ndarray]
        The source coordinates to fit.
    transform_param_init : np.array of float, optional
        Initial transformation parameters with 6 entries: [X, Y, Z, RX, RY, RZ], where the first
        three entries perform a translation into the respective Cartesian coordinate and
        the latter three rotate the result. Rotation is specified as Euler angles in radians.
        The default is None, causing no initial transformation.
    use_stochastic_optimizer: bool, optional
        If true, differential_evolution() is used for the fit instead of minimize(). Default is False.
    random_seed: int, None
        Allows to pass a random seed for reproducibility of the stochastic optimizer results.
        Has no effect when use_stochastic_optimizer==False. Default is None, causing random distributions.
    verbosity: int, optional
        Verbosity level of the operation. Default is ``v_def.release``.

    Returns
    -------
    np.ndarray
        The optimized transformation parameters.
    """
    # Build KD Tree
    target_coord_kdtree = KDTree(target_coords)

    def cost_fit(transform_arg: np.ndarray) -> float:
        """Calculate cost of current fit"""
        coord = transform_data(data=src_coords, translate_coords=transform_arg[:3], rotate_angles=transform_arg[3:6])
        dsum = calc_dsum(coord, target_coord_kdtree)
        return dsum

    if use_stochastic_optimizer:
        pop_size = 25
        domain_dist = np.linalg.norm(np.maximum(np.max(src_coords), np.max(target_coords)) - np.minimum(np.min(src_coords), np.min(target_coords)))
        translation_bounds = [-2 * domain_dist, 2 * domain_dist]
        rotation_bounds = [0.0, 2 * np.pi]
        all_bounds = np.array([translation_bounds, translation_bounds, translation_bounds, rotation_bounds, rotation_bounds, rotation_bounds])
        if transform_param_init is None:
            init_population = "latinhypercube"
        else:
            if not len(transform_param_init) == 6:
                raise (ValueError(f"Initial transformation parameters {transform_param_init} must be given as [X, Y, Z, RX, RY, RZ]."))
            # wrap initial angle into the interval [-pi,pi)
            transform_param_init[3:] = (transform_param_init[3:] + np.pi) % (2 * np.pi)
            if np.any(transform_param_init < all_bounds[:, 0]) or np.any(transform_param_init > all_bounds[:, 1]):
                raise (ValueError(f"Initial transformation parameters\n{transform_param_init}\nmust be within optimizer bounds\n{all_bounds}"))
            init_population = np.tile(transform_param_init, pop_size).reshape(pop_size, -1)  # type: ignore[assignment]
            # add some randomness in relation to the size of the exploration bounds
            init_population += (
                0.05 * np.diff(all_bounds, axis=1).swapaxes(0, 1) * (np.random.random_sample((pop_size, len(transform_param_init))) - 0.5)
            )
        res_opt = scipy.optimize.differential_evolution(
            cost_fit,
            all_bounds,
            strategy="best1bin",
            init=init_population,
            popsize=pop_size,
            mutation=(0.5, 1.9),
            recombination=0.7,
            maxiter=2500,
            rng=random_seed,
            workers=1,
            disp=verbosity >= v_def.debug,
        )
        transform_param_opt = res_opt.x
    else:
        # use gradient based optimization
        if transform_param_init is None:
            transform_param_init = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        else:
            if not len(transform_param_init) == 6:
                raise (ValueError(f"Initial transformation parameters {transform_param_init} must be given as [X, Y, Z, RX, RY, RZ]."))
        vprint(f"Initial cost: {cost_fit(transform_param_init)}", verbose=verbosity >= v_def.debug)
        res_opt = scipy.optimize.minimize(cost_fit, transform_param_init)
        transform_param_opt = res_opt.x
        vprint(f"{res_opt.message} (numIt={res_opt.nit}, numEval={res_opt.nfev})", verbose=verbosity >= v_def.debug)
    vprint(f"Fitted cost: {cost_fit(transform_param_opt)}", verbose=verbosity >= v_def.debug)
    vprint(f" - Translation {transform_param_opt[0:3]}", verbose=verbosity >= v_def.debug)
    vprint(f" - Rotation(rad) {transform_param_opt[3:6]}", verbose=verbosity >= v_def.debug)
    vprint(f" - Rotation(deg) {180 / np.pi * transform_param_opt[3:6]}", verbose=verbosity >= v_def.debug)

    return transform_param_opt


def fit_mesh(
    mesh_src: io.CFSMeshData,
    mesh_target: io.CFSMeshData,
    transform_dict_list: List[Dict] = [{"source": [], "target": [], "transform": []}],
    result_src: io.CFSResultContainer | None = None,
    transform_param_init: np.ndarray | None = None,
    use_stochastic_optimizer=False,
    random_seed: int | None = None,
    verbosity=v_def.release,
) -> tuple[io.CFSMeshData, io.CFSResultContainer, np.ndarray] | tuple[io.CFSMeshData, None, np.ndarray]:
    """
    Fits a given mesh to a target mesh by means of rotation and translation transformations based on
    minimizing the squared distance of all source nodes to the respective nearest neighbor on the target mesh.
    Allows to specify costom combinations of source, target, and transformed mesh regions.

    Parameters
    ----------
    mesh_src : io.CFSMeshData
        CFSMesh object of grid to fit.
    mesh_target : io.CFSMeshData
        CFSMesh object of target grid.
    transform_dict_list: List[Dict],
        List of dictionaries describing which regions are used for fitting the transformation parameters
        and which regions are actually transformed. The fit is performed on each entry of the list.
        Default is an empty list for every dict key, which uses all available regions of the mesh.
        Keys:
        - "source" ... the source regions for computing the fitting parameters
        - "target" ... the target regions for computing the fitting parameters
        - "transform" ... regions of the source mesh that are actually transformed
    result_src : io.CFSResultContainer
        CFSResult object corresponding to mesh_src. Data is rotated the same way as the mesh coordinates.
        The transformation is only necessary for non-scalar data. Scalar data remains untouched.
    transform_param_init : np.array of float, optional
        Initial transformation parameters with 6 entries: (T1,T2,T3,R1,R2,R3), where T performs
        a translation into the respective Cartesian coordinate and R are the Euler angles given in radians.
        The default is None, causing no initial transformation.
    use_stochastic_optimizer: bool, optional
        If true, differential_evolution() is used for the fit instead of minimize(). Default is False.
        random_seed: int, None
        Allows to pass a random seed for reproducibility of the stochastic optimizer results.
        Has no effect when use_stochastic_optimizer==False. Default is None, causing random distributions.
    verbosity: int, optional
        Verbosity level of the operation. Default is ``v_def.release``.

    Returns
    -------
    Tuple[io.CFSMeshData, io.CFSResultContainer, np.ndarray]
        The fitted mesh data, result data, and optimized transformation parameters.
    """
    all_transform_params = np.zeros((len(transform_dict_list), 6))

    # get coordinates
    for i_dict, it_dict in enumerate(transform_dict_list):
        vprint(
            f'Compute Transformation:\n{it_dict["source"]}\n->\n{it_dict["target"]}',
            verbose=verbosity >= v_def.debug,
        )
        # Get source coordinates
        if it_dict["source"]:
            src_nodes = mesh_src.get_multi_region_nodes(it_dict["source"])
            src_coords = mesh_src.Coordinates[src_nodes - 1, :]
        else:
            src_coords = mesh_src.Coordinates
        # Get target coordinates
        if it_dict["target"]:
            target_nodes = mesh_target.get_multi_region_nodes(it_dict["target"])
            target_coords = mesh_target.Coordinates[target_nodes - 1, :]
        else:
            target_coords = mesh_target.Coordinates

        # get the transformation parameters
        transform_param_opt = compute_fit_transform(
            target_coords=target_coords,
            src_coords=src_coords,
            transform_param_init=transform_param_init,
            use_stochastic_optimizer=use_stochastic_optimizer,
            random_seed=random_seed,
            verbosity=verbosity,
        )
        all_transform_params[i_dict, :] = np.array(transform_param_opt)

        if it_dict["transform"]:
            transform_regions = it_dict["transform"]
        else:
            transform_regions = mesh_src.Regions

        translate_coords = np.array(transform_param_opt[:3])
        rotate_angles = np.array(transform_param_opt[3:])

        transform_mesh_data(
            mesh=mesh_src,
            translate_coords=translate_coords,
            rotate_angles=rotate_angles,
            rotate_origin=None,
            transform_regions=transform_regions,
        )
        if result_src:
            # Rotate non-scalar results
            transform_result_data(result_data=result_src, rotate_angles=rotate_angles, rotate_origin=None, transform_regions=transform_regions)
    if result_src:
        return mesh_src, result_src, all_transform_params
    else:
        return mesh_src, None, all_transform_params


def fit_mesh_file(
    filename_src: str,
    filename_out: str,
    filename_target: str,
    transform_dict_list: List[Dict] = [{"source": [], "target": [], "transform": []}],
    transform_param_init: np.ndarray | None = None,
    use_stochastic_optimizer=False,
    verbosity=v_def.release,
):
    """
    Top-level function for fit_mesh that reads the data from a file and writes it out to a new file.
    Fits a given mesh to a target mesh by means of rotation and translation transformations based on
    minimizing the squared distance of all source nodes to the respective nearest neighbor on the target mesh.
    Allows to specify costom combinations of source, target, and transformed mesh regions.

    Parameters
    ----------
    filename_src : str
        Filename of the HDF5 file source.
    filename_out : str
        Filename of the HDF5 file output.
    filename_target : str
        Filename of the HDF5 file target.
    transform_dict_list: List[Dict],
        List of dictionaries describing which regions are used for fitting the transformation parameters
        and which regions are actually transformed. The fit is performed on each entry of the list.
        Default is an empty list for every dict key, which uses all available regions of the mesh.
        Keys:
        - "source" ... the source regions for computing the fitting parameters
        - "target" ... the target regions for computing the fitting parameters
        - "transform" ... regions of the source mesh that are actually transformed
    result_src : io.CFSResultContainer
        CFSResult object corresponding to mesh_src. Data is rotated the same way as the mesh coordinates.
        The transformation is only necessary for non-scalar data. Scalar data remains untouched.
    transform_param_init : np.array of float, optional
        Initial transformation parameters with 6 entries: (T1,T2,T3,R1,R2,R3), where T performs
        a translation into the respective Cartesian coordinate and R are the Euler angles given in radians.
        The default is None, causing no initial transformation.
    use_stochastic_optimizer: bool, optional
        If true, differential_evolution() is used for the fit instead of minimize(). Default is False.
    verbosity: int, optional
        Verbosity level of the operation. Default is ``v_def.release``.

    Returns
    -------
    Tuple[io.CFSMeshData, io.CFSResultContainer, np.ndarray]
        The fitted mesh data, result data, and optimized transformation parameters.
    """
    """
    Fits a region to a target region by means of rotation and translation transformations based on
    minimizing the squared distance of all source nodes to the respective nearest neighbor on the target mesh.

    Parameters
    ----------
    filename_src : str
        Filename of the HDF5 file source.
    filename_out : str
        Filename of the HDF5 file output.
    filename_target : str
        Filename of the HDF5 file target.
    regions_target : list of str, optional
        List of region names to be targeted, if not specified all Coordinates are used, by default None.
    regions_fit : list of str, optional
        List of region names to be fitted, if not specified all Coordinates are used, by default None.
    transform_param_init : list of float, optional
        Initial transformation parameters, by default None.
    init_angle_degree : bool, optional
        Whether to convert initial Euler angles from degrees to radians, by default False.
    """
    # Read target Coordinates
    with io.CFSReader(filename_target) as h5reader:
        mesh_data_target = h5reader.MeshData

    # Read source Coordinates
    with io.CFSReader(filename_src) as h5reader:
        mesh_data = h5reader.MeshData
        result_data = h5reader.MultiStepData

    mesh_data, result_data, _ = fit_mesh(
        mesh_src=mesh_data,
        mesh_target=mesh_data_target,
        transform_dict_list=transform_dict_list,
        result_src=result_data,
        transform_param_init=transform_param_init,
        use_stochastic_optimizer=use_stochastic_optimizer,
        verbosity=verbosity,
    )

    with io.CFSWriter(filename_out) as h5writer:
        h5writer.create_file(mesh=mesh_data, result=result_data)


def project_mesh_onto_plane(mesh: io.CFSMeshData, plane_coords: np.ndarray, transform_regions: List[str | io.CFSRegData] = []):
    """
    Estimates a plane normal based a bunch of points sitting on the plane (plane_coords) and
    projects the mesh coordinates onto it.
    The projection is along the negative normal direction of the plane.

    Parameters
    ----------
    mesh_src : io.CFSMeshData
        CFSMesh object of grid to project.
    plane_coords : (m,3) ndarray
        Points defining the target plane.
    transform_regions : List[str, io.CFSRegData], optional
        List of regions to be transformed, by default an empty list, in which case all
        regions are considered.

    Returns
    -------
    io.CFSMeshData
        The transformed mesh data object.
    """
    # get the nodes for the desired regions
    if transform_regions:
        project_nodes = mesh.get_multi_region_nodes(transform_regions)
    else:
        project_nodes = np.arange(start=1, stop=mesh.Coordinates.shape(0), step=1)

    project_coords = mesh.Coordinates[project_nodes - 1, :]
    # --- 1. Estimate plane parameters ---
    # Take centroid as a reference point on the plane
    p0 = np.mean(plane_coords, axis=0)

    # Estimate plane normal (e.g., from PCA)
    cov = np.cov((plane_coords - p0).T)
    eigvals, eigvecs = np.linalg.eigh(cov)
    normal = eigvecs[:, np.argmin(eigvals)]  # normal = eigenvector with smallest variance
    normal /= np.linalg.norm(normal)

    # --- 2. Compute signed distances from points to plane ---
    vecs = project_coords - p0
    distances = np.dot(vecs, normal)

    # --- 3. Project in the negative normal direction ---
    projected_points = project_coords - np.outer(distances, normal)

    # Ensure projection is in the *negative* normal direction
    # (if distance > 0, projection goes toward negative normal)
    projected_points[distances > 0] = project_coords[distances > 0] - np.outer(distances[distances > 0], normal)
    projected_points[distances < 0] = project_coords[distances < 0] + np.outer(np.abs(distances[distances < 0]), normal)

    # set the new coordinates to the mesh object
    mesh.Coordinates[project_nodes - 1, :] = projected_points

    return mesh
