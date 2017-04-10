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

