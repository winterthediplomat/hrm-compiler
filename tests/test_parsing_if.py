import hrmcompiler.parser as parser
from io import StringIO
import pyparsing
import pytest


#######################################################

def test_if_single_op():
    code = """
    emp = inbox
    if ez then
        emp = inbox
    endif
    """
    with StringIO(code) as f:
        ast = parser.parse_it(f)

    assert type(ast[1]) == parser.IfOp
    assert ast[1].condition == "ez"
    assert ast[1].true_branch == [parser.AssignOp("inbox", "emp")]

def test_if_multiple_ops():
    code = """
    start:
    emp = inbox
    if ez then
        outbox
        jmp start
    endif
    """
    with StringIO(code) as f:
        ast = parser.parse_it(f)

    if_op = ast[2]
    assert type(if_op) == parser.IfOp
    assert if_op.condition == "ez"
    assert if_op.true_branch == [
            parser.OutboxOp(),
            parser.JumpOp("start")
    ]

def test_if_noelse():
    code = """
    if ez then
        outbox
    endif
    """
    with StringIO(code) as f:
        ast = parser.parse_it(f)

    if_op = ast[0]
    assert if_op.false_branch == []

def test_if_doublebranch():
    code = """
    start:
    emp = inbox
    if ez then
        outbox
    else
        jmp start
    endif
    """
    with StringIO(code) as f:
        ast = parser.parse_it(f)

    if_op = ast[2]
    assert type(if_op) == parser.IfOp
    assert if_op.condition == "ez"
    assert if_op.true_branch == [parser.OutboxOp()]
    assert if_op.false_branch == [parser.JumpOp("start")]

#########################################

def test_if_nz():
    code = """
    if nz then
        outbox
    endif
    """
    with StringIO(code) as f:
        ast = parser.parse_it(f)

    if_op = ast[0]
    assert type(if_op) == parser.IfOp
    assert if_op.condition == "nz"
