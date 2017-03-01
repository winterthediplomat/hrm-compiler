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

def _convert_iftojump(ast, if_counter=0):
    new_ast = []
    for ast_item in ast:
        if type(ast_item) == IfOp:
            if_counter = if_counter + 1
            new_ast.append(p.JumpCondOp(condition="j"+ast_item.condition,
                label_name="_hrm_{0}".format(if_counter)))
            converted_false_branch, counter = _convert_iftojump(ast_item.false_branch, if_counter)
            for op in converted_false_branch:
                new_ast.append(op)
            new_ast.append(p.JumpOp("_hrm_endif_{0}".format(if_counter)))
            new_ast.append(p.LabelStmt("_hrm_{0}".format(if_counter)))
            converted_true_branch, counter = _convert_iftojump(ast_item.true_branch, counter)
            for op in converted_true_branch:
                new_ast.append(op)
            new_ast.append(p.LabelStmt("_hrm_endif_{0}".format(if_counter)))
            if_counter = counter
        else:
            new_ast.append(ast_item)
    return new_ast, if_counter

def convert_iftojump(ast):
    new_ast, counter = _convert_iftojump(ast)
    return new_ast
