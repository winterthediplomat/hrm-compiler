from hrmcompiler.parser import IfOp
import hrmcompiler.parser as p
from pprint import pprint
import itertools as it

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
    hrm_unreachable_used = False

    def next_ic_in_jcond_stack(jcond_stack):
        while jcond_stack:
            jcond_ic = jcond_stack.pop()
            _, maybe_ic = next_pointers[jcond_ic]
            if maybe_ic != None:
                return maybe_ic
        return None

    while ic < INSTRUCTIONS_NUM or jcond_stack:
        # if we reached the last instruction of the program,
        # but we still have some unexplored `jcond`s, we must explore
        # these "forgotten" paths too!
        if not (ic < INSTRUCTIONS_NUM) and jcond_stack:
            ic = next_ic_in_jcond_stack(jcond_stack) or ic
            if ic >= INSTRUCTIONS_NUM and not jcond_stack:
                break

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
                    try:
                        _next_pos = labels_positions[instr.label_name]
                        if last_was_jmp:
                            next_pointers[prev_ic] = (_next_pos, -1)
                        else:
                            next_pointers[ic] = (_next_pos, -1)
                        if assoc[_next_pos] != None:
                            assoc[_next_pos].append(instr.label_name)
                        else:
                            assoc[_next_pos] = [instr.label_name]
                        ic = _next_pos
                        last_was_jmp = True
                    except KeyError:
                        _next_pos = ic
                        if last_was_jmp:
                            next_pointers[prev_ic] = (_next_pos, -1)
                        else:
                            next_pointers[ic] = (_next_pos, -1)
                        ast[ic] = p.JumpOp("_hrm_unreachable")
                        hrm_unreachable_used = True
                        ic = INSTRUCTIONS_NUM
                else:
                    if type(instr) == p.JumpCondOp:
                        # S_jcond
                        jcond_stack.append(ic)
                        try:
                            _jcond_pos = labels_positions[instr.label_name]
                            next_pointers[ic] = (ic+1, _jcond_pos)
                            ic += 1
                            if assoc[_jcond_pos] != None:
                                assoc[_jcond_pos].append(instr.label_name)
                            else:
                                assoc[_jcond_pos] = [instr.label_name]
                        except KeyError:
                            _jcond_pos = None
                            ast[ic] = p.JumpCondOp("_hrm_unreachable", instr.condition)
                            next_pointers[ic] = (ic+1, _jcond_pos)
                            ic += 1
                            hrm_unreachable_used = True
                    else:
                        # S_normal
                        next_pointers[ic] = (ic+1, -1)
                        ic += 1
        else:
            if not jcond_stack:
                break
            ic = next_ic_in_jcond_stack(jcond_stack) or ic

    minimized_ast = []
    for index, ast_item in enumerate(ast):
        if visited[index]:
            if assoc[index]:
                for label_name in sorted(set(assoc[index])):
                    minimized_ast.append(p.LabelStmt(label_name))
            minimized_ast.append(ast_item)

    if hrm_unreachable_used:
        minimized_ast.append(p.LabelStmt("_hrm_unreachable"))

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
                # get the first position executable by `_label`
                next_pos = labels_positions[_label]
            except KeyError:
                jump_going_nowhere = True
                # even though a jump, either conditional or unconditional, redirects to a label
                # that is _not_ associated to any instruction, removing conditional
                # jumps alters the logic of the program
                compressed_ast.append(ast_item)
                continue

            while type(ast[next_pos]) == p.JumpOp and \
                not visited[next_pos] and \
                not jump_going_nowhere:
                visited[next_pos] = True
                _label = ast[next_pos].label_name
                try:
                    next_pos = labels_positions[_label]
                except KeyError:
                    jump_going_nowhere = True

            if type(ast_item) == p.JumpOp:
                compressed_ast.append(p.JumpOp(_label))
            else:
                compressed_ast.append(p.JumpCondOp(_label, ast_item.condition))
        else:
            compressed_ast.append(ast_item)

    return compressed_ast

from collections import Counter

def fix_jmp_then_label(ast):
    new_ast = []
    labels_positions, label_at_pos = labels_in_ast(ast)

    lst = []
    for ast_item in ast:
        if type(ast_item) in [p.JumpOp, p.JumpCondOp]:
            lst.append(ast_item.label_name)
    references_counter = Counter(lst)

    skip_label = False
    next_skip_label = False
    for (a_instr, b_instr) in it.zip_longest(ast, ast[1:]):
        is_jmp_then_label = (type(a_instr) == p.JumpOp or type(a_instr) == p.JumpCondOp) and type(b_instr) == p.LabelStmt
        if is_jmp_then_label:
            same_name = a_instr.label_name == b_instr.label_name
            if same_name:
                is_referenced_once = references_counter[b_instr.label_name] == 1
                if same_name:
                    if is_referenced_once:
                        next_skip_label = True
                    else:
                        # write the label (don't skip), but don't write the jmp instruction
                        pass
                else:
                    new_ast.append(a_instr)
            else:
                new_ast.append(a_instr)
        elif not skip_label:
            new_ast.append(a_instr)

        skip_label = next_skip_label
        next_skip_label = False

    return new_ast
