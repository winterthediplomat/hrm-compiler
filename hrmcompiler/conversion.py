from hrmcompiler.parser import IfOp
import hrmcompiler.parser as p
from pprint import pprint

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

def labels_in_ast(ast):
    assoc = dict()
    label_at_position = []
    saved_labels = []
    found_label = False
    for index, ast_item in enumerate(ast):
        if type(ast_item) == p.LabelStmt:
            label_at_position.append(None)
            saved_labels.append(ast_item.label_name)
            found_label = True
        else:
            if found_label:
                label_at_position.append(saved_labels)
                for label in saved_labels:
                    assoc[label] = index
                saved_labels = []
            else:
                label_at_position.append(None)

            found_label = False

    return (assoc, label_at_position)

def remove_unreachable_code(ast):
    minimized_ast = []
    labels_positions, label_at_pos = labels_in_ast(ast)

    # tree-like structure
    next_pointers = [None for instr in ast]
    visited = [False for instr in ast]
    assoc = [None for instr in ast]
    ic = 0
    jcond_stack = []
    last_was_jmp = False
    prev_ic = 0
    INSTRUCTIONS_NUM = len(ast)

    while ic < INSTRUCTIONS_NUM:
        # read instruction
        instr = ast[ic]
        prev_ic = ic
        last_was_jmp = False
        if not visited[ic]:
            # S_notvis
            if type(instr) == p.LabelStmt:
                # S_label
                ic += 1
            else:
                visited[ic] = True
                if type(instr) == p.JumpOp:
                    # S_jmp
                    _next_pos = labels_positions[instr.label_name]
                    if last_was_jmp:
                        next_pointers[prev_ic] = (_next_pos, -1)
                    else:
                        next_pointers[ic] = (_next_pos, -1)
                    assoc[_next_pos] = instr.label_name
                    ic = _next_pos
                    last_was_jmp = True
                else:
                    if type(instr) == p.JumpCondOp:
                        # S_jcond
                        jcond_stack.append(ic)
                        _jcond_pos = labels_positions[instr.label_name]
                        next_pointers[ic] = (ic+1, _jcond_pos)
                        assoc[_jcond_pos] = instr.label_name
                        ic += 1
                    else:
                        # S_normal
                        next_pointers[ic] = (ic+1, -1)
                        ic += 1
        else:
            if not jcond_stack:
                break
            # jcond_stack is not empty
            jcond_ic = jcond_stack.pop()
            _, ic = next_pointers[jcond_ic]

    minimized_ast = []
    for index, ast_item in enumerate(ast):
        if visited[index]:
            if assoc[index]:
                minimized_ast.append(p.LabelStmt(assoc[index]))
            minimized_ast.append(ast_item)

    return minimized_ast


def compress_jumps(ast):
    compressed_ast = []
    labels_positions, label_at_pos = labels_in_ast(ast)

    for index, ast_item in enumerate(ast):
        if type(ast_item) in [p.JumpOp, p.JumpCondOp]:
            jump_going_nowhere = False
            visited = [False for i in ast]
            _label = ast_item.label_name
            try:
                next_pos = labels_positions[_label]
            except KeyError:
                jump_going_nowhere = True

            if not jump_going_nowhere:
                while type(ast[next_pos]) == p.JumpOp and \
                    not visited[next_pos] and \
                    not jump_going_nowhere:
                    visited[next_pos] = True
                    _label = ast[next_pos].label_name
                    try:
                        next_pos = labels_positions[_label]
                    except KeyError:
                        jump_going_nowhere = True

            if jump_going_nowhere:
                pass
            elif type(ast_item) == p.JumpOp:
                compressed_ast.append(p.JumpOp(_label))
            else:
                compressed_ast.append(p.JumpCondOp(_label, ast_item.condition))
        else:
            compressed_ast.append(ast_item)

    return compressed_ast
