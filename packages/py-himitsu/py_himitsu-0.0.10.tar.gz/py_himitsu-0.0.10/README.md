# py-himitsu

Himitsu client library.

## Install

A package is available via [pip](https://pypi.org/project/py-himitsu/)

```sh
pip install py-himitsu
```

## Example

```python
from himitsu import client

c = client.connect()
print(c.status())
```
