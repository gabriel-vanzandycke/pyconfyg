import ast
import copy
import functools
import itertools
import logging
import os
import re
import traceback
from typing import Any, Dict, Iterator, Optional, Tuple

import astunparse

from pyconfyg.ast import update_ast
from pyconfyg.exceptions import InterpreterError

# pylint: disable=logging-fstring-interpolation

logger = logging.getLogger(__name__)

def product_kwargs(**kwargs) -> Iterator[Dict]:
    """ Transforms a dictionary of arguments (argument_name, list_of_values)
        into an iterator over dictoraries or initial arguments and every
        combination of their values.

        :param kwargs: dict of name, lists
        :returns: Iterator
    """
    kvs = []
    for k in kwargs:
        try:
            kvs.append([(k, v) for v in kwargs[k]])
        except BaseException as e:
            raise SyntaxError(
                f"Error parsing: `{k}:{kwargs[k]}`. Expected an iterable"
            ) from e
    yield from (dict(kv) for kv in itertools.product(*kvs))


def parse_strings(*strings: str, env=None) -> Dict[str, Any]:
    """ Parses strings of 'k=v' by using builtin exec and returns a dictionary
        of the created symbols and their value.
        Arguments:
            strings - strings to be parsed
            env     - local environment to use. variables defined in strings
                overwrite the ones defined in environment
    """
    env = env or {}
    for i, string in enumerate(strings):  # pylint: disable=unused-variable
        # assert re.match(r"\w*=[\w\[\],'\"\(\)]*", string), \
        #    f"Failed parsing argument #{i}: \"{string}\". Only \"key=value\" are supported"
        _exec(string, None, env)
    return env

def insert_line_numbers(txt):
    return "\n".join([f"{n+1:03d}.\t{line}" for n, line in enumerate(txt.split("\n"))])

def _exec(cmd, globals: Optional[Dict[str, Any]] = None, locals: Optional[Dict[str, Any]] = None):  # pylint: disable=redefined-builtin
    """Some documentation

    :param cmd: ................
    :param globals: ................
    :param locals: ................
    :param description: ................
    """
    try:
        exec(cmd, globals, locals)  # pylint: disable=exec-used
    except (Exception, SyntaxError) as err:  # pylint: disable=broad-except
        error_class = err.__class__.__name__
        detail = err.args[0]
        tb = err.__traceback__
        line_number = (
            err.lineno
            if isinstance(err, SyntaxError)
            else traceback.extract_tb(tb)[-1][1]
        )
        traceback.print_exception(type(err), err, tb)
    else:
        return
    raise InterpreterError(f"{error_class} at line {line_number}: {detail}\n{cmd}")


class Confyg:
    def __init__(self, config, overwrite: Optional[Dict] = None):
        """Some documentation here

        :param config: ................
        :param overwrite: ................
        """
        self.tree = load_tree(config)
        update_ast(self.tree, overwrite)

    @functools.cached_property
    def string(self):
        return astunparse.unparse(self.tree)

    @functools.cached_property
    def dict(self):
        return parse_strings(self.string)

    def __call__(self):
        return self.dict

class _GridConfygIterator:
    def __init__(self, config_trees: Dict[Tuple, Confyg]):
        # make a copy of the iterable in order to avoid issues related to
        # the iterable being modified/accessed while iterating over it
        self._config_trees = copy.deepcopy(config_trees)
        self._keys = list(self._config_trees.keys())
        self._i = 0

    def __iter__(self) -> "_GridConfygIterator":
        return self

    def __next__(self) -> Tuple[Dict, Confyg]:
        try:
            key = self._keys[self._i]
            confyg = self._config_trees[key]
            self._i += 1
            return dict(key), confyg
        except IndexError:
            raise StopIteration() # pylint: disable=raise-missing-from

def load_tree(config) -> ast.Module:
    if isinstance(config, str) and os.path.isfile(config):
        logger.info(f"Loading config from file: {config}")
        with open(config) as config:
            config = config.read()
    if isinstance(config, str):
        config = ast.parse(config)
    elif not isinstance(config, ast.Module):
        raise FileNotFoundError(config)
    return config

class GridConfyg:
    def __init__(self, config, grid: Optional[Dict] = None, overwrite: Optional[Dict] = None):
        """Some documentation here

        :param config: ................
        :param overwrite: ................
        """
        tree = load_tree(config)
        grid = grid if grid is not None else {}
        overwrite = overwrite if overwrite is not None else {}

        self.config_trees = {}
        for grid_sample in product_kwargs(**grid):
            key = tuple(grid_sample.items())
            value = Confyg(copy.deepcopy(tree), {**grid_sample, **overwrite})
            self.config_trees[key] = value

    def __len__(self) -> int:
        return len(self.config_trees)

    def __iter__(self) -> _GridConfygIterator:
        return _GridConfygIterator(self.config_trees)

