# JaSON - yet another JSON parser

## Installation

### Never but in case of, from pypi

```
pip install jason
```

### Or locally

```
pip install .
```

## Usage

```
usage: jason [-h] [-i INPUT] [-v] query

positional arguments:
  query                 query to perform

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        input file
  -v, --verbose         verbose mode

examples:
  cat file.json | jason '$'
  jason '$' -i file.json
```

## API

```python
from jason.api import query, unmarshal

# perform request with `query`
query(string, request)
# convert to python obj with `unmarshal`
unmarshal(string)

# and decicated objects
q = Query(string)
res = q.exec(request)

p = Parser(string)
res = p.unmarshal()
```

## Run tests

```
$ pip install pytest
$ pytest
```

## TODO

- query the produced ast (`api.py:query`)
  - https://goessner.net/articles/JsonPath/
  - filters and ranges
- tests
  - lexer
    - string_pass / string_fail
  - parser
    - unmarshal
  - query
