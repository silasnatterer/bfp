# OpenDiHu cases
To run a case, the name of one of the configurations in the variables folder has to be added as a second command line argument.
If no second argument is provided, the configuration "variables.py" is used by default.
For example, "./muscle_only ../settings.py neumann.py" runs the muscle mechanics with a neumann pulling force on one end.
Note that all the cases can use all of the configuration files.
Instead of changing one of the existing configuration files, it should be preferred to copy it and modify the copy instead.

## Cases
The following cases are provided:
- muscle_only: A muscle without any fibers solved using OpenDiHus MuscleContractionSolver.
- fibers_only: Activation of multiple fibers solved using OpenDiHus FastMonodomainSolver.
- muscle_contraction: Full muscle simulation with OpenDiHu using OpenDiHus internal coupling.
- precice_contraction: Full muscle simulation with OpenDiHu using external preCICE coupling.
- febio_contraction: Couples FEBios mechanics solver with OpenDiHus FastMonodomain solver using the preCICE adapter.

## Configuration
The following configuration files are provided:
- variables.py: Default configuration file.
- neumann.py: Similar to variables.py, but includes Neumann pulling force.
- mapping.py: Different results when using preCICE coupling and openDiHu coupling
