"""
Tests for jinja functions
"""

import filecmp
import os
import shutil
from pathlib import Path

from walltheme import jinja, utils


def test_gen_templates():
	"""
	Testing if color themes are being generated correctly
	"""
	test_image = 'walltheme/tests/test_files/test.jpg'
	test_theme = {
		'wallpaper': test_image,
		'background': '#070605',
		'foreground': '#b7a998',
		'cursor': '#b7a998',
		'primary': '#241f19',
		'primary_dark': '#120f0c',
		'primary_light': '#5a4e3f',
		'secondary': '#4a351e',
		'secondary_dark': '#251a0f',
		'secondary_light': '#b7844d',
		'tertiary': '#6c502b',
		'tertiary_dark': '#362816',
		'tertiary_light': '#a27840',
		'quaternary': '#8a705c',
		'quaternary_dark': '#45382e',
		'quaternary_light': '#bdaa9c',
		'quinary': '#ccc1b2',
		'quinary_dark': '#73624c',
		'quinary_light': '#ffffff',
	}

	template_dir = Path('walltheme/templates')
	test_themes_dir = Path('tests/test_themes')
	tmp_dir = Path('tmp')

	if tmp_dir.exists():
		shutil.rmtree(tmp_dir)

	utils.create_dir(tmp_dir)
	assert utils.is_dir_empty(tmp_dir)

	jinja.gen_templates(template_dir, tmp_dir, test_theme)

	cmp = filecmp.cmpfiles(
		test_themes_dir, tmp_dir, os.listdir(test_themes_dir), False
	)

	# print(cmp)

	assert cmp[0] == os.listdir(test_themes_dir)

	shutil.rmtree(tmp_dir)
