import os
import subprocess

from OMlogger import Logger

def wrap_mo_to_fmu(model_name, model_file, output_path):
    log_level = 'INFO'
    LOG_FMT = "[%(asctime)s] %(name)s %(levelname)s:%(message)s";
    # 检查输出目录是否存在，如果不存在则创建
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        Logger().getLogger('Fmu File not exist'.format(model_name, log_level, LOG_FMT))

    # 构建 omc 命令
    cmd = ['omc', '-s', '-d=initialization', '-q', '-n=loadModel(Modelica);instantiateModel({},"{}")'.format(model_name, model_file)]

    # 执行 omc 命令
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # 检查是否有错误输出
    if stderr:
        print("封装模型出错：", stderr.decode("utf-8"))
    else:
        # 获取封装后的 FMU 文件路径
        fmu_path = os.path.join(output_path, model_name + ".fmu")

        # 构建命令行封装命令
        cmd = ['omc', '-s', '-d=fmi', '-q', '-n=generateFMU({{"startTime"=0.0, "stopTime"=1.0}}, "{}", "{}")'.format(model_name, fmu_path)]

        # 执行封装命令
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # 检查是否有错误输出
        if stderr:
            print("封装为 FMU 出错：", stderr.decode("utf-8"))
        else:
            print("成功封装为 FMU：", fmu_path)

