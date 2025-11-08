#!/bin/sh

set -euo pipefail

make lint

version="$1"

if [ -z "$version" ]; then
	echo "version as argument required"
	exit 1
fi

curversion=$(grep version pyproject.toml | cut -d'"' -f 2)

echo "releasing $version"

if [ "$curversion" = "$version" ]; then
	echo "version already in pyproject.toml. Has it been released already?"
	exit 1
fi

sed -i 's/version = ".*"/version = "'$version'"/' pyproject.toml

make check
make build

git add pyproject.toml
git commit -m "release $version"
git tag "$version"

git push
git push --tags

python3 -m twine upload --repository pypi dist/*"$version"*
