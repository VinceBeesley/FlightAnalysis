import pymeshlab


ms = pymeshlab.MeshSet()
ms.load_new_mesh("_trials/ColdDraftF3APlane.obj")

#pymeshlab.print_filter_list()

geom = ms.compute_geometric_measures()

print(geom["bbox"]["dim_x"])
print(geom["bbox"]["dim_y"])
print(geom["bbox"]["dim_z"])