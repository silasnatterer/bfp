import sys
import os
import importlib

# parse arguments
rank_no = (int)(sys.argv[-2])
n_ranks = (int)(sys.argv[-1])
var_file = sys.argv[0] if ".py" in sys.argv[0] else "variables.py"

# add folders to python path
script_path = os.path.dirname(os.path.abspath(__file__))
var_path = os.path.join(script_path, "variables")
sys.path.insert(0, script_path)
sys.path.insert(0, var_path)

# load variables file
var_module, _ = os.path.splitext(var_file)
variables = importlib.import_module(var_module, package=var_file)

# define config
config = {
  "scenarioName":                   variables.scenario_name,

  "logFormat":                      "csv",
  "mappingsBetweenMeshesLogFile":   "out/" + variables.scenario_name + "/muscle_contraction/mappings_between_meshes_log.txt",
  "solverStructureDiagramFile":     "out/" + variables.scenario_name + "/muscle_contraction/solver_structure_diagram.txt",
  
  "Meshes":                         variables.meshes,
  "MappingsBetweenMeshes":          {},

  "Solvers": {
    "mechanicsSolver": {
      "solverType":                     "preonly",
      "preconditionerType":             "lu",
      "relativeTolerance":              1e-10,
      "absoluteTolerance":              1e-10,
      "maxIterations":                  1e4,
      "snesLineSearchType":             "l2",
      "snesRelativeTolerance":          1e-5,
      "snesAbsoluteTolerance":          1e-5,
      "snesMaxIterations":              10,
      "snesMaxFunctionEvaluations":     1e8,
      "snesRebuildJacobianFrequency":   5,
      "dumpFilename":                   "",
      "dumpFormat":                     "matlab"
    }
  },

  "PreciceAdapterVolumeCoupling": {
    "preciceConfigFilename":        "../precice_config.xml",
    "preciceParticipantName":       "MuscleContraction",
    "couplingEnabled":              True,
    "timeStepOutputInterval":       100,
    "timestepWidth":                1,
    "scalingFactor":                1,
    "outputOnlyConvergedTimeSteps": True,

    "preciceData": [
      {
        "mode":             "write",
        "preciceDataName":  "Geometry",
        "preciceMeshName":  "MuscleContractionMesh",
        "opendihuMeshName": None,
        "slotName":         None,
        "isGeometryField":  True
      },
      {
        "mode":             "read",
        "preciceDataName":  "Gamma",
        "preciceMeshName":  "MuscleContractionMesh",
        "opendihuMeshName": None,
        "slotName":         "gamma",
        "isGeometryField":  False
       }
    ],

    "MuscleContractionSolver": {
      "Pmax":                         variables.pmax,
      "slotNames":                    ["lambda", "ldot", "gamma", "T"],
      "dynamic":                      True,

      "numberTimeSteps":              1,
      "timeStepOutputInterval":       100,
      "lambdaDotScalingFactor":       1,
      "enableForceLengthRelation":    True,
      "mapGeometryToMeshes":          [],

      "OutputWriter": [
        {
          "format":             "Paraview",
          "outputInterval":     int(1.0 / variables.dt_3D),
          "filename":           "out/" + variables.scenario_name + "/muscle_contraction/mechanics",
          "fileNumbering":      "incremental", 
          "binary":             True,
          "fixedFormat":        False,
          "onlyNodalValues":    True,
          "combineFiles":       True
        }
      ],

      "DynamicHyperelasticitySolver": { 
        "durationLogKey":         "duration_3D",
        "logTimeStepWidthAsKey":  "dt_3D",
        "timeStepWidth":          variables.dt_3D,
        "materialParameters":     variables.material_parameters,
        "density":                variables.rho,
        "timeStepOutputInterval": 1,

        "meshName":                 "mesh3D",
        "fiberDirectionInElement":  variables.fiber_direction,
        "inputMeshIsGlobal":        True,
        "fiberMeshNames":           [],
        "fiberDirection":           None,

        "solverName":                 "mechanicsSolver",
        "displacementsScalingFactor": 1.0,
        "useAnalyticJacobian":        True,
        "useNumericJacobian":         False,
        "dumpDenseMatlabVariables":   False,
        "loadFactorGiveUpThreshold":  4e-2,
        "loadFactors":                [],
        "scaleInitialGuess":          False,
        "extrapolateInitialGuess":    True,
        "nNonlinearSolveCalls":       1,

        "dirichletBoundaryConditions":                            variables.dirichlet_bc,
        "neumannBoundaryConditions":                              variables.neumann_bc,
        "updateDirichletBoundaryConditionsFunction":              None,
        "updateDirichletBoundaryConditionsFunctionCallInterval":  1,
        "divideNeumannBoundaryConditionValuesByTotalArea":        True,

        "initialValuesDisplacements": [[0, 0, 0] for _ in range(variables.bs_x * variables.bs_y * variables.bs_z)],
        "initialValuesVelocities":    [[0, 0, 0] for _ in range(variables.bs_x * variables.bs_y * variables.bs_z)],
        "constantBodyForce":          (0, 0, 0),

        "dirichletOutputFilename":    "out/" + variables.scenario_name + "/muscle_contraction/dirichlet_output",
        "residualNormLogFilename":    "out/" + variables.scenario_name + "/muscle_contraction/residual_norm_log.txt",
        "totalForceLogFilename":      "out/" + variables.scenario_name + "/muscle_contraction/total_force_log.txt",

        "OutputWriter": [],
        "pressure":       { "OutputWriter": [] },
        "dynamic":        { "OutputWriter": [] },
        "LoadIncrements": { "OutputWriter": [] }
      }
    }
  }
}
