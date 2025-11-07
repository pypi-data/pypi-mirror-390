from typing import SupportsFloat

import numpy as np
from numpy.typing import NDArray

def _volume_from_spheres_float32(
    coords: NDArray[np.float32],
    radii: NDArray[np.float32],
    grid_spacing: SupportsFloat = ...,
) -> float: ...
def _volume_from_spheres_float64(
    coords: NDArray[np.float64],
    radii: NDArray[np.float64],
    grid_spacing: SupportsFloat = ...,
) -> float: ...
