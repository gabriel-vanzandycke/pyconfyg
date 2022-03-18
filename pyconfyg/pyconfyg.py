import ast
import copy
import functools
import itertools
import re
import traceback
import warnings

import astunparse

from .exceptions import InterpreterError


def update_ast(tree, overwrite, allow_double_assignation=False, allow_tuple_assignation=False):
    met_targets = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if hasattr(target, "id"):
                assert allow_tuple_assignation or isinstance(target, ast.Name), \
                    "Tuple assignation is not allowed in config files (e.g. `a,b=1,2`). Impossible to overwrite '{}' of type '{}'".format(target.id, type(target))
                assert allow_double_assignation or target.id not in met_targets, \
                    "Double assignation is not allowed in config files. '{}' seems to be assigned twice.".format(target.id)
                if target.id in overwrite:
                    node.value = ast.parse(repr(overwrite.pop(target.id))).body[0].value
                    met_targets.append(target.id)
    # Add remaining keys
    for key, value in overwrite.items():
        tree.body.append(ast.Assign([ast.Name(id=key, ctx=ast.Store())], ast.Constant(value, kind=None)))
    ast.fix_missing_locations(tree)
    return overwrite

def product_kwargs(**kwargs):
    kvs = []
    for k in kwargs:
        try:
            kvs.append([(k, v) for v in kwargs[k]])
        except BaseException as e:
            raise SyntaxError(f"Error parsing: `{k}:{kwargs[k]}`. Expected an iterable") from e
    yield from [dict(kv) for kv in itertools.product(*kvs)]

def parse_strings(*strings, env=None):
    """ Parses strings of 'k=v' by using builtin exec and returns a dictionary
        of the created symbols and their value.
        Arguments:
            strings - strings to be parsed
            env     - local environment to use. variables defined in strings
                overwrite the ones defined in environment
    """
    env = env or {}
    for i, string in enumerate(strings): # pylint: disable=unused-variable
        #assert re.match(r"\w*=[\w\[\],'\"\(\)]*", string), \
        #    f"Failed parsing argument #{i}: \"{string}\". Only \"key=value\" are supported"
        _exec(string, None, env, description="parsable strings")
    return env

# from https://stackoverflow.com/a/28836286/1782553
def _exec(cmd, globals=None, locals=None, description='source string'): # pylint: disable=redefined-builtin
    try:
        exec(cmd, globals, locals) # pylint: disable=exec-used
    except (Exception, SyntaxError) as err: # pylint: disable=broad-except
        error_class = err.__class__.__name__
        detail = err.args[0]
        tb = err.__traceback__
        line_number = err.lineno if isinstance(err, SyntaxError) else traceback.extract_tb(tb)[-1][1]
        traceback.print_exception(type(err), err, tb)
    else:
        return
    raise InterpreterError("%s at line %d of %s: %s\n%s" % (error_class, line_number, description, detail, cmd))

class Confyg():
    def __init__(self, tree):
        self.tree = tree
    @functools.cached_property
    def string(self):
        return astunparse.unparse(self.tree)
    @functools.cached_property
    def dict(self):
        return parse_strings(self.string)
    def __call__(self):
        return self.dict

class PyConfyg():
    i = 0
    def __init__(self, config_file, grid_dict, kwargs_dict):
        fd = open(config_file, 'r') if isinstance(config_file, str) else config_file
        tree = ast.parse(fd.read())
        if isinstance(config_file, str):
            fd.close()
        self.config_trees = tuple({
            tuple(overwrite.items()): Confyg(self._update_ast(tree, {**overwrite, **kwargs_dict}))
                             for overwrite in product_kwargs(**grid_dict or {})
        }.items())

    @staticmethod
    def _update_ast(config_tree, grid_sample):
        unoverwritten = {}
        tree = copy.deepcopy(config_tree)
        unoverwritten.update(**update_ast(tree, grid_sample))
        warnings.warn("Unoverwritten config grid : ", list(unoverwritten.keys()))
        return tree

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if self.i < len(self.config_trees):
            self.i += 1
            key, confyg = self.config_trees[self.i-1]
            return dict(key), confyg

        raise StopIteration()
