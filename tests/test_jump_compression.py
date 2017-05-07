import pytest
import hrmcompiler.parser as parser
from hrmcompiler.conversion import compress_jumps, labels_in_ast
from pprint import pprint

# `jmp` instructions compression

def test_no_compress():
    expected_ast = start_ast = [
        parser.JumpOp("test"),
        parser.LabelStmt("test"),
        parser.OutboxOp()
    ]
    ast = compress_jumps(start_ast)
    assert expected_ast == ast

def test_compress_single_jump():
    start_ast = [
        parser.JumpOp("test"),
        parser.LabelStmt("test"),
        parser.JumpOp("wow"),
        parser.LabelStmt("wow"),
        parser.OutboxOp()
    ]
    expected_ast = [
        parser.JumpOp("wow"),
        parser.LabelStmt("test"),
        parser.JumpOp("wow"),
        parser.LabelStmt("wow"),
        parser.OutboxOp()
    ]
    ast = compress_jumps(start_ast)
    assert ast == expected_ast

def test_compress_multi_jump():
    start_ast = [
        parser.JumpOp("first"),
        parser.LabelStmt("first"), parser.JumpOp("second"),
        parser.LabelStmt("second"), parser.JumpOp("third"),
        parser.LabelStmt("third"), parser.JumpOp("fourth"),
        parser.LabelStmt("fourth"), parser.JumpOp("last"),
        parser.LabelStmt("last"), parser.OutboxOp()
    ]
    expected_ast = [
        parser.JumpOp("last"),
        parser.LabelStmt("first"), parser.JumpOp("last"),
        parser.LabelStmt("second"), parser.JumpOp("last"),
        parser.LabelStmt("third"), parser.JumpOp("last"),
        parser.LabelStmt("fourth"), parser.JumpOp("last"),
        parser.LabelStmt("last"), parser.OutboxOp()
    ]
    ast = compress_jumps(start_ast)
    assert ast == expected_ast

def test_avoid_loop():
    start_ast = [
        parser.LabelStmt("test"),
        parser.JumpOp("test")
    ]
    expected_ast = start_ast
    ast = compress_jumps(start_ast)
    assert ast == expected_ast

# `jcond` instructions compression

def test_compress_jcond_no_compress():
    start_ast = [
        parser.JumpCondOp("label", "ez"),
          parser.OutboxOp(),
          parser.JumpOp("endif"),
        parser.LabelStmt("label"),
          parser.OutboxOp(),
        parser.LabelStmt("endif"),
        parser.OutboxOp()
    ]
    expected_ast = start_ast
    ast = compress_jumps(start_ast)
    assert ast == expected_ast

def test_compress_jcond_single():
    start_ast = [
        parser.LabelStmt("start"),
        parser.AssignOp(src="inbox", dst="emp"),
        parser.JumpCondOp("if", "ez"),
            parser.OutboxOp(),
            parser.JumpOp("endif"),
        parser.LabelStmt("if"),
            parser.JumpOp("start"),
        parser.LabelStmt("endif"),
        parser.OutboxOp()
    ]
    expected_ast = [
        parser.LabelStmt("start"),
        parser.AssignOp(src="inbox", dst="emp"),
        parser.JumpCondOp("start", "ez"),
            parser.OutboxOp(),
            parser.JumpOp("endif"),
        parser.LabelStmt("if"),
            parser.JumpOp("start"),
        parser.LabelStmt("endif"),
        parser.OutboxOp()
    ]
    ast = compress_jumps(start_ast)
    assert ast == expected_ast

def test_compress_jcond_multi():
    start_ast = [
        parser.LabelStmt("start"),
        parser.AssignOp(src="inbox", dst="emp"),
        parser.JumpCondOp("if", "ez"),
            parser.OutboxOp(),
            parser.JumpOp("endif"),
        parser.LabelStmt("if"),
            parser.JumpOp("interm_first"),
        parser.LabelStmt("endif"),
        parser.OutboxOp(),
        parser.LabelStmt("interm_first"),
        parser.JumpOp("interm_last"),
        parser.LabelStmt("interm_last"),
        parser.JumpOp("start")
    ]
    expected_ast = [
        parser.LabelStmt("start"),
        parser.AssignOp(src="inbox", dst="emp"),
        parser.JumpCondOp("start", "ez"),
            parser.OutboxOp(),
            parser.JumpOp("endif"),
        parser.LabelStmt("if"),
            parser.JumpOp("start"),
        parser.LabelStmt("endif"),
        parser.OutboxOp(),
        parser.LabelStmt("interm_first"),
        parser.JumpOp("start"),
        parser.LabelStmt("interm_last"),
        parser.JumpOp("start")
    ]
    ast = compress_jumps(start_ast)
    assert ast == expected_ast

def test_jcond_avoid_loop():
    start_ast = [
        parser.LabelStmt("test"),
        parser.JumpCondOp("test", "ez"),
        parser.OutboxOp(),
        parser.JumpOp("test"),
    ]
    expected_ast = start_ast
    ast = compress_jumps(start_ast)
    assert ast == expected_ast

def test_jcond_lone_label():
    start_ast = [
        parser.LabelStmt("start"),
        parser.AssignOp(src="inbox", dst="emp"),
        parser.JumpCondOp("if", "ez"),
            parser.JumpOp("start"),
            parser.JumpOp("_generated_endif"),
        parser.LabelStmt("if"),
            parser.JumpOp("start"),
        parser.LabelStmt("_generated_endif")
    ]
    expected_ast = [
        parser.LabelStmt("start"),
        parser.AssignOp(src="inbox", dst="emp"),
        parser.JumpCondOp("start", "ez"),
            parser.JumpOp("start"),
        parser.LabelStmt("if"),
            parser.JumpOp("start"),
        parser.LabelStmt("_generated_endif")
    ]
    ast = compress_jumps(start_ast)
    assert ast == expected_ast

# `labels_in_ast`

def test_labelinast_valid_access():
    start_ast = [
        parser.LabelStmt("test"),
        parser.JumpOp("test")
    ]
    labels_positions, _ = labels_in_ast(start_ast)
    assert "test" in labels_positions

def test_labelinast_no_labels():
    start_ast = []
    start_ast_2 = [parser.OutboxOp()]
    labels_positions, _ = labels_in_ast(start_ast)
    labels_positions_2, _ = labels_in_ast(start_ast_2)
    assert not len(labels_positions)
    assert not len(labels_positions_2)

def test_labelinast_nojump():
    start_ast = [
        parser.OutboxOp(),
        parser.LabelStmt("test"),
        parser.OutboxOp()
    ]
    labels_positions, _ = labels_in_ast(start_ast)
    assert "test" in labels_positions
    assert labels_positions["test"] == 2

def test_labelinast_invalid_access():
    start_ast = [
        parser.OutboxOp(),
        parser.LabelStmt("test")
    ]
    labels_positions, _ = labels_in_ast(start_ast)
    assert "test" not in labels_positions

def test_dont_optimize_conditional_jumps():
    """
    if ez then
        # nothing, but the `jez` must not be removed!
        # if removed, the program becomes only `outbox`,
        # that is incorrect.
    else
        outbox
    endif
    """
    start_ast = [
            parser.JumpCondOp(label_name='_hrm_1', condition='jez'),
            parser.OutboxOp(),
            parser.JumpOp(label_name="_hrm_endif_1"),
            parser.LabelStmt(label_name="_hrm_1"),
            parser.LabelStmt(label_name="_hrm_endif_1")
    ]
    ast = compress_jumps(start_ast)
    assert parser.JumpCondOp(label_name="_hrm_1", condition="jez") in ast
