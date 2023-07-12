# BFP Plugin for FEBio 

## Installation
The following dependencies are required:
- [preCICE](https://precice.org/installation-overview.html)
- [FEBio](https://febio.org/downloads/)

For the adapter to link against the FEBio SKD successfully you have to perform the following steps:
- Include the SDK when installing FEBio
- Copy FEBioStudio/lib to FEBioStudio/sdk/lib
- Clone the [FEBio git repository](https://github.com/febiosoftware/FEBio) (branch febio4)
- Copy the folders FEAMR, FEBio3, FEBioLib, FEBioOpt, FEBioPlot, FEBioRVE, FEBioTest, FEBioXML, FEImgLib, NumCore and XML from the repository to FEBioStudio/sdk/include
- Set the path in build.sh to your FEBio installation path

You should then be able to compile the plugin by running the build.sh script.
Then you have to add the following lines to your FEBioStudio/bin/febio.xml:
```xml
<import>pathToAdapter/build/lib/libBFPPlugin.so</import>
```

## Usage
For the PreCICE coupling to work you have to add the following lines to your model.feb file 
```xml
<Code>
	<callback name="precice_callback"\>
</Code>
```
In addition you have to change the Material to the custom DiHuMaterial
```xml
<Material>
	<material id="1" name="Material1" type="DiHuMaterial">
		<density>OpenDiHu density</density>
		<k>1000</k>
		<pressure_model>default</pressure_model>
		<c1>OpenDiHu c1 (1st MaterialParameter)</c1>
		<c2>OpenDiHu c2 (2nd Material Parameter)</c2>
		<c3>0</c3>
		<c4>1</c4>
		<c5>OpenDiHu d (4th Material Parameter)</c5>
		<lam_max>1</lam_max>
		<fiber type="vector">
			<vector>Direction of fiber</vector>
		</fiber>
		<active_contraction type="DiHuContraction">
			<pmax>OpenDiHu Pmax</pmax>
		</active_contraction>
	</material>
</Material>
```
Note that the following names are hardcoded in the plugin:
- "Muscle": name of the preCICE participant 
- "MuscleMesh": name of the preCICE mesh
- "Gamma", "Geometry": name of the preCICE fields to couple
- "MusclePart": name of the FEBio part to couple 
By default the adapter will use "../precice-config.xml" for the preCICE config.
To change this, set the "BFP_CONFIG" environment variable.
You can then run the case with
```bash
mpirun -n 1 FEBioStudio/bin/febio4 model.feb
```

