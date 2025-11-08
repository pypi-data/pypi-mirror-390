"""
Tests for color functions
"""

import matplotlib.colors as mc

from walltheme import colors, utils


def test_to_full_rgb():
	"""
	Testing if a color properly converted to the 'full' RGB format (0-255)
	"""
	color = (1, 0.52, 0.999)

	assert colors.to_full_rgb(color) == (255, 133, 255)


def test_to_unit_rgb():
	"""
	Testing if a color properly converted to the unit RGB format (0-1)
	"""
	color = (255, 133, 52)

	assert colors.to_unit_rgb(color) == (1.0, 0.52, 0.203)


def test_is_light():
	"""
	Testing if a color is properly detected as light
	"""
	color_light = (255, 255, 255)
	color_dark = (0, 0, 0)

	assert colors.is_light(color_light)
	assert not colors.is_light(color_dark)


def test_is_dark():
	"""
	Testing if a color is properly detected as dark
	"""
	color_light = (255, 255, 255)
	color_dark = (0, 0, 0)

	assert not colors.is_dark(color_light)
	assert colors.is_dark(color_dark)


def test_get_dominant_colors():
	"""
	Testing if right amount of colors is generated
	"""
	test_colors5 = colors.get_dominant_colors('tests/test_files/test.jpg')
	test_colors3 = colors.get_dominant_colors('tests/test_files/test.jpg', 3)
	test_colors8 = colors.get_dominant_colors('tests/test_files/test.jpg', 8)

	assert (
		len(test_colors5) == 5 and len(test_colors3) == 3 and len(test_colors8) == 8
	)


def test_adjust_lightness():
	"""
	Testing if colors are adjusted properly
	"""
	color_light = (77, 79, 43)
	color_dark = (40, 33, 23)

	# ensure the test colors are actually light and dark
	assert colors.is_light(color_light)
	assert colors.is_dark(color_dark)

	# adjust_lightness expects RGB colors only in the unit format (0-1)
	# (due to mathplotlib's to_rgb function)

	color_light_adjusted_hex = colors.adjust_lightness(
		colors.to_unit_rgb(color_light), 0.5
	)
	color_dark_adjusted_hex = colors.adjust_lightness(
		colors.to_unit_rgb(color_dark), 1.5
	)

	# adjust_lightness returns a color in the Hex format
	# and is_light then expects an RGB tuple in the 'full' format (0-255)

	color_light_adjusted_rgb = colors.to_full_rgb(
		mc.to_rgb(color_light_adjusted_hex)
	)
	color_dark_adjusted_rgb = colors.to_full_rgb(
		mc.to_rgb(color_dark_adjusted_hex)
	)

	assert not colors.is_light(color_light_adjusted_rgb)
	assert not colors.is_dark(color_dark_adjusted_rgb)


def test_gen_theme():
	"""
	Testing if theme is properly generated
	"""
	test_image = utils.get_image('tests/test_files/test.jpg')
	test_colors = colors.get_dominant_colors(test_image)
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

	theme = colors.gen_theme(test_image, test_colors)

	assert theme == test_theme
