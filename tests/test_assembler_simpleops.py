import pytest
from hrmcompiler import parser
from hrmcompiler.assembler import Assembler

def get_assembly(ast_code):
    converter = Assembler()
    converter.convert(ast_code)
    return converter.code

################ AssignOp ################

def test_inbox():
    code = [parser.AssignOp("inbox", "emp")]
    assert get_assembly(code) == ["inbox"]

def test_copyfrom():
    code = [parser.AssignOp("3", "emp")]
    assert get_assembly(code) == ["copyfrom 3"]

def test_copyto():
    code = [parser.AssignOp("emp", "3")]
    assert get_assembly(code) == ["copyto 3"]

def test_copyfrom_alias():
    code = [parser.AliasStmt(3, "knownLabel"), parser.AssignOp("knownLabel", "emp")]
    assert get_assembly(code) == ["copyfrom 3"]

def test_copyfrom_equivalence():
    alias_ast = [parser.AliasStmt(3, "knownLabel"), parser.AssignOp("knownLabel", "emp")]
    tile_ast = [parser.AssignOp("3", "emp")]
    assert get_assembly(alias_ast) == get_assembly(tile_ast)

def test_copyfrom_undefined_label():
    code = [parser.AssignOp("unknownLabel", "emp")]

    with pytest.raises(ValueError):
        get_assembly(code)

###########################################

def test_outbox():
    code = [parser.OutboxOp()]
    converter = Assembler()
    converter.convert(code)

    assert converter.code == ["outbox"]

##########################################

def test_incr_withnumber():
    code = [parser.IncrOp("0")]
    assert get_assembly(code) == ["incr 0"]

def test_incr_withlabel():
    code = [parser.AliasStmt("0", "mylabel"), parser.IncrOp("mylabel")]
    assert get_assembly(code) == ["incr 0"]

