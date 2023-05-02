# Bachelorforschungsprojekt Muskelsimulation

## opendihu cases
The folder opendihu contains 4 cases:
- muscle_only: A muscle with no fibers solved using MuscleContractionSolver
- fibers_only: Activation of multiple fibers without a muscle mesh using FastMonodomainSolver. 
- muscle_contraction: Coupling of fibers and muscle using opendihu
- precice_contracion: Coupling of fibers and muscle using precice
The folder also contains a variables folder with some possible configurations.
To run a case, the name of one of the configurations in this folder has to be added as a second command line argument.
If no second argument is provided, the configuration "variables.py" is used by default.
For example, "./muscle_only ../settings.py neumann.py" runs the muscle mechanics with a neumann pulling force on one end.
Note that all the cases use the same set of configuration files.
Instead of changing one of the existing configuration files, it should be preferred to copy it and modify the copy instead. 
