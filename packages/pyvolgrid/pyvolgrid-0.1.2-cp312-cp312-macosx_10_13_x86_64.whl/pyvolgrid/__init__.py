from importlib.metadata import PackageNotFoundError, version
from typing import cast

import numpy as np
from numpy.typing import ArrayLike, NDArray

from pyvolgrid._core import _volume_from_spheres_float32, _volume_from_spheres_float64

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    __version__ = "0.0.0"


def volume_from_spheres(
    coords: ArrayLike,
    radii: ArrayLike | float,
    grid_spacing: float = 0.1,
) -> float:
    """Calculate the volume occupied by a set of spheres using a grid-based method.

    Parameters
    ----------
    coords : array-like
        An array-like object of shape (N, 3) containing the coordinates of the centers.
    radii : array-like or float
        An array-like object of shape (N,) containing the radii of the spheres.
        If a single float is provided, all spheres are assumed to have the same radius.
    grid_spacing : float, optional
        The spacing between grid points. Default is 0.1.

    Returns
    -------
    float
        The total volume occupied by the spheres.

    Notes
    -----
    Input arrays are automatically converted to C-contiguous numpy arrays as required
    by the underlying C++ implementation. Float32 and float64 dtypes are preserved
    to avoid unnecessary conversions; all other types are converted to float64.
    """

    # Convert to numpy arrays for inspection
    coords_arr = np.asarray(coords)
    radii_is_scalar = np.isscalar(radii)

    # Shape validation for coords
    if coords_arr.ndim != 2 or coords_arr.shape[1] != 3:
        raise ValueError(f"coords must have shape (N, 3), got shape {coords_arr.shape}")
    if coords_arr.shape[0] == 0:
        raise ValueError("coords must contain at least one coordinate")

    # Determine target dtype using numpy.result_type for robustness
    if radii_is_scalar:
        result_type = np.result_type(coords_arr.dtype, radii)
        radii_arr = None
    else:
        radii_arr = np.asarray(radii)
        result_type = np.result_type(coords_arr.dtype, radii_arr.dtype)

    # Use float32 if the result can be safely cast, otherwise default to float64
    DTYPE = np.float32 if np.can_cast(result_type, np.float32, casting="safe") else np.float64

    # Validate grid spacing
    if grid_spacing <= 0.0:
        raise ValueError("grid_spacing must be greater than 0.0")

    coords_array = np.ascontiguousarray(coords_arr, dtype=DTYPE)

    if radii_is_scalar:
        radii_array = np.full(coords_array.shape[0], radii, dtype=DTYPE)
    else:
        radii_array = np.ascontiguousarray(radii_arr, dtype=DTYPE)

    # Validate radii
    if radii_array.ndim != 1:
        raise ValueError(f"radii must be 1-dimensional, got shape {radii_array.shape}")
    if radii_array.shape[0] != coords_array.shape[0]:
        raise ValueError(
            f"Number of radii ({radii_array.shape[0]}) must match number of coordinates ({coords_array.shape[0]})"
        )

    if DTYPE == np.float32:
        coords_f32 = cast(NDArray[np.float32], coords_array)
        radii_f32 = cast(NDArray[np.float32], radii_array)
        return _volume_from_spheres_float32(coords_f32, radii_f32, grid_spacing)
    else:
        coords_f64 = cast(NDArray[np.float64], coords_array)
        radii_f64 = cast(NDArray[np.float64], radii_array)
        return _volume_from_spheres_float64(coords_f64, radii_f64, grid_spacing)


__all__ = ["volume_from_spheres"]
