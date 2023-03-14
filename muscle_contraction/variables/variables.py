import sys
import itertools
import numpy as np

rank_no = int(sys.argv[-2])
n_ranks = int(sys.argv[-1])

# Scenario name
scenario_name = "muscle_contraction"
input_dir = "../../../electrophysiology/input/"

# Time stepping
dt_3D = 1e0             # time step of 3D mechanics
dt_splitting = 2e-3     # time step of strang splitting
dt_1D = 2e-3            # time step of 1D fiber diffusion
dt_0D = 1e-3            # time step of 0D cellml problem
end_time = 100.0        # end time of the simulation 

# Mechanics
pmax = 7.3                                                  # maximum active stress
rho = 10                                                    # density of the muscle
material_parameters = [3.176e-10, 1.813, 1.075e-2, 9.1733]  # [c1, c2, b, d]
constant_body_force = (0, 0, 0)                             # gravity (0, 0, -9.81e-4)

# Solvers
solvers = {
    "diffusion_solver": { # implicit timestepping diffusion
        "maxIterations": 1e4,
        "relativeTolerance": 1e-10,
        "absoluteTolerance": 1e-10,
        "solverType": "cg",
        "preconditionerType": "none",
        "dumpFilename": "",
        "dumpFormat": "matLab"
    },
    "mechanics_solver": { # solver for 3D mechanics
        "maxIterations": 1e4,
        "relativeTolerance": 1e-5,
        "absoluteTolerance": 1e-10,
        "solverType": "lu",
        "preconditionerType": "none",
        "snesMaxFunctionEvaluations": 1e8,
        "snesMaxIterations": 10,
        "snesRelativeTolerance": 1e-5,
        "snesAbsoluteTolerance": 1e-5,
        "snesLineSearchType": "l2",
        "snesRebuildJacobianFrequency": 2,
        "dumpFilename": "",
        "dumpFormat": "matLab"
    }
}
diffusion_solver_name = "diffusion_solver"
mechanics_solver_name = "mechanics_solver"

# Output writer
output_writer_mechanics = [{
    "format":           "Paraview",
    "outputInterval":   int(1.0/dt_3D),
    "filename":         "out/" + scenario_name + "/mechanics_3D",
    "binary":           True,
    "fixedFormat":      False,
    "onlyNodalValues":  True,
    "combineFiles":     True,
    "fileNumbering":    "incremental"
}]
output_writer_fibers = [{
    "format":           "Paraview",
    "outputInterval":   int(1.0/dt_splitting),
    "filename":         "out/" + scenario_name + "/fibers",
    "binary":           True,
    "fixedFormat":      False,
    "combineFiles":     True,
    "fileNumbering":    "incremental"
}]

# Meshes
n_subdomains_x = 1
n_subdomains_y = 1
n_subdomains_z = 1

ex_x, ex_y, ex_z = 3.0, 3.0, 9.0                # extent of muscle
el_x, el_y, el_z = 3, 3, 9                      # number of elements
bs_x, bs_y, bs_z = 2*el_x+1, 2*el_y+1, 2*el_z+1 # quadratic basis functions

fb_x, fb_y = 4, 4   # number of fibers
fb_points = 40      # number of points per fiber

meshes = {
    "mesh3D": {
        "nElements":            [el_x, el_y, el_z],
        "physicalExtent":       [ex_x, ex_y, ex_z],
        "physicalOffset":       [0, 0, 0],
        "logKey":               "mesh3D",
        "inputMeshIsGlobal":    True,
        "nRanks":               n_ranks
    }
}
mesh3D_name = "mesh3D"
fiber_mesh_names = list(range(fb_x * fb_y))
mappings_between_meshes = {}

def get_fiber_no(subdomain_x, subdomain_y, fiber_x, fiber_y):
    return fiber_x + fiber_y*fb_x

def n_fibers_in_subdomain_x(subdomain_x):
    return fb_x

def n_fibers_in_subdomain_y(subdomain_y):
    return fb_y

for subdomain_x, subdomain_y in itertools.product(range(n_subdomains_x), range(n_subdomains_y)):
    for fiber_x, fiber_y in itertools.product(range(n_fibers_in_subdomain_x(subdomain_x)), range(n_fibers_in_subdomain_y(subdomain_y))):
        fiber_no = get_fiber_no(subdomain_x, subdomain_y, fiber_x, fiber_y)
        x = ex_x * fiber_x / (fb_x - 1)
        y = ex_y * fiber_y / (fb_y - 1)
        nodePositions = [[x, y, ex_z * i / (fb_points - 1)] for i in range(fb_points)]
        meshName = "fiber{}".format(fiber_no)
        meshes[meshName] = {
            "nElements":            [fb_points - 1],
            "nodePositions":        nodePositions,
            "inputMeshIsGlobal":    True,
            "nRanks":               n_ranks
        }
        fiber_mesh_names[fiber_no] = meshName
        mappings_between_meshes[meshName] = mesh3D_name

# Boundary conditions
dirichlet_bc = {} # fix z=0 with dirichlet boundary conditions
for x, y in itertools.product(range(bs_x), range(bs_y)):
    dirichlet_bc[x + y*bs_x] = [0.0, 0.0, 0.0, None, None, None]

neumann_bc = [] # add pulling force to z=el_z with neumann boundary conditions
neumann_force = 0
for x, y in itertools.product(range(el_x), range(el_y)):
    neumann_bc += [{
        "element": x + y*el_x + (el_z-1)*el_y*el_x, 
        "constantVector": [0, 0, neumann_force], 
        "face": "0+"
    }]

init_displacement = [[0.0, 0.0, 0.0] for _ in range(bs_x*bs_y*bs_z)]
init_velocity = [[0.0, 0.0, 0.0] for _ in range(bs_x*bs_y*bs_z)]

# Fiber activation
vm_value_stimulated = 20.0
fiber_distribution_file = input_dir + "MU_fibre_distribution_3780.txt"
firing_times_file = input_dir + "MU_firing_times_always.txt"
fiber_distribution = np.genfromtxt(fiber_distribution_file, delimiter=" ", dtype=int)
firing_times = np.genfromtxt(firing_times_file)

def get_motor_unit_no(fiber_no):
    return int(fiber_distribution[fiber_no % len(fiber_distribution)]-1)

Conductivity = 3.828
Am = 500.0
Cm = 0.58

def get_specific_states_call_frequency(fiber_no):
    return 1*1e-3

def get_specific_states_frequency_jitter(fiber_no):
    return [0]

def get_specific_states_call_enable_begin(fiber_no):
    return 10.0 

def get_diffusion_prefactor(fiber_no):
    return Conductivity / (Am * Cm)

def fiber_gets_stimulated(fiber_no, current_time):
    frequency = get_specific_states_call_frequency(fiber_no)
    mu = get_motor_unit_no(fiber_no)
    index = int(np.round(current_time * frequency))
    size = np.size(firing_times, 0)
    return firing_times[index % size, mu] == 1

def set_specific_states(n_nodes_global, time_step_no, current_time, states, fiber_no):
    if fiber_gets_stimulated(fiber_no, current_time):
        innervation_node_global = int(n_nodes_global/2)
        nodes_to_stimulate = [innervation_node_global]
        if innervation_node_global > 0:
            nodes_to_stimulate.insert(0, innervation_node_global-1)
        if innervation_node_global < n_nodes_global-1:
            nodes_to_stimulate.insert(0, innervation_node_global+1)
        for node in nodes_to_stimulate:
            states[(node,0,0)] = vm_value_stimulated
