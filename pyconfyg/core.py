import ast
import copy
import functools
import itertools
import logging
import os
import re
import traceback
import warnings
from typing import Any, Dict, Iterator, Optional, Sequence, Tuple

import astunparse

from pyconfyg.ast import update_ast
from pyconfyg.exceptions import InterpreterError


def product_kwargs(**kwargs) -> Iterator[Dict]:
    """Some documentation.

    :param kwargs: ................
    :returns: Iterator of dict objects containing ................
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
        _exec(string, None, env, description="parsable strings")
    return env


def _exec(
    cmd,
    globals: Optional[Dict[str, Any]] = None,
    locals: Optional[Dict[str, Any]] = None,
    description: str = "source string",
):  # pylint: disable=redefined-builtin
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
    raise InterpreterError(
        "%s at line %d of %s: %s\n%s"
        % (error_class, line_number, description, detail, cmd)
    )


class Confyg:
    def __init__(self, tree: ast.Module):
        self.tree = tree

    @functools.cached_property
    def string(self):
        return astunparse.unparse(self.tree)

    @functools.cached_property
    def dict(self):
        return parse_strings(self.string)

    def __call__(self):
        return self.dict


class _PyConfigIterator:
    def __init__(self, config_trees: Sequence[Tuple[Tuple, Confyg]]):
        # make a copy of the iterable in order to avoid issues related to
        # the iterable being modified/accessed while iterating over it
        self._config_trees = copy.deepcopy(config_trees)
        self._i = 0

    def __iter__(self) -> "_PyConfigIterator":
        return self

    def __next__(self) -> Tuple[Dict, Confyg]:
        try:
            key, confyg = self._config_trees[self._i]
            self._i += 1
        except IndexError:
            raise StopIteration()
        else:
            return dict(key), confyg


class PyConfyg:
    def __init__(
        self,
        config_file: str,
        grid_dict: Optional[Dict] = None,
        kwargs_dict: Optional[Dict] = None,
    ):
        """Some documentation here

        :param config_file: ................
        :param grid_dict: ................
        :param kwargs_dict: ................
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        grid_dict = grid_dict if grid_dict is not None else {}
        kwargs_dict = kwargs_dict if kwargs_dict is not None else {}

        if os.path.isfile(config_file):
            self.logger.info(f"Loading config file from {config_file}")
            config_file = self._load_config_file(config_file)

        tree = ast.parse(config_file)

        config_trees = {}
        for overwrite in product_kwargs(**grid_dict):
            key = tuple(overwrite.items())
            value = Confyg(self._update_ast(tree, {**overwrite, **kwargs_dict}))
            config_trees[key] = value
        self.config_trees = tuple(config_trees.items())

    @classmethod
    def _load_config_file(cls, config_file: str) -> str:
        try:
            with open(config_file, "r") as f:
                config_file = f.read()
        except FileNotFoundError:
            # handle file not found error here
            raise
        except IOError:
            # handle IO error here
            raise
        return config_file

    @staticmethod
    def _update_ast(config_tree: ast.Module, grid_sample: Dict):
        unoverwritten = {}
        tree = copy.deepcopy(config_tree)
        unoverwritten.update(**update_ast(tree, grid_sample))
        warnings.warn(f"Unoverwritten config grid : {list(unoverwritten.keys())}")

        return tree

    def __len__(self) -> int:
        return len(self.config_trees)

    def __iter__(self) -> _PyConfigIterator:
        return _PyConfigIterator(self.config_trees)
