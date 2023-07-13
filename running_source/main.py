from openmodelica import Ompy_run
from openmodelica import ex_result
from OMPython import OMCSessionZMQ
from OMEngineUnits.OMcompile import wrap_mo_to_fmu
import os


if __name__ == '__main__':
    # Connect to OpenModelica
    '''
    omc = OMCSessionZMQ()

    # Load the model
    model_name = "DataCenterContinuousTimeControl"

    # run the function
    Ompy_run(omc, model_name)
    ex_result(omc, model_name)
    '''
    omc = OMCSessionZMQ()
    model_name = "Test_Wuxi_WPF_05010508"
    fmu_dir = './fmu_doc'
    model_file = f"{model_name}.mo"
    output_path = f"{fmu_dir}"

    wrap_mo_to_fmu(model_name, model_file, output_path)

