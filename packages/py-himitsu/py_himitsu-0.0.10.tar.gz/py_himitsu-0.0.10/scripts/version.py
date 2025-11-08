import tomllib

with open('pyproject.toml', 'rb') as f:
	print(tomllib.load(f)['project']['version'])
