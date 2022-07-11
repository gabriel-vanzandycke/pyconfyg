# pyconfyg

Python experiments configuration files library

For a configuration file `cfg.py`:
```
a = 2
k = "a"
v = {
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
```

### Runtime overwriting parameters
Loads the configuration file and update the parameter 'k' before retrieving the dictionary
```python
from pyconfyg import Confyg
config = Confyg("cfg.py", {'k': 'b'}).dict
```

### Confyg iterator
Creates a configuration iterator for multiple values of the parameter 'k'
```python
from pyconfyg import GridConfyg
configs = [c.dict for c in GridConfyg("cfg.py", {'k': ['a', 'b']})]
```


### Cartesian product Confyg iterator
Creates a configuration iterator for multiple values of the parameters 'k' and 'a' (creating 6 different configurations)
```python
from pyconfyg import GridConfyg
configs = list(GridConfyg("cfg.py", {'k': ['a', 'b'], 'a': [2, 4, 8]}))
```
