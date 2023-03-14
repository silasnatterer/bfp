import sys
import os
import itertools
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
  "mappingsBetweenMeshesLogFile":   "out/" + variables.scenario_name + "/mappings_between_meshes.txt",
  "solverStructureDiagramFile":     "out/" + variables.scenario_name + "/solver_structure.txt",
  
  "Meshes":                         variables.meshes,
  "MappingsBetweenMeshes":          variables.mappings_between_meshes,

  "Solvers":                        variables.solvers,

  "Coupling": {
    "timeStepWidth":            variables.dt_3D,
    "logTimeStepWidthAsKey":    "dt_3D",
    "durationLogKey":           "duration_3D",
    "timeStepOutputInterval":   1,
    "endTime":                  variables.end_time,
    "connectedSlotsTerm1To2":   {1:2},  # transfer gamma to MuscleContractionSolver
    "connectedSlotsTerm2To1":   None,   # transfer nothing back

    "Term1": { # fibers (FastMonodomainSolver)
      "MultipleInstances": { # subdomains
        "logKey":                       "duration_subdomains_xy",
        "ranksAllComputedInstances":    list(range(n_ranks)),
        "nInstances":                   variables.n_subdomains_x * variables.n_subdomains_y,
        "instances": [{
          "ranks": list(range(subdomain_y*variables.n_subdomains_x + subdomain_x, n_ranks, variables.n_subdomains_x*variables.n_subdomains_y)),

          "StrangSplitting": {
            "timeStepWidth":            variables.dt_splitting,
            "logTimeStepWidthAsKey":    "dt_splitting",
            "durationLogKey":           "duration_splitting",
            "timeStepOutputInterval":   100,
            "endTime":                  variables.dt_splitting,
            "connectedSlotsTerm1To2":   None,
            "connectedSlotsTerm2To1":   None,

            "Term1": { # reaction term
              "MultipleInstances": {
                "logKey":       "duration_subdomains_z",
                "nInstances":   variables.n_fibers_in_subdomain_x(subdomain_x) * variables.n_fibers_in_subdomain_y(subdomain_y),
                "instances": [{
                  "ranks": list(range(variables.n_subdomains_z)),

                  "Heun": {
                    "timeStepWidth":            variables.dt_0D,
                    "logTimeStepWidthAsKey":    "dt_0D",
                    "durationLogKey":           "duration_0D",

                    "timeStepOutputInterval":       1e4,
                    "initialValues":                [],
                    "dirichletBoundaryConditions":  {},
                    "dirichletOutputFilename":      None,
                    "inputMeshIsGlobal":            True,
                    "checkForNanInf":               True,
                    "nAdditionalFieldVariables":    0,
                    "additionalSlotNames":          [],
                    "OutputWriter":                 [],

                    "CellML": { # hodgkin-huxley-razumova cellml
                      "modelFilename": variables.input_dir + "hodgkin_huxley-razumova.cellml",

                      "statesInitialValues":                        [],
                      "initializeStatesToEquilibrium":              False,
                      "initializeStatesToEquilibriumTimeStepWidth": 1e-4,
                      "optimizationType":                           "vc",
                      "approximateExponentialFunction":             True,
                      "compilerFlags":                              "-fPIC -O3 -march=native -Wno-deprecated_declarations -shared",
                      "maximumNumberOfThreads":                     0,

                      "setSpecificStatesFunction":              None,
                      "setSpecificStatesCallInterval":          0,
                      "setSpecificStatesCallFrequency":         variables.get_specific_states_call_frequency(variables.get_fiber_no(subdomain_x, subdomain_y, fiber_x, fiber_y)),
                      "setSpecificStatesFrequencyJitter":       variables.get_specific_states_frequency_jitter(variables.get_fiber_no(subdomain_x, subdomain_y, fiber_x, fiber_y)),
                      "setSpecificStatesCallEnableBegin":       variables.get_specific_states_call_enable_begin(variables.get_fiber_no(subdomain_x, subdomain_y, fiber_x, fiber_y)),
                      "setSpecificStatesRepeatAfterFirstCall":  0.01,
                      "additionalArgument":                     variables.get_fiber_no(subdomain_x, subdomain_y, fiber_x, fiber_y),

                      "mappings": {
                        ("parameter", 0):               "membrane/i_Stim",
                        ("parameter", 1):               "Razumova/l_hs",
                        ("parameter", 2):               ("constant", "Razumova/rel_velo"),
                        ("connectorSlot", "vm"):        "membrane/V",
                        ("connectorSlot", "stress"):    "Razumova/activestress",
                        ("connectorSlot", "alpha"):     "Razumova/activation",
                        ("connectorSlot", "lambda"):    "Razumova/l_hs",
                        ("connectorSlot", "ldot"):      "Razumova/rel_velo"
                      },
                      "parametersInitialValues": [0.0, 1.0, 0.0],

                      "meshName":               variables.fiber_mesh_names[variables.get_fiber_no(subdomain_x, subdomain_y, fiber_x, fiber_y)],
                      "stimulationLogFilename": "out/stimulation.log"
                    },
                  }
                } for fiber_x, fiber_y in itertools.product(range(variables.n_fibers_in_subdomain_x(subdomain_x)), range(variables.n_fibers_in_subdomain_y(subdomain_y)))]
              }
            },

            "Term2": { # diffusion term
              "MultipleInstances": {
                "nInstances": variables.n_fibers_in_subdomain_x(subdomain_x) * variables.n_fibers_in_subdomain_y(subdomain_y),
                "instances": [{
                  "ranks": list(range(variables.n_subdomains_z)),

                  "ImplicitEuler": {
                    "timeStepWidth":            variables.dt_1D,
                    "logTimeStepWidthAsKey":    "dt_1D",
                    "durationLogKey":           "duration_1D",

                    "nAdditionalFieldVariables":    4,
                    "additionalSlotNames":          ["stress", "alpha", "lambda", "ldot"],

                    "solverName":                       variables.diffusion_solver_name,
                    "timeStepOutputInterval":           1e4,
                    "timeStepWidthRelativeTolerance":   1e-10,
                    "dirichletBoundaryConditions":      {},
                    "dirichletOutputFilename":          None,
                    "inputMeshIsGlobal":                True,
                    "checkForNanInf":                   True,
                    "OutputWriter":                     [],

                    "FiniteElementMethod": {
                      "inputMeshIsGlobal":  True,
                      "meshName":           variables.fiber_mesh_names[variables.get_fiber_no(subdomain_x, subdomain_y, fiber_x, fiber_y)],
                      "solverName":         variables.diffusion_solver_name,
                      "prefactor":          variables.get_diffusion_prefactor(variables.get_fiber_no(subdomain_x, subdomain_y, fiber_x, fiber_y)),
                      "slotName":           "vm"
                    }
                  }
                } for fiber_x, fiber_y in itertools.product(range(variables.n_fibers_in_subdomain_x(subdomain_x)), range(variables.n_fibers_in_subdomain_y(subdomain_y)))],

                "OutputWriter": variables.output_writer_fibers
              }
            }
          }
        } for subdomain_x, subdomain_y in itertools.product(range(variables.n_subdomains_x), range(variables.n_subdomains_y))]
      },

      # settings for FastMonodomainSolver
      "fiberDistributionFile":                              variables.fiber_distribution_file,
      "firingTimesFile":                                    variables.firing_times_file,
      "valueForStimulatedPoint":                            variables.vm_value_stimulated,
      "onlyComputeIfHasBeenStimulated":                     True,
      "disableComputationWhenStatesAreCloseToEquilibrium":  True,
      "neuromuscularJunctionRelativeSize":                  0.1,
      "generateGPUSource":                                  True,
      "useSinglePrecision":                                 False
    },

    "Term2": { # solid mechanics (MuscleContractionSolver)
      "MuscleContractionSolver": {
        "numberTimeSteps":              1,
        "timeStepOutputInterval":       100,
        "Pmax":                         variables.pmax,
        "enableForceLengthRelation":    True,
        "lambdaDotScalingFactor":       1,
        "dynamic":                      True,
        "mapGeometryToMeshes":          [],
        "slotNames":                    ["lambda", "ldot", "gamma", "T"],
        "OutputWriter":                 variables.output_writer_mechanics,

        "DynamicHyperelasticitySolver": { # actual 3D mechanics solver
          "timeStepWidth":          variables.dt_3D,
          "durationLogKey":         "mechanics",
          "timeStepOutputInterval": 1,

          "materialParameters":         variables.material_parameters,
          "density":                    variables.rho,
          "displacementsScalingFactor":  1.0,
          "residualNormLogFilename":    "log_residual_norm.txt",
          "useAnalyticJacobian":        True,
          "useNumericJacobian":         False,
          "dumpDenseMatlabVariables":   False,

          "inputMeshIsGlobal":  True,
          "meshName":           variables.mesh3D_name,
          "fiberMeshNames":     variables.fiber_mesh_names,

          "solverName":                 variables.mechanics_solver_name,
          "loadFactorGiveUpThreshold":  1,
          "loadFactors":                [],
          "scaleInitialGuess":          False,
          "nNonlinearSolveCalls":       1,

          "dirichletBoundaryConditions":                            variables.dirichlet_bc,
          "neumannBoundaryConditions":                              variables.neumann_bc,
          "updateDirichletBoundaryConditionsFunction":              None,
          "updateDirichletBoundaryConditionsFunctionCallInterval":  1,
          "divideNeumannBoundaryConditionValuesByTotalArea":        True,

          "initialValuesDisplacements": variables.init_displacement,
          "initialValuesVelocities":    variables.init_velocity,
          "extrapolateInitialGuess":    True,
          "constantBodyForce":          variables.constant_body_force,

          "dirichletOutputFilename":    "out/" + variables.scenario_name + "/dirichlet_boundary_conditions",
          "totalForceLogFilename":      "out/" + variables.scenario_name + "/total_force.txt",

          "OutputWriter": [],
          "pressure":       { "OutputWriter": [] },
          "dynamic":        { "OutputWriter": [] },
          "LoadIncrements": { "OutputWriter": [] }
        }
      }
    }
  }
}
