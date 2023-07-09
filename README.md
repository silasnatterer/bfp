# Bachelorforschungsprojekt Muskelsimulation

## opendihu cases
The folder opendihu contains 4 cases:
- muscle_only: A muscle with no fibers solved using MuscleContractionSolver
- fibers_only: Activation of multiple fibers without a muscle mesh using FastMonodomainSolver. 
- muscle_contraction: Coupling of fibers and muscle using opendihu
- precice_contracion: Coupling of fibers and muscle using precice
- febio_contraction: Coupling of febio and opendihu

The folder also contains a variables folder with some possible configurations.
To run a case, the name of one of the configurations in this folder has to be added as a second command line argument.
If no second argument is provided, the configuration "variables.py" is used by default.
For example, "./muscle_only ../settings.py neumann.py" runs the muscle mechanics with a neumann pulling force on one end.
Note that all the cases use the same set of configuration files.
Instead of changing one of the existing configuration files, it should be preferred to copy it and modify the copy instead. 

## opendihu and febio cases
The folder opendihu_febio contains two cases for comparison between opendihu and FEBioStudio:
- [...]/muscle_no_fibers: A muscle without fibers being fixed on one side and being pulled with increasing force on the other side
- [...]/muscle_contraction: A muscle with fibers and active contraction

The folders are divided into two subfolders, each containing cases for one of the programs.
Since the cases are meant to compare opendihu and FEBioStudio with each other, there is little to configurate.
In the folder of the FEBioStudio case there is a "conversion.txt" file, providing how the different parameters are adapted from opendihu to febio.
