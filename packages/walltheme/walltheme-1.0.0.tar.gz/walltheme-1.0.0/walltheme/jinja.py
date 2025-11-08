"""
Jinja2 setup
"""

import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from . import colors, utils


def setup_jinja_env(templates_dir: Path) -> Environment:
	"""
	Jinja2 environment setup
	"""
	env = Environment(
		loader=FileSystemLoader(str(templates_dir)),
		autoescape=False,
		keep_trailing_newline=True,
		trim_blocks=True,
		lstrip_blocks=True,
	)

	# Lighten/Darken color with adjust_lightness
	env.filters['lighten'] = lambda color, amount=1.2: colors.adjust_lightness(
		color, amount
	)
	env.filters['darken'] = lambda color, amount=0.8: colors.adjust_lightness(
		color, amount
	)

	return env


def gen_templates(templates_path: Path, output_dir: Path, theme: dict) -> None:
	"""
	Generates all *.j2 templates in templates_path into output_dir
	Color themes keep their filename but with the .j2 suffix removed
	"""
	if not templates_path.is_dir():
		raise ValueError('The templates path must be a directory!')

	env = setup_jinja_env(templates_path)

	for template_path in templates_path.iterdir():
		rel = template_path.relative_to(templates_path)

		if template_path.suffix == '.j2':
			template = env.get_template(str(rel))
			wallpaper, special, palette = utils.split_theme(theme)
			context = {
				'theme': theme,
				'wallpaper': wallpaper,
				'special': special,
				'palette': palette,
			}
			rendered = template.render(**context)

			# Write to output file with same path but strip .j2
			output = output_dir / rel.with_suffix('')
			output.parent.mkdir(parents=True, exist_ok=True)
			output.write_text(rendered, encoding='utf-8')
			# print(f'Generated {rel.with_suffix("")} to {output}')
			logging.info('Generated %s to %s', rel.with_suffix(''), output)
		else:
			logging.warning(
				"The template '%s' has to be '.j2' to be recognized!", rel
			)
