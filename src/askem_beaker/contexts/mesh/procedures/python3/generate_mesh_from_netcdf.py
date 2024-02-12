# {#

# #}


def generate_mesh_from_netcdf(netcdf_path: str):
    import pyvista as pv
    import xarray as xr

    x_dim = None
    y_dim = None

    x_dim_names = [
        "latitude",
        "lat",
        "x",
    ]

    y_dim_names = [
        "longitude",
        "long",
        "lon",
        "y",
    ]

    def pick_dimension(dim_map, dim_names):
        for dim_name in dim_names:
            if dim_name in dim_map:
                return dim_map[dim_name]
        else:
            raise ValueError(f"Dimension mapping not able to be determined")

    dataset = xr.load_dataset(netcdf_path)
    dim_name_map = {dim_name.lower(): dim_name for dim_name in dataset.dims.keys()}

    x_dim = pick_dimension(dim_name_map, x_dim_names)
    y_dim = pick_dimension(dim_name_map, y_dim_names)

    grid = pv.RectilinearGrid(dataset[x_dim].values, dataset[y_dim].values)
    restacked_dataset = dataset.stack(vertex=(x_dim, y_dim))
    # Note: This may take a long time on large grids
    mesh = pv.PolyData(grid.points).delaunay_2d()
    return mesh, restacked_dataset

mesh, dataset = generate_mesh_from_netcdf({{ netcdf_path }})
