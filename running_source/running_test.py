
'''
from OMPython import OMCSessionZMQ

# Connect to OpenModelica
omc = OMCSessionZMQ()

# Load the model
model_name = "DataCenterContinuousTimeControl"
omc.sendExpression(f"loadModel(Modelica);")
omc.sendExpression(f"loadFile(\"{model_name}.mo\");")

# Set simulation options
omc.sendExpression(f"setCommandLineOptions(\"+s=ode\", \"+simCodeTarget=Python\");")
omc.sendExpression(f"setStopTime(10.0);")

# Simulate the model
omc.sendExpression(f"simulate({model_name});")

# Extract simulation results
result = omc.sendExpression(f"getErrorString();")
print(result)
'''
from OMPython import OMCSessionZMQ

# Connect to OpenModelica
omc = OMCSessionZMQ()

# Load the model
model_name = "Test_Wuxi_WPF_05010508"
omc.sendExpression(f"loadModel(Modelica);")
omc.sendExpression(f"loadFile(\"{model_name}.mo\");")

# Set simulation options
omc.sendExpression(f"setCommandLineOptions(\"+s=ode\", \"+simCodeTarget=Python\");")
omc.sendExpression(f"setStopTime(1000.0);")

# Simulate the model
omc.sendExpression(f"simulate({model_name});")

# Check if simulation results exist
result_exists = omc.sendExpression(f"existSimulationResult({model_name})")
if result_exists:
    # Extract simulation results
    result = omc.sendExpression(f"readSimulationResult({model_name}, \"\")")
    print(result)
else:
    print("Simulation results do not exist.")
