# {#

# #}


def generate_mesh_from_geotiff(image_path:str):
    import pyvista as pv
    import geotiff
    import numpy as np
    import xarray as xr
    import tifffile

    # Extract normalized coordinates (lat, long)
    gtiff = geotiff.GeoTiff(image_path)
    shape = gtiff.tif_shape[:2]
    x_coord_array, y_coord_array = gtiff.get_coord_arrays()
    # Stack the data so that each point has 3 values: x, y, z (z will always be 0)
    nd_coord_arrays = np.stack([x_coord_array, y_coord_array, np.zeros(shape=shape)])
    # Reshape such that we have one record per point
    coord_array = np.stack(nd_coord_arrays, axis=2).reshape((shape[0] * shape[1], 3))
    # Convert the set of points in to a triangular mesh
    mesh = pv.PolyData(coord_array).delaunay_2d()

    # Extract and flatten the data values
    tiff = tifffile.TiffFile(image_path)
    tiffdata = tiff.asarray()

    metadata = {}
    for submeta, meta_key in [(getattr(tiff, key), key) for key in dir(tiff) if 'metadata' in key]:
        if isinstance(submeta, dict):
            metadata.update(submeta)
        elif isinstance(submeta, str):
            metadata[meta_key] = submeta

    if len(tiffdata.shape) < 3:
        tiffdata = np.expand_dims(tiffdata, axis=2)

    data = xr.DataArray(
        data=tiffdata,
        dims=[
            "y",
            "x",
            "band",
        ],
        attrs=metadata,
    )
    stacked_data = data.stack(vertex=("x", "y"))
    dataset = stacked_data.to_dataset(dim="band")

    return mesh, dataset

mesh, dataset = generate_mesh_from_geotiff({{ image_path }})
