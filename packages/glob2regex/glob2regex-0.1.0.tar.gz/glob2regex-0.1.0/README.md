# glob2regex

Converts glob search format to regex format

[![Python package](https://github.com/Salamek/glob2regex/actions/workflows/python-test.yml/badge.svg)](https://github.com/Salamek/glob2regex/actions/workflows/python-test.yml)


## Install


```bash
pip install glob2regex
```


## Example of usage


```python
from glob2regex import glob2regex

glob_search = '/home/*/ST-*/q[01-10]*.pdf'

regex = glob2regex(glob_search)

print(regex)

```