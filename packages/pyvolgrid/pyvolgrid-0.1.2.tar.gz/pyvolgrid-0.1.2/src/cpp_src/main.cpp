#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include "volgrid.hpp"

namespace py = pybind11;

// Float64 backend
double calc_vol_float64(
    py::array_t<double, py::array::c_style> coords,
    py::array_t<double, py::array::c_style> radii,
    double grid_spacing
) {
    size_t n_spheres = static_cast<size_t>(coords.shape(0));
    const double* ptr_coords = coords.data();
    const double* ptr_radii = radii.data();

    double volume;
    {
        py::gil_scoped_release release;
        volume = volume_of_spheres<double>(ptr_coords, ptr_radii, n_spheres, grid_spacing);
    }
    return volume;
}

// Float32 backend
double calc_vol_float32(
    py::array_t<float, py::array::c_style> coords,
    py::array_t<float, py::array::c_style> radii,
    float grid_spacing
) {
    size_t n_spheres = static_cast<size_t>(coords.shape(0));
    const float* ptr_coords = coords.data();
    const float* ptr_radii = radii.data();

    float volume;
    {
        py::gil_scoped_release release;
        volume = volume_of_spheres<float>(ptr_coords, ptr_radii, n_spheres, grid_spacing);
    }
    return static_cast<double>(volume);
}

PYBIND11_MODULE(_core, m) {
    m.doc() = "C++ extension for volume calculation using a grid-based approach";

    m.def("_volume_from_spheres_float64", &calc_vol_float64,
        R"pbdoc(
            Calculate the volume occupied by spheres using a grid-based approach (float64 backend).

            Args:
                coords: N x 3 array of sphere center coordinates (float64, C-contiguous)
                radii: 1D array of sphere radii (float64, length N, C-contiguous)
                grid_spacing: Grid spacing for the volume calculation (float64)

            Returns:
                float: Estimated volume occupied by the spheres

            Notes:
                Arrays must be C-contiguous and float64. GIL is released during computation.
        )pbdoc",
        py::arg("coords").noconvert(),
        py::arg("radii").noconvert(),
        py::arg("grid_spacing") = 0.1
    );

    m.def("_volume_from_spheres_float32", &calc_vol_float32,
        R"pbdoc(
            Calculate the volume occupied by spheres using a grid-based approach (float32 backend).

            Args:
                coords: N x 3 array of sphere center coordinates (float32, C-contiguous)
                radii: 1D array of sphere radii (float32, length N, C-contiguous)
                grid_spacing: Grid spacing for the volume calculation (float32)

            Returns:
                float: Estimated volume occupied by the spheres

            Notes:
                Arrays must be C-contiguous and float32. GIL is released during computation.
        )pbdoc",
        py::arg("coords").noconvert(),
        py::arg("radii").noconvert(),
        py::arg("grid_spacing") = 0.1f
    );
}
