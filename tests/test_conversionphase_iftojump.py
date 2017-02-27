import pytest
from hrmcompiler import parser as p
from hrmcompiler import conversion as c

def test_convert_iftojump_nothingchanged():
    code = [
        p.AssignOp("inbox", "emp"),
        p.SubOp("0"),
        p.OutboxOp()
    ]
    expected_ast = code
    ast = c.convert_iftojump(code)
    assert ast == expected_ast


def test_convert_iftojump_onlytruebranch():
    code = [
        p.IfOp("ez", [
            p.OutboxOp()
        ], [])]
    expected_ast = [
        p.JumpCondOp("jez", "_hrm_1"),
        p.JumpOp("_hrm_endif_1"),
        p.LabelStmt("_hrm_1"),
        p.OutboxOp(),
        p.LabelStmt("_hrm_endif_1")
    ]
    ast = c.convert_iftojump(code)
    assert ast == expected_ast

def test_convert_iftojump_onlytruebranch_consecutive():
    code = [
        p.IfOp("ez", [p.OutboxOp()], []),
        p.IfOp("ez", [p.OutboxOp()], [])]
    expected_ast = [
        # first IF
        p.JumpCondOp("jez", "_hrm_1"),
        p.JumpOp("_hrm_endif_1"),
        p.LabelStmt("_hrm_1"),
        p.OutboxOp(),
        p.LabelStmt("_hrm_endif_1"),
        # second IF
        p.JumpCondOp("jez", "_hrm_2"),
        p.JumpOp("_hrm_endif_2"),
        p.LabelStmt("_hrm_2"),
        p.OutboxOp(),
        p.LabelStmt("_hrm_endif_2")]
    ast = c.convert_iftojump(code)
    assert ast == expected_ast

def test_convert_iftojump_onlyfalsebranch():
    code = [
        p.IfOp("ez", [], [
            p.OutboxOp()
        ])]
    expected_ast = [
        p.JumpCondOp("jez", "_hrm_1"),
        p.OutboxOp(),
        p.JumpOp("_hrm_endif_1"),
        p.LabelStmt("_hrm_1"),
        p.LabelStmt("_hrm_endif_1")
    ]
    ast = c.convert_iftojump(code)
    assert ast == expected_ast

def test_convert_iftojump_onlyfalsebranch_consecutive():
    code = [
        p.IfOp("ez", [], [
            p.OutboxOp()
        ]),
        p.IfOp("ez", [], [
            p.OutboxOp()
        ])]
    expected_ast = [
        p.JumpCondOp("jez", "_hrm_1"),
        p.OutboxOp(),
        p.JumpOp("_hrm_endif_1"),
        p.LabelStmt("_hrm_1"),
        p.LabelStmt("_hrm_endif_1"),
        p.JumpCondOp("jez", "_hrm_2"),
        p.OutboxOp(),
        p.JumpOp("_hrm_endif_2"),
        p.LabelStmt("_hrm_2"),
        p.LabelStmt("_hrm_endif_2")
    ]
    ast = c.convert_iftojump(code)
    assert ast == expected_ast



