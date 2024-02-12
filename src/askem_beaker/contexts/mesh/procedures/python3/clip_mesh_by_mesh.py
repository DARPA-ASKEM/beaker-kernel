{#
    Args `mesh_to_clip`: pv.PolyData, `dataset`: xr.Dataset, `reference_mesh`: pv.PolyData, `operation`: "difference" | "intersection" = "difference"


#}


def clip_mesh_by_mesh_boundary(mesh_to_clip:pv.PolyData, dataset: xr.Dataset, reference_mesh:pv.PolyData, operation: str="difference"):
    if "point" not in dataset.dims:
        raise ValueError("Provided dataset is missing the `vertex` dimension.")
    clipped_mesh = mesh_to_clip.boolean_intersection(clip_shape)
    if clipped_mesh.n_points == dataset.shape[-1]:
        # Points haven't changed, can return original
        return clipped_mesh, dataset
    else:
        pass

mesh, dataset = clip_mesh_by_mesh_boundary(
    {{ mesh_to_clip }},
    {{ dataset }},
    {{ reference_mesh}},
    operation="{{ operation|default('difference') }}"
)

