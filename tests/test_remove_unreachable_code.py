import pytest
from hrmcompiler import parser
from hrmcompiler.conversion import convert_iftojump
from hrmcompiler.conversion import remove_unreachable_code
from io import StringIO
from pprint import pprint

def labels_in_ast(ast):
    labels = set()
    for ast_item in ast:
        if type(ast_item) == parser.IfOp:
            labels = labels.union(labels_in_ast(ast.true_branch))
            labels = labels.union(labels_in_ast(ast.false_branch))
        elif type(ast_item) == parser.LabelStmt:
            labels.add(ast_item.label_name)
    return labels

def test_single_operation():
    start_ast = [parser.OutboxOp()]
    ast = remove_unreachable_code(start_ast)

    assert start_ast == ast

def test_endless_program_1():
    start_ast = [parser.LabelStmt("label"), parser.AssignOp("inbox", "emp"), parser.JumpOp("label")]
    ast = remove_unreachable_code(start_ast)

    assert start_ast == ast

def test_endless_program_2():
    start_ast = [parser.LabelStmt("label"), parser.JumpOp("label")]
    ast = remove_unreachable_code(start_ast)

    assert start_ast == ast

def test_skip_operation():
    start_ast = [
            parser.AssignOp("inbox", "emp"),
            parser.JumpOp("label"),
            parser.OutboxOp(),
            parser.LabelStmt("label"),
            parser.AddOp("tmp")
    ]
    expected_ast = [
            parser.AssignOp("inbox", "emp"),
            parser.JumpOp("label"),
            parser.LabelStmt("label"),
            parser.AddOp("tmp")
    ]

    ast = remove_unreachable_code(start_ast)
    assert ast == expected_ast

def test_jcond_no_jump_in_false():
    start_ast = [
        parser.AssignOp("inbox", "emp"),
        parser.JumpCondOp(condition="ez", label_name="truebranch"),
          parser.OutboxOp(),
        parser.LabelStmt("truebranch"),
          parser.AddOp("tmp")
        ]

    ast = remove_unreachable_code(start_ast)
    assert ast == start_ast

def test_dont_remove_series_of_jumps():
    start_ast = [
        parser.JumpOp("jump1"),
        parser.LabelStmt("jump1"), parser.JumpOp("jump2"),
        parser.LabelStmt("jump2"), parser.JumpOp("jump3"),
        parser.LabelStmt("jump3"), parser.JumpOp("jump4"),
        parser.LabelStmt("jump4"), parser.AssignOp("inbox", "emp")
    ]

    ast = remove_unreachable_code(start_ast)
    assert ast == start_ast

def test_still_reachable():
    start_ast = [
        parser.JumpOp("skip"),
        parser.LabelStmt("ahah"), parser.OutboxOp(),
        parser.LabelStmt("skip"), parser.JumpOp("ahah")
    ]

    ast = remove_unreachable_code(start_ast)
    assert ast == start_ast

def test_dont_keep_only_last_label_on_instruction():
    start_ast = [
        parser.AssignOp(src='inbox', dst='emp'),
        parser.JumpCondOp(label_name='_hrm_1', condition='jez'),
        parser.OutboxOp(),
        parser.JumpOp(label_name="_hrm_endif_1"),
        parser.LabelStmt("_hrm_1"),
        parser.LabelStmt("_hrm_endif_1"),
        parser.AssignOp(src="inbox", dst="emp")
    ]
    ast = remove_unreachable_code(start_ast)
    assert parser.LabelStmt("_hrm_endif_1") in ast
    assert parser.LabelStmt("_hrm_1") in ast

def test_no_duplicated_labels_on_same_point():
    start_ast = [
        parser.AssignOp(src="inbox", dst="emp"),
        parser.JumpOp("skip"),
        parser.LabelStmt("comehere"),
        parser.OutboxOp(),
        parser.LabelStmt("skip"),
        parser.JumpOp("comehere")
    ]
    ast = remove_unreachable_code(start_ast)

    comehere_counter = sum(1 for ast_item in ast \
                    if type(ast_item) == parser.LabelStmt \
                        and ast_item.label_name == "comehere")
    assert comehere_counter == 1

    start_ast = [
        parser.AssignOp(src="inbox", dst="emp"),
        parser.JumpOp("comehere"),
        parser.LabelStmt("comehere"),
        parser.OutboxOp(),
        parser.LabelStmt("skip"),
        parser.JumpOp("comehere")
    ]
    ast = remove_unreachable_code(start_ast)

    comehere_counter = sum(1 for ast_item in ast \
                    if type(ast_item) == parser.LabelStmt \
                        and ast_item.label_name == "comehere")
    assert comehere_counter == 1

    start_ast = [
        parser.AssignOp(src="inbox", dst="emp"),
        parser.JumpCondOp("comehere", "jez"),
        parser.JumpOp("comehere"),
        parser.LabelStmt("comehere"),
        parser.OutboxOp(),
        parser.LabelStmt("skip"),
        parser.JumpOp("comehere")
    ]
    ast = remove_unreachable_code(start_ast)

    comehere_counter = sum(1 for ast_item in ast \
                    if type(ast_item) == parser.LabelStmt \
                        and ast_item.label_name == "comehere")
    assert comehere_counter == 1

def test_unreachable_condjumps():
    start_ast = [
        parser.AssignOp(src="inbox", dst="emp"),
        parser.JumpCondOp("_hrm_1", "jez"),
        parser.OutboxOp(),
        parser.LabelStmt("_hrm_1"),
        parser.LabelStmt("_hrm_endif_1")
    ]
    expected_ast = [
        parser.AssignOp(src="inbox", dst="emp"),
        parser.JumpCondOp("_hrm_unreachable", "jez"),
        parser.OutboxOp(),
        parser.LabelStmt("_hrm_unreachable")
    ]
    ast = remove_unreachable_code(start_ast)
    assert ast == expected_ast

def test_no_operation_ignored_in_nonlooping_code():
    start_ast = [
        parser.JumpCondOp("_hrm_1", "jez"),
            parser.IncrOp("a_field"),
            parser.JumpOp("the_fence"),
        parser.LabelStmt("_hrm_1"),
            parser.IncrOp("b_field"),
        parser.LabelStmt("the_fence"),
        parser.IncrOp("c_field")
    ]
    ast = remove_unreachable_code(start_ast)
    assert parser.IncrOp("b_field") in start_ast
    assert parser.IncrOp("b_field") in ast

def test_unreachable_jumps():
    start_ast = [
        parser.LabelStmt("start"),
        parser.AssignOp(src="inbox", dst="emp"),
        parser.JumpOp("label_a"),
        parser.LabelStmt("label_a"),
        parser.JumpOp("label_b"),
        parser.LabelStmt("label_b"),
        parser.JumpOp("label_c"),
        parser.LabelStmt("label_c"),
        parser.JumpOp("label_z"),
        parser.JumpOp("start"),
        parser.LabelStmt("label_z")
    ]
    expected_ast = [
        parser.AssignOp(src="inbox", dst="emp"),
        # the indented part is needed in the test
        # it would be optimized because of the previous
        # 'jump compression' optimization
        # but every jump here is reachable if the
        # code is passed as in the test.
             parser.JumpOp("label_a"),
             parser.LabelStmt("label_a"),
             parser.JumpOp("label_b"),
             parser.LabelStmt("label_b"),
             parser.JumpOp("label_c"),
             parser.LabelStmt("label_c"),
        parser.JumpOp("_hrm_unreachable"),
        parser.LabelStmt("_hrm_unreachable")
    ]
    ast = remove_unreachable_code(start_ast)
    assert ast == expected_ast
