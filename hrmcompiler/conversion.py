from hrmcompiler.parser import IfOp

def convert_ifnz_to_ifez(ast):
    new_ast = []
    for ast_item in ast:
        if type(ast_item) == IfOp:
            nz_true_branch = convert_ifnz_to_ifez(ast_item.true_branch)
            nz_false_branch = convert_ifnz_to_ifez(ast_item.false_branch)
            if ast_item.condition == "nz":
                new_ast.append(IfOp("ez", nz_false_branch, nz_true_branch))
            else:
                new_ast.append(IfOp(ast_item.condition, nz_true_branch, nz_false_branch))
        else:
            new_ast.append(ast_item)
    return new_ast
