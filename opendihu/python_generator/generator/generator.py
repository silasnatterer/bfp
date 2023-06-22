import numpy as np
import time
import precice

# preCICE setup
interface = precice.Interface("Fibers", "../precice_config.xml", 0, 1)
mesh_id = interface.get_mesh_id("FibersMesh")
data_id = interface.get_data_id("var", mesh_id)

ex_x, ex_y, ex_z = 3.0, 3.0, 9.0                # extent of muscle
el_x, el_y, el_z = 2, 2, 6                      # number of elements
bs_x, bs_y, bs_z = 2*el_x+1, 2*el_y+1, 2*el_z+1 # quadratic basis functions

fb_x, fb_y = 4, 4           # number of fibers
fb_points = 40              # number of points per fiber
fiber_direction = [0, 0, 1] # direction of fiber in element

coords = np.zeros((fb_x*fb_y*fb_points, 3))
for fiber_x in range(fb_x):
    for fiber_y in range(fb_y):
        x = ex_x * fiber_x / (fb_x - 1)
        y = ex_y * fiber_y / (fb_y - 1)
        for fiber_z in range(fb_points):
            i = fiber_x*fb_y*fb_points + fiber_y*fb_points + fiber_z
            coords[i] = [x, y, ex_z * fiber_z / (fb_points - 1)]

vertex_ids = interface.set_mesh_vertices(mesh_id, coords)
precice_dt = interface.initialize()
write_data = np.zeros(fb_x*fb_y*fb_points)

t = 0
dt = 0.01

while interface.is_coupling_ongoing():
    dt = np.minimum(dt, precice_dt)

    print("Generating data")
    write_data.fill(t/50.0)  # Change this value to change which constant data is written to preCICE

    interface.write_block_scalar_data(data_id, vertex_ids, write_data)

    precice_dt = interface.advance(dt)

    t = t + dt

interface.finalize()
