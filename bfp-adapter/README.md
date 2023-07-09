# FEBio-preCICE adapter

## Installation
The following dependencies are required:
- [preCICE](https://precice.org/installation-overview.html)
- [FEBio](https://febio.org/downloads/)

For the adapter to link against the FEBio SKD successfully you have to perform the following steps:
- Include the SDK when installing FEBio
- Copy FEBioStudio/lib to FEBioStudio/sdk/lib
- Clone the [FEBio git repository](https://github.com/febiosoftware/FEBio) (branch febio4)
- Copy the folders FEAMR, FEBio3, FEBioLib, FEBioOpt, FEBioPlot, FEBioRVE, FEBioTest, FEBioXML, FEImgLib, NumCore and XML from the repository to FEBioStudio/sdk/include
- Set the path in build.sh to your FEBio SDK installation path

You should then be able to compile the adapter by running the build.sh script.

## Usage
First you have to add the following lines to your FEBioStudio/bin/febio.xml:
```xml
<import>pathToAdapter/build/lib/libFEBioPreciceAdapter.so</import>
```
Then you have to add the following to your FEBio model file
```xml
<Code>
	<callback name="precice_callback"\>
</Code>
```
You can then run the case with
```bash
mpirun -n 1 FEBioStudio/bin/febio4 model.feb
```
