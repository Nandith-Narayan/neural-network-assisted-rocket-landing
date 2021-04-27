# neural-network-assisted-rocket-landing
An agent that  attempts to land a simulated rocket using a neural network trained by a genetic algorithm

### Video demonstrations have been recorded in the "Videos" folder.

## RUN Instructions

Make sure KSP is running with the kRPC mod enabled.
The RPC and stream ports are 5000 and 5001 respectively

```
python lander.py
```


## Unity Simulation build instructions:

	Method 1(requires additional libraries):
		Install Unity from their website (Personal edition is what we used, it's Free)
		Import the Unity project from code/Unity Simulation/src/Lander
		Press the run button at the top
	Method 2(Easy):
		run the executable in code/Unity Simulation/windows build/Lander.exe
		Warning: the executable is built only for 64-bit Windows 10.


## KSP Build Instructions and library requirements:
	"Kerbal Space Program" is required.
	The "kRPC" mod must be installed and enabled in Kerbal Space Program(KSP)
	The "kRPC" python client must also be installed using pip: "pip install krpc"
	Python 3.6 or higher is required.
	Once all the libraries are installed, make sure the file "nn.txt" which contains the trained neural network, is in the same directory as the python script.
	To run the python script, use the command "python3 lander.py" Make sure KSP is running first and the kRPC server is running.
