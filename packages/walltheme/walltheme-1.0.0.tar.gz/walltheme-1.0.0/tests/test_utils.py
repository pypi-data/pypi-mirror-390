"""
Tests for utility functions
"""

import filecmp
import os
import shutil
from pathlib import Path

from walltheme import utils


def test_create_dir():
	"""
	Testing creating a directory
	"""
	tmp_dir = 'tmp'
	if os.path.exists(tmp_dir):
		shutil.rmtree(tmp_dir)

	utils.create_dir(tmp_dir)
	assert os.path.isdir(tmp_dir)
	os.rmdir(tmp_dir)


def test_empty_dir_check():
	"""
	Testing if a directory is empty
	"""
	is_empty = utils.is_dir_empty('tests')
	assert not is_empty

	tmp_dir = 'tmp'
	if os.path.exists(tmp_dir):
		shutil.rmtree(tmp_dir)

	utils.create_dir(tmp_dir)
	is_empty = utils.is_dir_empty(tmp_dir)
	assert is_empty
	os.rmdir(tmp_dir)


def test_is_valid_image():
	"""
	Testing if a file is a valid image
	"""
	img_formats = ['.png', '.jpg', '.jpeg', '.webp']

	test_file_dir = Path('tests/test_files')

	for file_path in test_file_dir.iterdir():
		extension = ''.join(file_path.suffixes).lower()
		if extension in img_formats:
			assert utils.is_valid_image(file_path)
		else:
			assert not utils.is_valid_image(file_path)


def test_init_templates():
	"""
	Testing initializing templates
	"""
	template_dir = 'walltheme/templates'
	tmp_dir = 'tmp'
	if os.path.exists(tmp_dir):
		shutil.rmtree(tmp_dir)

	utils.create_dir(tmp_dir)
	utils.init_templates(tmp_dir)
	result = filecmp.cmpfiles(
		template_dir, tmp_dir, os.listdir(template_dir), False
	)

	assert result[0] == os.listdir(template_dir)
	shutil.rmtree(tmp_dir)
