# Author: Zhiang Zhang
# Date: 2022-06-11
import os
import csv
import time
import subprocess
import threading
import _thread
import shutil
import xml.etree.ElementTree as ET
import traceback
import pandas as pd

from zipfile import ZipFile
from modelica_builder.model import Model
from .EngineUtils.Logger import Logger
from .EngineUtils.FileUtils import find_files_in_dir
from .EngineUtils.Exceptions import NotCompiledException


LOG_FMT = "[%(asctime)s] %(name)s %(levelname)s:%(message)s";
THIS_DIR = os.path.dirname(os.path.realpath(__file__))

class Engine(object):

	def __init__(self, mo_path, res_dir, sudo_pwd,
				fmu_path = None, jm_docker_dir = THIS_DIR,
				jm_docker_src = None,
				jm_compile_src = None,
				jm_simulate_src = None,
				set_params = [],
				#[['Buildings.Fluid.FixedResistances.Junction',
			    #  'jun_1', {'m_flow_nominal': '{800,-600,-200}',
			    #			 'dp_nominal': '{5000, -2000, -3000}'}],
			    #  'Buildings.Fluid.Movers.SpeedControlled_y',
			    #  'chwp_2', {'p_start': '40000'} ]
				is_soep = False,
				log_level = 'INFO'):
		# make all paths and dirs into abspath
		jm_docker_dir = os.path.abspath(jm_docker_dir)
		mo_path = os.path.abspath(mo_path)
		res_dir = os.path.abspath(res_dir)
		if fmu_path is not None:
			fmu_path = os.path.abspath(fmu_path)
		if jm_docker_src is None:
			jm_docker_src = jm_docker_dir + \
								os.sep + 'jm_ipython.sh'
		else:
			jm_docker_src = os.path.abspath(jm_docker_src)
		if jm_compile_src is None:
			jm_compile_src = jm_docker_dir + \
								os.sep + 'compile_fmu_1.py'
		else:
			jm_compile_src = os.path.abspath(jm_compile_src)
		if jm_simulate_src is None:
			jm_simulate_src = jm_docker_dir + \
								os.sep + 'run_fmu_1.py'
		else:
			jm_simulate_src = os.path.abspath(jm_simulate_src)
		self._mo_path = mo_path
		self._fmu_path = fmu_path
		if self._mo_path is not None:
			self._is_mo_dir = os.path.isdir(self._mo_path)
			if self._is_mo_dir:
				self._mo_name = self._mo_path.split(os.sep)[-1]
			else:
				self._mo_name = self._mo_path\
							.split(os.sep)[-1].split('.mo')[0]
		else:
			self._is_mo_dir = None
			self._mo_name = self._fmu_path\
							.split(os.sep)[-1].split('.fmu')[0]
		self._logger = Logger().getLogger('ModelicaEngine-{}'\
										.format(self._mo_name),
                                        log_level, LOG_FMT)
		################################################################
		# process attributes
		self._res_dir = res_dir
		self._sudo_pwd = sudo_pwd
		self._jm_docker_src = jm_docker_src
		self._jm_compile_src = jm_compile_src
		self._jm_simulate_src = jm_simulate_src
		self._is_soep = is_soep
		self._log_level = log_level
		self._set_params = set_params
		################################################################
		# prepare result path
		if not os.path.exists(res_dir):
			os.mkdir(res_dir)
		################################################################
		# compile the modelica model
		if fmu_path is None:
			self._logger.info("Compilation starts")
			################################################################
			# process the modelica model file
			if self._is_mo_dir:
				self._mo_file_paths = find_files_in_dir(self._mo_path,
											file_ext = '.mo')
				self._mo_file_path = self._mo_file_paths[0]
				if len(self._mo_file_paths) > 0:
					self._logger.warning('More than one Modelica model '\
							'files are found, the first found one '\
							'is used. The used file is {}'\
							.format(self._mo_file_path))
			else:
				self._mo_file_path = self._mo_path
			self._fmu_path, self._used_mo_path\
							= self._compile_mo(
											self._mo_name,
											self._mo_path,
											self._mo_file_path,
											self._is_mo_dir,
											self._res_dir,
											self._sudo_pwd,
											self._jm_docker_src,
											self._jm_compile_src,
											self._is_soep,
											self._log_level,
											self._set_params
											)
		else:
			self._fmu_path = fmu_path
			self._used_mo_path = None

	def _compile_mo(self, mo_name, mo_cp_dir, mo_file_path,
					is_mo_dir, res_dir, sudo_pwd, docker_src,
					compile_src, is_soep, log_level, set_params):
		"""
		Call a JModelica docker script to compile Modelica model
		"""
		this_id = time.time()
		################################################################
		# prepare a logger
		cmp_log_fmt = "%(name)s %(levelname)s:%(message)s";
		cmp_logger = Logger().getLogger('ModelicaEngine-Compilation-{}'\
										.format(this_id),
                                        log_level, cmp_log_fmt)
		################################################################
		# copy the modelica model file to the docker mounting dir
		docker_src_dir = os.path.dirname(docker_src)
		docker_tmp_dir = '{}{}tmpcomp_{}_{}'.format(docker_src_dir, 
								os.sep, mo_name, this_id) 
		os.makedirs(docker_tmp_dir)
		cmp_logger.info('Preparing compilation model directory...')
		cmp_logger.debug('Compilation model temporary directory is:{}'\
						.format(docker_tmp_dir))
		if os.path.isdir(mo_cp_dir):
			dir_name = os.path.basename(os.path.normpath(mo_cp_dir))
			docker_mofolder_dir = docker_tmp_dir + os.sep + dir_name
			shutil.copytree(mo_cp_dir, docker_mofolder_dir)
			mo_file_rela_path = mo_file_path.split(mo_cp_dir)[-1]
			docker_mo_path = docker_mofolder_dir + os.sep \
								+ mo_file_rela_path
			docker_mo_dir = os.path.dirname(docker_mo_path)
		else:
			docker_mo_path = docker_tmp_dir + os.sep + mo_name + '.mo'
			docker_mo_dir = docker_tmp_dir
			shutil.copyfile(mo_file_path, docker_mo_path)
		cmp_logger.debug('docker_mo_path:{}'\
						.format(docker_mo_path))
		cmp_logger.debug('docker_mo_dir:{}'\
						.format(docker_mo_dir))
		################################################################
		# change modelica file parameters
		if len(set_params) > 0:
			cmp_logger.info('Setting specified parameters...')
			# set_params format
			#[['Buildings.Fluid.FixedResistances.Junction',
		    #  'jun_1', {'m_flow_nominal': '{800,-600,-200}',
		    #			 'dp_nominal': '{5000, -2000, -3000}'}],
		    #  ['Buildings.Fluid.Movers.SpeedControlled_y',
		    #  'chwp_2', {'p_start': '40000'} ],
		    #  ['parameter', 'Real', 'jun_p1_dp', '2000']]
			for set_param in set_params:
				if set_param[0] == 'parameter':
					self._update_mo_parameter(mo_name = mo_name,
											mo_path = docker_mo_path,
											param_type = set_param[1],
											name = set_param[2],
											val = set_param[3])
				else:
					docker_mo_model = Model(docker_mo_path)
					docker_mo_model\
					.update_component_modifications(
						set_param[0], set_param[1], set_param[2])
					docker_mo_model.save_as(docker_mo_path)
		################################################################
		# call the jm shell script to compile the model
		docker_mo_dir_rela = docker_mo_dir.split(docker_src_dir)[-1]
		# remove the leading /mnt if there is (/mnt is likely a mounted a directory in a docker container)
		docker_src_dir_host = docker_src_dir.split('/mnt')[-1]
		cmp_logger.info(docker_src)
		if sudo_pwd is None:
			sh_script = "{} {} {} {} {} {} {} {}"\
					.format(docker_src, docker_src_dir_host, docker_mo_dir_rela, 
						compile_src, mo_name, docker_mo_dir_rela, 'me', 
						is_soep)
		else:
			sh_script = "echo {} | sudo -S {} {} {} {} {} {} {} {}"\
					.format(sudo_pwd, docker_src, docker_src_dir_host, docker_mo_dir_rela, 
						compile_src, mo_name, docker_mo_dir_rela, 'me', 
						is_soep)
		cmp_logger.info('Calling compilation script...')
		cmp_logger.debug('Compilation script is: {}'\
						.format(sh_script))
		jm_compile_prcs = subprocess.Popen(
						sh_script,
                        shell = True,
                        cwd = docker_src_dir,
                        stdout = subprocess.PIPE,
                        stderr = subprocess.PIPE,
                        preexec_fn=os.setsid)
		threading_return = []
		log_info_t = threading.Thread(target=self._log_subprocess_info,
										args=(jm_compile_prcs.stdout,
											cmp_logger, threading_return))
		log_err_t = threading.Thread(target=self._log_subprocess_err,
										args=(jm_compile_prcs.stderr,
											cmp_logger))
		log_info_t.start()
		log_err_t.start()
		while self._get_is_subprocess_running(jm_compile_prcs):
			pass
		# finishing compilation
		if len(threading_return) > 0:
			cmp_logger.info('Compilation script compeltes')
		################################################################
		# move post compilation results
		# elevate directory permissions
		if sudo_pwd is None:
			elevation_script = "chmod ugo+rwx -R ."
		else:
			elevation_script = "echo {} | sudo -S chmod ugo+rwx -R ."\
							.format(sudo_pwd)
		jm_compile_prcs = subprocess.call(
						elevation_script,
                        shell = True,
                        cwd = docker_src_dir,
                        stdout = subprocess.PIPE,
                        stderr = subprocess.PIPE,
                        preexec_fn=os.setsid)
		# move fmu file to res_dir
		returned_fmu_dir = threading_return[0]\
					.split('Compilation_Result_Directory:')[1]\
					.split('\n')[0]

		fmu_dir = '{}{}{}'.format(
						docker_mo_dir, os.sep, returned_fmu_dir)
		res_fmu_dir = '{}{}{}'\
						.format(res_dir, os.sep, 'compilation')
		if os.path.exists(res_fmu_dir):
			shutil.rmtree(res_fmu_dir)
		shutil.copytree(fmu_dir, res_fmu_dir)
		returned_mo_path = res_fmu_dir + os.sep + mo_name + '.mo'
		shutil.copyfile(docker_mo_path, returned_mo_path)
		cmp_logger.debug('Original FMU directory: {}'\
							.format(fmu_dir))
		cmp_logger.debug('Resulting FMU directory: {}'\
							.format(res_fmu_dir))
		res_fmu_path = res_fmu_dir + os.sep + mo_name + '.fmu'
		if os.path.isfile(res_fmu_path) \
			and not os.path.isdir(mo_cp_dir): 
			cmp_logger.info('Compilaton succeeded, '\
							'compiled FMU is ready at: {}'\
						.format(res_fmu_path))
			returned_fmu_path = res_fmu_path
		################################################################
		# special arrangement for the model with support files
		# the file structure must be kept, so the fmu must be copied for
		# the second time to the same directory with the mo file
		elif os.path.isfile(res_fmu_path) \
			and os.path.isdir(mo_cp_dir):
			dir_name = os.path.basename(os.path.normpath(mo_cp_dir))
			res_mofolder_dir = res_dir + os.sep + 'compilation' \
								+ os.sep + dir_name
			cmp_logger.debug('res_mofolder_dir: {}'\
							.format(res_mofolder_dir))
			shutil.copytree(mo_cp_dir, res_mofolder_dir)
			mo_file_rela_path = mo_file_path.split(mo_cp_dir)[-1]
			res_mo_path = res_mofolder_dir + os.sep \
								+ mo_file_rela_path
			res_mo_dir = os.path.dirname(res_mo_path)
			res_fmu_path2 = res_mo_dir + os.sep + mo_name + '.fmu'
			cmp_logger.debug('res_fmu_path2 (the one used for '\
				'simulation if the modelica model needs supporting '\
				'files): {}'.format(res_fmu_path2))
			shutil.copy(res_fmu_path, res_fmu_path2)
			res_fmu_path = res_fmu_path2
			cmp_logger.info('Compilaton succeeded, '\
							'compiled FMU is ready at: {}'\
						.format(res_fmu_path))
			cmp_logger.info('Compiled FMU directory is ready at: {}'\
						.format(res_mo_dir))
			returned_fmu_path = res_mo_dir
		else:
			res_fmu_path = None
			returned_fmu_path = res_fmu_path
			cmp_logger.info('Compilation failed')
			
		################################################################
		# clean temporarly working directory
		shutil.rmtree(docker_tmp_dir, ignore_errors = True)
		################################################################
		# extract result output
		if res_fmu_path is not None:
			self._read_model_variables(res_fmu_path, res_fmu_dir)
			
		return returned_fmu_path, returned_mo_path

	def _update_mo_parameter(self, mo_name, mo_path, param_type, name, val):
		is_found = False
		with open(mo_path, 'r') as mo_file:
			mo_texts = mo_file.read()
			mo_header = 'model {}'.format(mo_name)
			mo_body_si = mo_texts.find(mo_header)\
								+ len(mo_header)
			mo_body = mo_texts[mo_body_si: ]
			mo_lines = mo_body.split(';')
			for i in range(len(mo_lines)):
				mo_line = mo_lines[i]
				mo_line = mo_line.strip()
				mo_line_ls = mo_line.split(' ')
				if mo_line_ls[0].strip() == 'parameter' and\
				   mo_line_ls[1].strip() == param_type and\
				   mo_line_ls[2].strip().split('=')[0] == name:
					param_val = mo_line_ls[2].strip().split('=')
					param_val[1] = str(val)
					mo_line_ls[2] = '='.join(param_val)
					mo_lines[i] = '\n'+' '.join(mo_line_ls)
					mo_body = ';'.join(mo_lines)
					mo_texts_new = mo_header + mo_body
					is_found = True
					break
		if is_found:
			with open(mo_path, 'w') as mo_file:
				mo_file.write(mo_texts_new)

	def _read_model_variables(self, res_fmu_path, res_dir):
		varaibles_path = '{}{}variables.csv'\
							.format(res_dir, os.sep)
		var_csv = open(varaibles_path, 'w+', newline='')
		var_writer = csv.writer(var_csv)
		var_writer.writerow(['name', 'valueReference',
						'causality', 'variability',
						'initial', 'description', 'type'])
		with ZipFile(res_fmu_path, 'r') as fmu:
			md = fmu.read('modelDescription.xml')
			mdtree = ET.ElementTree(ET.fromstring(md))
			mdroot = mdtree.getroot()
			variables = mdroot.find('ModelVariables')
			for variable in variables:
				var_attr = variable.attrib
				to_read_keys = ['name', 'valueReference', 'causality',
								'variability', 'initial', 'description']
				var_data = []
				for to_read_key in to_read_keys:
					try:
						var_data.append(var_attr[to_read_key])
					except:
						var_data.append('')
				var_type = variable[0].tag
				var_data.append(var_type)
				if var_type == 'Real':
					to_read_keys = ['quantity', 'unit']
					var_type_attr = variable[0].attrib
					for to_read_key in to_read_keys:
						try:
							var_data.append(var_type_attr[to_read_key])
						except:
							pass
				var_writer.writerow(var_data)
		var_csv.close()

	def _log_subprocess_info(self, out, logger, 
							threading_return = None,
							shared_n = None):
		for line in iter(out.readline, b''):
			line = line.decode()
			logger.info(line)
			if 'Result_Directory' in line:
				threading_return.append(line)
			if shared_n is not None:
				shared_n[0] += 1

	def _log_subprocess_err(self, out, logger):
		for line in iter(out.readline, b''):
			logger.error(line.decode())

	def _get_is_subprocess_running(self, subprocess):
		if subprocess.poll() is None:
			return True
		else:
			return False

	def simulate(self, 
				start_time: int, 
				final_time: int,
				time_step: int = None, 
				res_names:list = [], 
				set_param_dict:dict = {}, 
				fmu_path: str = None,
				debug_solver: bool = False, 
				rtol: float = 10e-4, 
				maxh: float = 10,
				return_res_files: bool = True):
		"""

		Args:
		----------
		set_param_dict: Dict
			A dictionary of parameters to be set for the model.
			The dict key is the parameter name to be set, and 
			the dict value is the parameter value to be set.

		"""
		if fmu_path is None:
			fmu_path = self._fmu_path
		if fmu_path is None:
			raise NotCompiledException()
		this_id = time.time()
		################################################################
		# prepare a logger
		sim_log_fmt = "%(name)s %(levelname)s:%(message)s";
		sim_logger = Logger().getLogger('ModelicaEngine-Simulation-{}'\
										.format(this_id),
                                        self._log_level, sim_log_fmt)
		################################################################
		# copy the FMU model file to the docker mounting dir
		docker_src_dir = os.path.dirname(self._jm_docker_src)
		docker_tmp_dir = '{}{}tmpsimu_{}_{}'.format(
								docker_src_dir, os.sep, self._mo_name,
								this_id) 
		os.makedirs(docker_tmp_dir)
		sim_logger.info('Preparing simulation model directory...')
		sim_logger.debug('Simulation model temporary directory is:{}'\
						.format(docker_tmp_dir))
		if os.path.isdir(self._fmu_path):
			fmu_dir_name = os.path.basename(
							os.path.normpath(self._fmu_path))
			fmu_in_docker_dir = docker_tmp_dir + os.sep \
								+ fmu_dir_name
			shutil.copytree(self._fmu_path, fmu_in_docker_dir)
			fmu_in_docker_path = find_files_in_dir(fmu_in_docker_dir,
											file_ext = '.fmu')[0]
		else:
			fmu_in_docker_dir = docker_tmp_dir
			fmu_in_docker_path = docker_tmp_dir + os.sep \
							+ self._mo_name + '.fmu'
			shutil.copyfile(self._fmu_path, fmu_in_docker_path)
		sim_logger.debug('fmu_in_docker_dir:{}'\
							.format(fmu_in_docker_dir))
		sim_logger.debug('fmu_in_docker_path:{}'\
							.format(fmu_in_docker_path))
		################################################################
		# call the jm shell script to simulate the model
		fmu_in_docker_dir_rela = '.' + os.sep \
								+ fmu_in_docker_dir\
								.split(docker_src_dir)[-1]
		fmu_in_docker_path_rela = '.' + os.sep \
								+ fmu_in_docker_path\
								.split(fmu_in_docker_dir)[-1]
		docker_src_dir_host = docker_src_dir.split('/mnt')[-1]
		if self._sudo_pwd is None:
			sh_script = "{} {} {} {} -p {} -st {} -ft {} "\
					"-ll {} -rtol {} -maxh {}" \
					.format(self._jm_docker_src, docker_src_dir_host,
						fmu_in_docker_dir_rela, self._jm_simulate_src, 
						fmu_in_docker_path_rela, start_time, final_time,
						self._log_level, rtol, maxh)
		else:
			sh_script = "echo {} | sudo -S {} {} {} {} -p {} -st {} -ft {} "\
					"-ll {} -rtol {} -maxh {}" \
					.format(self._sudo_pwd, self._jm_docker_src, docker_src_dir_host,
						fmu_in_docker_dir_rela, self._jm_simulate_src, 
						fmu_in_docker_path_rela, start_time, final_time,
						self._log_level, rtol, maxh)
		if len(res_names) > 0:
			sh_script += ' -r {}'.format(' '.join(res_names))
		if len(set_param_dict) > 0:
			set_params = []
			for set_param_key in set_param_dict.keys():
				set_param_val = set_param_dict[set_param_key]
				set_params.append('{}:{}'\
							.format(set_param_key, set_param_val))
			sh_script += ' -s {}'.format(' '.join(set_params))
		if debug_solver:
			sh_script += ' -d'
		sim_logger.info('Calling simulation script...')
		sim_logger.info('Simulation script is: {}'\
						.format(sh_script))
		jm_simulate_prcs = subprocess.Popen(
						sh_script,
                        shell = True,
                        cwd = docker_src_dir,
                        stdout = subprocess.PIPE,
                        stderr = subprocess.PIPE,
                        preexec_fn=os.setsid)
		threading_return = []
		prcs_log_n = [0]
		log_info_t = threading.Thread(target=self._log_subprocess_info,
										args=(jm_simulate_prcs.stdout,
										sim_logger, threading_return, 
										prcs_log_n))
		log_err_t = threading.Thread(target=self._log_subprocess_err,
										args=(jm_simulate_prcs.stderr,
											sim_logger))
		log_info_t.start()
		log_err_t.start()
		################################################################
		# waiting for the process finishes
		# two criteria for finishing: 
		# 1: subprocess poll is None
		# 2: standard output log pipeline captures 'Result_Directory'
		while self._get_is_subprocess_running(jm_simulate_prcs):
			pass
		while True:
			if len(threading_return) > 0:
				break
		sim_logger.debug('prcs_log_n:{}'.format(prcs_log_n))
		################################################################
		# finishing compilation
		if len(threading_return) > 0:
			sim_logger.info('Simulation script compeltes')
		# elevate directory permissions
		if self._sudo_pwd is None:
			elevation_script = "chmod ugo+rwx -R ."
		else:
			elevation_script = "echo {} | sudo -S chmod ugo+rwx -R ."\
							.format(self._sudo_pwd)
		jm_ele_prcs = subprocess.call(
						elevation_script,
                        shell = True,
                        cwd = docker_src_dir,
                        stdout = subprocess.PIPE,
                        stderr = subprocess.PIPE,
                        preexec_fn=os.setsid)
		try:
			returned_res_dir = threading_return[0]\
					.split('Simulation_Result_Directory:')[1]\
					.split('\n')[0]
			returned_res_dir = '{}{}{}'.format(
							fmu_in_docker_dir, os.sep, returned_res_dir)
			sim_logger.debug('Original results path: {}'\
								.format(returned_res_dir))
			if os.path.isfile("{}{}{}_result.mat"
					.format(returned_res_dir, os.sep, self._mo_name)):
				sim_logger.info('Simulation succeeded!')
					
			else:
				sim_logger.error('Simulation failed')
			if return_res_files:
				# move simulation results file to res_dir
				dir_name = 'simres'
				ver_sig = 'run'
				sim_res_vernum = this_id# TODO: _res_dir_num is not thread safe
									# self._res_dir_num(self._res_dir, dir_name,
									#			ver_sig)
				host_res_dir = '{}{}{}_{}{}'\
							.format(self._res_dir, os.sep, dir_name,
									ver_sig, sim_res_vernum)
				if os.path.exists(host_res_dir):
					if os.path.isdir(host_res_dir):
						shutil.rmtree(host_res_dir)
					if os.path.isfile(host_res_dir):
						os.remove(host_res_dir)
				shutil.copytree(returned_res_dir, host_res_dir)
				# copy the current used mo file to the directory
				if self._used_mo_path is not None:
					shutil.copy(self._used_mo_path, host_res_dir)
				# clean temporarly working directory
				shutil.rmtree(docker_tmp_dir, ignore_errors = True) 
				return host_res_dir
			else:
				res_pd = pd.read_csv(returned_res_dir 
									+ os.sep 
									+ '{}_res.csv'.format(self._mo_name))
				if time_step is None:
					res_list = res_pd[res_names].iloc[-1]
				else:
					res_list = []
					res_pd = res_pd.set_index('time')
					res_pd = res_pd[~res_pd.index.duplicated(keep='first')]
					res_pd = res_pd.interpolate(method='linear', limit_direction='both')
					res_pd = res_pd.reindex(range(int(res_pd.index.min()), int(res_pd.index.max()) + 1))
					for time_i in range(time_step, final_time + 1, time_step):
						res_list.append(res_pd[res_names].loc[time_i].values.tolist())
                # clean temporarly working directory
				shutil.rmtree(docker_tmp_dir, ignore_errors = True) 
				return res_list
		except:
			sim_logger.error('Error! res_names: {}, set_param_dict:{}'\
								.format(res_names, set_param_dict))
			traceback.print_exc()


	def _res_dir_num(self, root_dir, dir_name, ver_sig):
		cur_max_vernum = 0
		dir_sig = '{}_{}'.format(dir_name, ver_sig)
		for dir_i in os.listdir(root_dir):
			path_name = '{}{}{}'.format(root_dir, os.sep, dir_i)
			if os.path.isdir(path_name):
				if dir_sig in dir_i:
					ver_name = dir_i.split(dir_sig)[-1]
					ver_num = None
					try:
						ver_num = int(ver_name[0: ])
					except:
						ver_num = None
					if ver_num is not None:
						if ver_num > cur_max_vernum:
							cur_max_vernum = ver_num
		cur_vernum = cur_max_vernum + 1
		return cur_vernum

	@property
	def mo_name(self):
		return self._mo_name