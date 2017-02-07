import pytest

from hrmcompiler.parser import IfOp, OutboxOp, LabelStmt, JumpOp, AssignOp
from hrmcompiler.conversion import convert_ifnz_to_ifez

def test_convert_nz_to_ez():
    start_ast = [IfOp("nz", [OutboxOp()], [])]
    expected_end_ast = [IfOp("ez", [], [OutboxOp()])]

    end_ast = convert_ifnz_to_ifez(start_ast)
    assert end_ast == expected_end_ast

def test_convert_nz_dont_touch_ez():
    start_ast = expected_end_ast = [IfOp("ez", [OutboxOp()], [])]

    end_ast = convert_ifnz_to_ifez(start_ast)
    assert end_ast == expected_end_ast

def test_convert_nz_biggerprogram():
    start_ast = [
            LabelStmt("test"),
            AssignOp(src="inbox", dst="emp"),
            IfOp("nz", [OutboxOp()], [AssignOp(src="inbox", dst="emp")]),
            JumpOp("test")
    ]

    expected_end_ast = [
            LabelStmt("test"),
            AssignOp(src="inbox", dst="emp"),
            IfOp("ez", [AssignOp(src="inbox", dst="emp")], [OutboxOp()]),
            JumpOp("test")
    ]

    end_ast = convert_ifnz_to_ifez(start_ast)
    assert end_ast == expected_end_ast

def test_convert_nz_nestedif():
    start_ast = [
            IfOp("ez",
                [IfOp("nz", [OutboxOp()], [JumpOp("test")])],
                [IfOp("ez", [JumpOp("test")], [OutboxOp()])]
            )]
    expected_end_ast = [
            IfOp("ez",
                [IfOp("ez", [JumpOp("test")], [OutboxOp()])],
                [IfOp("ez", [JumpOp("test")], [OutboxOp()])]
            )]

    end_ast = convert_ifnz_to_ifez(start_ast)
    assert end_ast == expected_end_ast
