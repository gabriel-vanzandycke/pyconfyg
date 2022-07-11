# pyconfyg

Python experiments configuration files library

For a configuration file `cfg.py`:
```
digit = 2
key = "a"
value = {
  "a": 12,
  "b": 42,
}[k]
```

## Usage

### Load configuration
Loads the configuration file as a dictionary
```python
from pyconfyg import Confyg
config = Confyg("cfg.py").dict
assert(conifg['value'] == 12)
```

### Runtime overwriting parameters
Loads the configuration file and update the parameter 'key' before retrieving the dictionary
```python
from pyconfyg import Confyg
config = Confyg("cfg.py", {'key': 'b'}).dict
assert(conifg['value'] == 42)
```

### Confyg iterator
Creates a configuration iterator for multiple values of the parameter 'key'
```python
from pyconfyg import GridConfyg
configs = [c.dict for c in GridConfyg("cfg.py", {'key': ['a', 'b']})]
```


### Cartesian product Confyg iterator
Creates a configuration iterator for multiple values of the parameters 'key' and 'digit' (creating 6 different configurations)
```python
from pyconfyg import GridConfyg
configs = list(GridConfyg("cfg.py", {'key': ['a', 'b'], 'digit': [2, 4, 8]}))
```
