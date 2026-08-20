import json
from .asts import ConfigsAST,AtomConfigAST

def ast_to_dict(ast):
    result = {}
    if isinstance(ast,ConfigsAST):
        for child in ast.children():
            result[child.section_name] = ast_to_dict(child) # type:ignore
        return result
    for child in ast.children():
        if isinstance(child,AtomConfigAST):
            result[child.name] = child.value
        else:
            result[child.section_name] = ast_to_dict(child) # type:ignore
    return result

def to_json(ast) -> str:
    json_ast = ast_to_dict(ast)
    return json.dumps(json_ast)