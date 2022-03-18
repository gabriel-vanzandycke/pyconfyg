import ast
import logging
from typing import Dict

logger = logging.getLogger(__name__)

def update_ast(
    tree: ast.Module,
    overwrite: Dict = None,
    allow_double_assignation: bool = False,
    allow_tuple_assignation: bool = False,
):
    if not overwrite:
        return {}

    met_targets = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if hasattr(target, "id"):
                assert allow_tuple_assignation or isinstance(
                    target, ast.Name
                ), "Tuple assignation is not allowed in config files (e.g. `a,b=1,2`). Impossible to overwrite '{}' of type '{}'".format(
                    target.id, type(target)
                )
                assert (
                    allow_double_assignation or target.id not in met_targets
                ), "Double assignation is not allowed in config files. '{}' seems to be assigned twice.".format(
                    target.id
                )
                if target.id in overwrite:
                    node.value = ast.parse(repr(overwrite.pop(target.id))).body[0].value
                    met_targets.append(target.id)
    # Add remaining keys
    for key, value in overwrite.items():
        tree.body.append(
            ast.Assign(
                [ast.Name(id=key, ctx=ast.Store())], ast.Constant(value, kind=None)
            )
        )
    ast.fix_missing_locations(tree)
    logging.warning(f"Unoverwritten parameters : {list(overwrite.keys())}")
    return overwrite
