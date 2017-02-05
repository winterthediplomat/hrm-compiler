import pytest
import hrmcompiler.parser as parser
from hrmcompiler.assembler import Assembler

def clean_output(assembly_str):
    return list(line.strip() for line in assembly_str.strip().splitlines())

#######################################################

def test_if_doublebranch():
    assembler = Assembler()
    transformed_ast = [
            parser.IfOp("ez", [parser.OutboxOp()],
                [parser.AssignOp("inbox", "emp")])]
    assembler.convert(transformed_ast)

    assert assembler.code == [
        "jez _hrm_1",
        "inbox",
        "jmp _hrm_endif_1",
        "_hrm_1:",
        "outbox",
        "_hrm_endif_1:"
    ]

def test_if_noelse():
    assembler = Assembler()
    transformed_ast = [parser.IfOp("ez", [parser.OutboxOp()], [])]
    assembler.convert(transformed_ast)

    assert assembler.code == clean_output("""
        jez _hrm_1
        jmp _hrm_endif_1
        _hrm_1:
        outbox
        _hrm_endif_1:
    """)

def test_nested_if():
    assembler = Assembler()
    transformed_ast = [
        parser.IfOp("ez", [
            parser.IfOp("ez", [], [])
            ], [])]
    assembler.convert(transformed_ast)

    assert assembler.code == clean_output("""
    jez _hrm_1
    jmp _hrm_endif_1
    _hrm_1:
        jez _hrm_2
        jmp _hrm_endif_2
        _hrm_2:
        _hrm_endif_2:
    _hrm_endif_1:
    """)

def test_nested_if_inside_else():
    assembler = Assembler()
    transformed_ast = [
        parser.IfOp("ez", [], [
            parser.IfOp("ez", [], [])
            ])]
    assembler.convert(transformed_ast)

    assert assembler.code == clean_output("""
    jez _hrm_1
        jez _hrm_2
        jmp _hrm_endif_2
        _hrm_2:
        _hrm_endif_2:
    jmp _hrm_endif_1
    _hrm_1:
    _hrm_endif_1:
    """)


