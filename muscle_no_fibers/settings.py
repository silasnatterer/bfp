# Linear elasticity
# Use paraview and the Warp Filter for visualization.
# Add a Glyph filter with arrows for field "-rhsNeumannBC", this is the applied traction.

import numpy as np

nx = 12
ny = 4
nz = 4

dirichlet_bc = {}
for k in range(0, 2*nz + 1):
  for j in range(0, 2*ny + 1):
    dirichlet_bc[(k * (2*ny + 1) + j) * (2*nx + 1)] = [0, 0, 0, None, None, None]

neumann_bc = []
for k in range(0, nz):
  for j in range(0, ny):
    neumann_bc.append({
    "element": (k * ny + j) * nx + nx - 1,               # local element no, negative values count from the end
    "face": "0+",               # face on which the neumann bc should act
    "constantValue": 0.5,
    "isInReferenceConfiguration": True,  # for dynamic hyperelasticity, if the traction is interpreted as specified in reference configuration or current configuration
  })

config = {
  "scenarioName":                   "muscle_no_fibers",    # scenario name for the log file
  "logFormat":                      "csv",     # "csv" or "json", format of the lines in the log file, csv gives smaller files
  "solverStructureDiagramFile":     "solver_structure.txt",     # output file of a diagram that shows data connection between solvers
  "mappingsBetweenMeshesLogFile":   "mappings_between_meshes.txt",   # log file for mappings between meshes
  "DynamicHyperelasticitySolver": {
    "timeStepWidth":              1,      # time step width
    "endTime":                    10,           # end time of the simulation time span
    "durationLogKey":             "duration_mechanics",         # key to find duration of this solver in the log file
  "useAnalyticJacobian":        True,                         # whether to use the analytically computed jacobian matrix in the nonlinear solver (fast)
  "useNumericJacobian":         False,                        # whether to use the numerically computed jacobian matrix in the nonlinear solver (slow), only works with non-nested matrices, if both numeric and analytic are enable, it uses the analytic for the preconditioner and the numeric as normal jacobian

    "materialParameters":         [0.3, 0.7],  # material parameters of the Mooney-Rivlin material
  
    # mesh
    "nElements":                  [nx, ny, nz],                 # number of elements in the 2 coordinate directions  
    "inputMeshIsGlobal":          True,                     # if the specifiation of the mesh is given in global numbers
    "physicalExtent":             [nx, ny, nz],                 # the physical dimensions of the mesh, in this case the same as the number of elements
    "physicalOffset":             [0, 0, 0],                # lower left bottom coordinates of the mesh

    # nonlinear solver
    "relativeTolerance":          1e-5,                         # 1e-10 relative tolerance of the linear solver
    "absoluteTolerance":          1e-10,                        # 1e-10 absolute tolerance of the residual of the linear solver
    "solverType":                 "preonly",                    # type of the linear solver: cg groppcg pipecg pipecgrr cgne nash stcg gltr richardson chebyshev gmres tcqmr fcg pipefcg bcgs ibcgs fbcgs fbcgsr bcgsl cgs tfqmr cr pipecr lsqr preonly qcg bicg fgmres pipefgmres minres symmlq lgmres lcd gcr pipegcr pgmres dgmres tsirm cgls
    "preconditionerType":         "lu",                         # type of the preconditioner
    "maxIterations":              1e4,                          # maximum number of iterations in the linear solver
    "snesMaxFunctionEvaluations": 1e8,                          # maximum number of function iterations
    "snesMaxIterations":          10,                           # maximum number of iterations in the nonlinear solver
    "snesRelativeTolerance":      1e-5,                         # relative tolerance of the nonlinear solver
    "snesLineSearchType":         "l2",                         # type of linesearch, possible values: "bt" "nleqerr" "basic" "l2" "cp" "ncglinear"
    "snesAbsoluteTolerance":      1e-5,                         # absolute tolerance of the nonlinear solver
    "snesRebuildJacobianFrequency": 5,                          # how often the jacobian should be recomputed, -1 indicates NEVER rebuild, 1 means rebuild every time the Jacobian is computed within a single nonlinear solve, 2 means every second time the Jacobian is built etc. -2 means rebuild at next chance but then never again

    #"dumpFilename": "out/r{}/m".format(sys.argv[-1]),          # dump system matrix and right hand side after every solve
    "dumpFilename":               "",                           # dump disabled
    "dumpFormat":                 "matlab",                     # default, ascii, matlab

    #"loadFactors":                [0.1, 0.2, 0.35, 0.5, 1.0],   # load factors for every timestep
    #"loadFactors":                [0.5, 1.0],                   # load factors for every timestep
    "loadFactors":                [],                           # no load factors, solve problem directly
    "loadFactorGiveUpThreshold":  4e-2,                         # a threshold for the load factor, when to abort the solve of the current time step. The load factors are adjusted automatically if the nonlinear solver diverged. If the progression between two subsequent load factors gets smaller than this value, the solution is aborted.
    "scaleInitialGuess":          False,                        # when load stepping is used, scale initial guess between load steps a and b by sqrt(a*b)/a. This potentially reduces the number of iterations per load step (but not always).
    "nNonlinearSolveCalls":       1,                            # how often the nonlinear solve should be called

    # boundary and initial conditions
    "dirichletBoundaryConditions": dirichlet_bc,   # the initial Dirichlet boundary conditions that define values for displacements u and velocity v
    "neumannBoundaryConditions":   neumann_bc,     # Neumann boundary conditions that define traction forces on surfaces of elements
    "divideNeumannBoundaryConditionValuesByTotalArea": False,            # if the given Neumann boundary condition values under "neumannBoundaryConditions" are total forces instead of surface loads and therefore should be scaled by the surface area of all elements where Neumann BC are applied
    "updateDirichletBoundaryConditionsFunction": None,                  # function that updates the dirichlet BCs while the simulation is running
    "updateDirichletBoundaryConditionsFunctionCallInterval": 1,         # every which step the update function should be called, 1 means every time step
    "updateNeumannBoundaryConditionsFunction": None,                    # function that updates the Neumann BCs while the simulation is running
    "updateNeumannBoundaryConditionsFunctionCallInterval": 1,           # every which step the update function should be called, 1 means every time step

    "OutputWriter": [
      {"format": "Paraview", "outputInterval": 1, "filename": "out/2d", "binary": False, "fixedFormat": False, "onlyNodalValues":True, "combineFiles":True, "fileNumbering": "incremental"},
      {"format": "PythonFile", "filename": "out/2d", "outputInterval": 1, "binary":False, "onlyNodalValues":True, "fileNumbering": "incremental"},
    ],
    # 2. additional output writer that writes also the hydrostatic pressure
    "pressure": {   # output files for pressure function space (linear elements), contains pressure values, as well as displacements and velocities
      "OutputWriter" : [
        #{"format": "Paraview", "outputInterval": 1, "filename": "out/"+variables.scenario_name+"/p", "binary": True, "fixedFormat": False, "onlyNodalValues":True, "combineFiles":True, "fileNumbering": "incremental"},
      ]
    },
    # 3. additional output writer that writes virtual work terms
    "dynamic": {    # output of the dynamic solver, has additional virtual work values
      "OutputWriter" : [   # output files for displacements function space (quadratic elements)
        {"format": "Paraview", "outputInterval": 1, "filename": "out/muscle_no_fibers/dynamic", "binary": True, "fixedFormat": False, "onlyNodalValues":True, "combineFiles":True, "fileNumbering": "incremental"},
        #{"format": "Paraview", "outputInterval": 1, "filename": "out/"+variables.scenario_name+"/virtual_work", "binary": True, "fixedFormat": False, "onlyNodalValues":True, "combineFiles":True, "fileNumbering": "incremental"},
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
