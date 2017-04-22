import pytest
import hrmcompiler.parser as parser
from hrmcompiler.conversion import compress_jumps
from pprint import pprint

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

