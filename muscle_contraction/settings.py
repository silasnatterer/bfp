scenario = "muscle_contraction"

# Create Meshes
nx, ny, nz = 12, 4, 4
mx, my, mz = 2*nx+1, 2*ny+1, 2*nz+1 # Quadratic basis functions
meshes = {
    "3Dmesh": {
        "nElements":            [nx, ny, nz],       # Number of elements in x, y and z direction
        "physicalExtent":       [nx, ny, nz],       # Extent of the mesh in [m]
        "physicalOffset":       [0.0, 0.0, 0.0],    # Offset of the mesh in [m]
        "inputMeshIsGlobal":    True                # whether values describe global domain or local subdomain
    }
}

# Create Solvers
solvers = {
    "nonlinear": {
        "relativeTolerance":            1e-10,      # 1e-10 relative tolerance of the linear solver
        "absoluteTolerance":            1e-10,      # 1e-10 absolute tolerance of the residual of the linear solver
        "solverType":                   "preonly",  # type of the linear solver
        "preconditionerType":           "lu",       # type of the preconditioner
        "maxIterations":                1e4,        # maximum number of iterations in the linear solver
        "snesMaxFunctionEvaluations":   1e8,        # maximum number of function iterations
        "snesMaxIterations":            10,         # maximum number of iterations in the nonlinear solver
        "snesRelativeTolerance":        1e-5,       # relative tolerance of the nonlinear solver
        "snesLineSearchType":           "l2",       # type of linesearch, possible values: "bt" "nleqerr" "basic" "l2" "cp" "ncglinear"
        "snesAbsoluteTolerance":        1e-5,       # absolute tolerance of the nonlinear solver
        "snesRebuildJacobianFrequency": 10,         # how often the jacobian should be recomputed
        "dumpFilename":                 "",         # filename of vector and matrix dump, "" means disabled
        "dumpFormat":                   "matlab",   # format of vector and matrix dump
    }
}

# Material parameters
c1 = 3.176e-10              # [N/cm^2]
c2 = 1.813                  # [N/cm^2]
b  = 1.075e-2               # [N/cm^2] anisotropy parameter
d  = 9.1733                 # [-] anisotropy parameter
material = [c1, c2, b, d]   # material parameters
pmax = 7.3                  # [N/cm^2] maximum isometric active stress
density = 1.0

# Dirichlet boundary condition
dirichlet = {}
for k in range(mz):
  for j in range(my):
    dirichlet[k*mx*my + j*mx] = [0.0, 0.0, 0.0, None, None, None]   # Fix x=0

# Neumann boundary condition
neumann = []
force = 25
for k in range(nz):
    for j in range(ny):
        neumann += [{"element": k*nx*ny + j*nx + nx-1, "constantVector": [force,0,0], "face": "0+"}]    # Force at x=nx-1

# Initial conditions
initDisplacement = [[0.0, 0.0, 0.0] for _ in range(mx*my*mz)]   # No initial displacement
initVelocity = [[0.0, 0.0, 0.0] for _ in range(mx*my*mz)]       # No initial velocity
constantForce = (0.0, 0.0, 0.0)                                 # No constant force

# Time stepping parameters
timesteps = 250
dt = 0.5
output_interval = dt

# Create config
config = {
  "scenarioName": scenario,                                             # specifier to find simulation run in log file
  "logFormat": "csv",                                                   # "csv" or "json", format of the lines in the log file, csv gives smaller files
  "solverStructureDiagramFile": "solver_structure.txt",                 # output file of a diagram that shows data connection between solvers
  "mappingsBetweenMeshesLogFile": "mappings_between_meshes_log.txt",    # log file for mappings 

  "Meshes": meshes,     # Set meshes
  "Solvers": solvers,   # Set solvers

  "MuscleContractionSolver": {
      "numberTimeSteps": timesteps,                         # number of timesteps per call
      "timeStepOutputInterval": 100,                        # how often the current time step is displayed
      "Pmax": pmax,                                         # maximum PK2 active stress
      "enableForceLengthRelation": True,                    # set to false if force-length relation is already considered in CellML model
      "lambdaDotScalingFactor": 1.0,                        # scaling factor of the lambda dot slot (contraction velocity)
      "mapGeometryToMeshes": [],                            # the mesh names of the meshes that will get the geometry transferred
      "slotNames": ["lambda", "ldot", "gamma", "T"],        # names of the connector slots
      "dynamic": True,                                      # whether to use dynamic or static solver

      # Output writer with all required fields
      "OutputWriter": [
          {"format": "Paraview", "outputInterval": int(1.0/dt*output_interval), "filename": "out/mechanics3D", "binary": True, "fixedFormat": False, "onlyNodalValues": True, "combineFiles": True, "fileNumbering": "incremental"}
       ],
    
    "DynamicHyperelasticitySolver": {
        "timeStepWidth": dt,                  # time step width 
        "durationLogKey": "nonlinear",        # key to find duration of this solver in the log file
        "timeStepOutputInterval": 1,          # how often the current time step should be printed to console
    
        "materialParameters": material,                     # material parameters of the Mooney-Rivlin material
        "density": density,                                 # density of the material
        "displacementsScalingFactor": 1.0,                  # scaling factor for displacements, only set to sth. other than 1 only to increase visual appearance for very small displacements
        "residualNormLogFilename": "log_residual_norm.txt", # log file where residual norm values of the nonlinear solver will be written
        "useAnalyticJacobian": True,                        # whether to use the analytically computed jacobian matrix in the nonlinear solver (fast)
        "useNumericJacobian": False,                        # whether to use the numerically computed jacobian matrix in the nonlinear solver (slow)
        "dumpDenseMatlabVariables": False,                  # whether to have extra output of matlab vectors, x,r, jacobian matrix (very slow)
    
        "meshName": "3Dmesh",                   # Selected mesh
        "inputMeshIsGlobal": True,              # whether boundary conditions are specified locally or globally
        "fiberMeshNames": [],                   # fiber meshes that will be used to determine the fiber direction
        "fiberDirection": [0, 0, 0],            # if fiberMeshNames is empty, directly set the constant fiber direction
        "fiberDirectionInElement": [0, 0, 1],   # direction of fiber in element
        "solverName": "nonlinear",              # Selected solver
        "loadFactors": [],                      # no load factors, solve problem directly
        "loadFactorGiveUpThreshold": 0.1,       # if the adaptive time stepping produces a load factor smaller than this value, the solution will be accepted for the current timestep
        "nNonlinearSolveCalls": 1,              # how often the nonlinear solve should be called
    
        "dirichletBoundaryConditions": dirichlet,                           # the initial Dirichlet boundary conditions that define values for displacements u and velocity v
        "dirichletOutputFilename": "out/dirichlet_boundary_conditions",     # filename for a vtp file that contains the Dirichlet boundary condition nodes and their values, set to None to disable
        "neumannBoundaryConditions": neumann,                               # Neumann boundary conditions that define traction forces on surfaces of elements
        "divideNeumannBoundaryConditionValuesByTotalArea": True,            # if the given Neumann boundary condition values should be scaled by the surface area of all elements where Neumann BC are applied
        "constantBodyForce": constantForce,                                 # a constant force that acts on the whole body, e.g gravity
        "initialValuesDisplacements": initDisplacement,                     # initial values for the displacement
        "initialValuesVelocities": initVelocity,                            # initial values for the velocity 
        "extrapolateInitialGuess": True,                                    # if the initial values for the dynamic nonlinear problem should be computed by extrapolating
    
        "totalForceLogFilename":  "out/total_force.csv",    # filename of a log file that will contain the total (bearing) forces and moments at the top and bottom of the volume
        "totalForceLogOutputInterval": 10,                  # output interval when to write the totalForceLog file

        # Define which file formats should be written
        # 1. main output writer that writes output files using the quadratic elements function space. Writes displacements, velocities and PK2 stresses.
        "OutputWriter" : [
            # Paraview files
            #{"format": "Paraview", "outputInterval": 1, "filename": "out/u", "binary": False, "fixedFormat": False, "onlyNodalValues":True, "combineFiles":True, "fileNumbering": "incremental"},
        ],
        # 2. additional output writer that writes also the hydrostatic pressure
        "pressure": {   # output files for pressure function space (linear elements), contains pressure values, as well as displacements and velocities
            "OutputWriter" : [
                #{"format": "Paraview", "outputInterval": 1, "filename": "out/p", "binary": False, "fixedFormat": False, "onlyNodalValues":True, "combineFiles":True, "fileNumbering": "incremental"},
            ]
        },
        # 3. additional output writer that writes virtual work terms
        "dynamic": {    # output of the dynamic solver, has additional virtual work values
            "OutputWriter" : [   # output files for displacements function space (quadratic elements)
            #{"format": "Paraview", "outputInterval": int(output_interval/dt), "filename": "out/dynamic", "binary": False, "fixedFormat": False, "onlyNodalValues":True, "combineFiles":True, "fileNumbering": "incremental"},
            #{"format": "Paraview", "outputInterval": 1, "filename": "out/dynamic", "binary": False, "fixedFormat": False, "onlyNodalValues":True, "combineFiles":True, "fileNumbering": "incremental"},
            ],
        },
        # 4. output writer for debugging, outputs files after each load increment, the geometry is not changed but u and v are written
        "LoadIncrements": {
            "OutputWriter" : [
                #{"format": "Paraview", "outputInterval": 1, "filename": "out/load_increments", "binary": False, "fixedFormat": False, "onlyNodalValues":True, "combineFiles":True, "fileNumbering": "incremental"},
            ]
        }
    }
  }
}
