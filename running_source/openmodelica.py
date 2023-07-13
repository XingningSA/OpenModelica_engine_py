import matplotlib.pyplot as plt
from OMPython import OMCSessionZMQ
import os

def Ompy_run(omc, model_name):
    omc.sendExpression(f"loadModel(Modelica);")
    omc.sendExpression(f"loadFile(\"{model_name}.mo\");")

    # Set simulation options with custom result file path
    # result_file = os.path.join("/path/to/results", f"{model_name}_res.mat")
    omc.sendExpression(f"setCommandLineOptions(\"+s=ode\", \"+simCodeTarget=Python\");")
    # omc.sendExpression(f"setResultFile(\"{model_name}\", \"{result_file}\");")
    omc.sendExpression(f"setResultFile(\"{model_name}\");")
    omc.sendExpression(f"setStopTime(10.0);")

    # Simulate the model
    omc.sendExpression(f"simulate({model_name});")


def ex_result(omc, model_name):
    # Extract simulation results
    result = omc.sendExpression(f"readSimulationResult(\"{model_name}_res.mat\", \"\")")
    print(result)

    # Plot the results
    time = result["cooTow"]
    variable1 = result["y"]
    variable2 = result["variable2"]

    plt.plot(time, variable1, label="Variable 1")
    plt.plot(time, variable2, label="Variable 2")
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.legend()
    plt.show()


if __name__ == '__main__':
    # Connect to OpenModelica
    omc = OMCSessionZMQ()

    # Load the model
    model_name = "DataCenterContinuousTimeControl"

    # run the function
    Ompy_run(omc, model_name)
    ex_result(omc, model_name)
