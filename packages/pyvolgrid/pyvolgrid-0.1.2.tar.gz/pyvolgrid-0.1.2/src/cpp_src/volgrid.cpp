#include "volgrid.hpp"
#include <cstddef>
#include <cstdint>
#include <stdexcept>
#include <limits>
#include <cmath>
#include <algorithm>
#include <memory>

template<typename T>
T volume_of_spheres(const T* coords, const T* radii, const size_t n_spheres, const T grid_spacing)
{
    // calculate origin and extent of the grid
    TR<size_t> extent;
    TR<T> origin;
    T cushion = grid_spacing + get_max(radii, n_spheres);
    get_grid_params(coords, n_spheres, cushion, grid_spacing, extent, origin);

    // allocate memory for the grid and initialize with zeroes
    size_t n_points = extent.x * extent.y * extent.z;
    if (n_points == 0) {
        return 0.0;
    }

    std::unique_ptr<int8_t[]> grid;
    try {
        grid = std::make_unique<int8_t[]>(n_points);
        std::fill(grid.get(), grid.get() + n_points, 0);
    }
    catch (const std::bad_alloc&) {
        throw std::runtime_error("Memory allocation failed for the grid.");
    }

    // loop over all spheres and mark the grid points inside the spheres
    size_t points_in_spheres = 0;
    for (size_t i = 0; i < n_spheres; ++i) {
        // radius in grid units
        T radius = radii[i] / grid_spacing;
        T radius_squared = radius * radius;

        // center of the sphere in grid units
        // assuming coords is a flat array [x1, y1, z1, x2, y2, z2, ...]
        size_t c_index = 3 * i;
        T cx = (coords[c_index] - origin.x) / grid_spacing;
        T cy = (coords[c_index + 1] - origin.y) / grid_spacing;
        T cz = (coords[c_index + 2] - origin.z) / grid_spacing;

        // determine the bounding box of the sphere in grid coordinates
        size_t x_min = static_cast<size_t>(std::max(T(0.0), std::floor(cx - radius)));
        size_t x_max = static_cast<size_t>(std::min(static_cast<T>(extent.x), std::ceil(cx + radius)));
        size_t y_min = static_cast<size_t>(std::max(T(0.0), std::floor(cy - radius)));
        size_t y_max = static_cast<size_t>(std::min(static_cast<T>(extent.y), std::ceil(cy + radius)));
        size_t z_min = static_cast<size_t>(std::max(T(0.0), std::floor(cz - radius)));
        size_t z_max = static_cast<size_t>(std::min(static_cast<T>(extent.z), std::ceil(cz + radius)));

        // iterate over the bounding box and mark points inside the sphere
        for (size_t x = x_min; x < x_max; ++x) {
            for (size_t y = y_min; y < y_max; ++y) {
                for (size_t z = z_min; z < z_max; ++z) {
                    // calculate the 1D index for the 3D grid point (x, y, z)
                    size_t index = x * extent.y * extent.z + y * extent.z + z;

                    // skip already processed points
                    if (grid[index] == 1) continue;

                    // check if the point is inside the sphere
                    T dx = (static_cast<T>(x) - cx);
                    T dy = (static_cast<T>(y) - cy);
                    T dz = (static_cast<T>(z) - cz);
                    if ((dx * dx + dy * dy + dz * dz) <= radius_squared) {
                        grid[index] = 1;
                        points_in_spheres++;
                    }
                }
            }
        }
    }

    // calculate the total volume
    T volume_per_point = grid_spacing * grid_spacing * grid_spacing;
    T total_volume = static_cast<T>(points_in_spheres) * volume_per_point;

    return total_volume;
}

template<typename T>
T get_max(const T* array, const size_t n)
{
    if (n == 0) {
        throw std::invalid_argument("Cannot find the maximum of an empty array.");
    }

    T max_val = -std::numeric_limits<T>::infinity();
    for (size_t i = 0; i < n; ++i) {
        // assume array is a flat array
        if (array[i] > max_val) {
            max_val = array[i];
        }
    }
    return max_val;
}

template<typename T>
void get_grid_params(
    const T* coords, const size_t& n_coords, const T& cushion, const T& grid_spacing,
    TR<size_t>& extent, TR<T>& origin
)
{
    // extent of coordinates in cartesian
    TR<T> min_coords, max_coords;
    get_extent(coords, n_coords, min_coords, max_coords);

     // calculate extent in grid units
    long a_min = static_cast<long>(std::floor((min_coords.x - cushion) / grid_spacing));
    long a_max = static_cast<long>(std::ceil((max_coords.x + cushion) / grid_spacing));
    long b_min = static_cast<long>(std::floor((min_coords.y - cushion) / grid_spacing));
    long b_max = static_cast<long>(std::ceil((max_coords.y + cushion) / grid_spacing));
    long c_min = static_cast<long>(std::floor((min_coords.z - cushion) / grid_spacing));
    long c_max = static_cast<long>(std::ceil((max_coords.z + cushion) / grid_spacing));

    // number of grid points and origin of the grid
    extent = {
        static_cast<size_t>(a_max - a_min + 1),
        static_cast<size_t>(b_max - b_min + 1),
        static_cast<size_t>(c_max - c_min + 1)
    };
    origin = {a_min * grid_spacing, b_min * grid_spacing, c_min * grid_spacing};
}

template<typename T>
void get_extent(const T* coords, const size_t& n_coords, TR<T>& min_coords, TR<T>& max_coords)
{
    if (n_coords == 0) {
        throw std::invalid_argument("Cannot determine min/max of an empty array.");
    }

    min_coords.x = min_coords.y = min_coords.z = std::numeric_limits<T>::infinity();
    max_coords.x = max_coords.y = max_coords.z = -std::numeric_limits<T>::infinity();

    for (size_t i = 0; i < n_coords; ++i) {
        // assume coords is a flat array [x1, y1, z1, x2, y2, z2, ...]
        T x = coords[3 * i];
        T y = coords[3 * i + 1];
        T z = coords[3 * i + 2];

        if (x < min_coords.x) min_coords.x = x;
        if (y < min_coords.y) min_coords.y = y;
        if (z < min_coords.z) min_coords.z = z;

        if (x > max_coords.x) max_coords.x = x;
        if (y > max_coords.y) max_coords.y = y;
        if (z > max_coords.z) max_coords.z = z;
    }
}

// Explicit template instantiations for int, float and double
template struct TR<size_t>;
template struct TR<float>;
template struct TR<double>;

template float get_max<float>(const float*, const size_t);
template double get_max<double>(const double*, const size_t);

template void get_extent<float>(const float*, const size_t&, TR<float>&, TR<float>&);
template void get_extent<double>(const double*, const size_t&, TR<double>&, TR<double>&);

template void get_grid_params<float>(const float*, const size_t&,
                                      const float&, const float&, TR<size_t>&, TR<float>&);
template void get_grid_params<double>(const double*, const size_t&,
                                       const double&, const double&, TR<size_t>&, TR<double>&);

template float volume_of_spheres<float>(const float*, const float*, const size_t, const float);
template double volume_of_spheres<double>(const double*, const double*, const size_t, const double);
