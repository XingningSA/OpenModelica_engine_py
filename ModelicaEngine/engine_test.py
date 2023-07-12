from ModelicaEngine import ModelicaEngine
########################################################################
# single modelica file test
#mo_path = '../../MoModels/System1.mo'
#res_dir = './test_modelica1'
#sudo_pwd = '63z64q92zza'
#mo_engine = ModelicaEngine(mo_path, res_dir, sudo_pwd, log_level = 'DEBUG')
## simulate with all result output
#mo_engine.simulate(start_time=0, final_time=3600, res_names = [])
## simulate with some result output
#mo_engine.simulate(start_time=0, final_time=3600, res_names = ['vol.portT.y', 'vol.preTem.T'])
## simulate with some result output and parameter setting
#mo_engine.simulate(start_time=0, final_time=3600,
#	set_param_dict = {'theCon.G': 200, 'V': 300},
#	res_names = ['vol.portT.y', 'vol.preTem.T'])

########################################################################
# modelica model with supporting files test
mo_path = '../../MoModels/nb_hydr_static.mo'
res_dir = './nb_hydr_static_res'
sudo_pwd = '63z64q92zza'
mo_engine = ModelicaEngine(mo_path, res_dir, sudo_pwd, 
							log_level = 'DEBUG',
							fmu_path = 'nb_hydr_static_res/compilation/nb_hydr_static.fmu')
res_dir = mo_engine.simulate(start_time=0, final_time=3600,
					res_names = ['chw_ret_P.p', 'chw_sup_P.p',
								 'chw_sup_m.m_flow'])

