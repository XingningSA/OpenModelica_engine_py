# Author: Zhiang Zhang
# First create: 2022-06-16
import os

def find_files_in_dir(dir_name, file_ext = '.mo'):
	"""
	Find all .mo files in a directory
	"""
	items = os.listdir(dir_name)
	ext_len = len(file_ext)
	file_list = []
	for item in items:
		full_path = dir_name + os.sep + item
		if os.path.isdir(full_path):
			file_list.extend(find_files_in_dir(full_path))
		else:
			if full_path[-ext_len: ].lower() == file_ext:
				file_list.append(full_path)
	return file_list
