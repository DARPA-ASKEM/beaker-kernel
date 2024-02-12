# {#

# #}


def generate_2d_earth_grid(lat_top_right: float, lon_top_right: float, lat_bottom_left: float, lon_bottom_left:float, x_step_dist:float, y_step_dist: float, projection:str="wgs_84"):
    import pyvista as pv
    import numpy as np

    # Add point so grid is consistent and covers right/bottom boundary, but boundary may not be exact
    x_points = np.arange(lon_top_right, lon_bottom_left + x_step_dist, x_step_dist)
    y_points = np.arange(lat_top_right, lat_bottom_left + y_step_dist, y_step_dist)

    # TODO: validate input so steps are in correct direction and check that this across boundaries

    ## Optional alternative implementation
    # # Add points such that the right/bottom boundary is firm, but last step distance may be shorter than rest of grid
    # x_points = np.arange(lon_top_right, lon_bottom_left, x_step_dist)
    # y_points = np.arange(lat_top_right, lat_bottom_left, y_step_dist)
    # # Ensure that the far boundaries are included
    # if lon_bottom_left != x_points[-1]:
    #     np.append(x_points, lon_bottom_left)
    # if lat_bottom_left not in y_points:
    #     np.append(y_points, lat_bottom_left)

    grid = pv.RectilinearGrid(x_points, y_points)
    mesh = pv.PolyData(grid.points).delaunay_2d()
    return mesh

mesh = generate_2d_earth_grid(
    {{ lat_top_right }},
    {{ lon_top_right }},
    {{ lat_bottom_left }},
    {{ lon_bottom_left }},
    {{ x_step_dist }},
    {{ y_step_dist }},
    projection="{{ projection|default('wgs_84')" }}
)
