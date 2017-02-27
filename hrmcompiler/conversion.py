from hrmcompiler.parser import IfOp
import hrmcompiler.parser as p

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

def convert_iftojump(ast):
    new_ast = []
    if_counter = 1
    for ast_item in ast:
        if type(ast_item) == IfOp:
            new_ast.append(p.JumpCondOp("j"+ast_item.condition, "_hrm_{0}".format(if_counter)))
            for op in ast_item.false_branch:
                new_ast.append(op)
            new_ast.append(p.JumpOp("_hrm_endif_{0}".format(if_counter)))
            new_ast.append(p.LabelStmt("_hrm_{0}".format(if_counter)))
            for op in ast_item.true_branch:
                new_ast.append(op)
            new_ast.append(p.LabelStmt("_hrm_endif_{0}".format(if_counter)))
            if_counter += 1
        else:
            new_ast.append(ast_item)
    return new_ast
