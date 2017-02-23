import pytest
from hrmcompiler import parser
from hrmcompiler.assembler import Assembler

def get_assembly(ast_code):
    converter = Assembler()
    converter.convert(ast_code)
    return converter.code

def clean_output(assembly_str):
    return list(line.strip() for line in assembly_str.strip().splitlines())

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

def test_copyto_alias():
    code = [parser.AliasStmt(3, "knownLabel"), parser.AssignOp("emp", "knownLabel")]
    assert get_assembly(code) == ["copyto 3"]

def test_copyfrom_equivalence():
    alias_ast = [parser.AliasStmt(3, "knownLabel"), parser.AssignOp("knownLabel", "emp")]
    tile_ast = [parser.AssignOp("3", "emp")]
    assert get_assembly(alias_ast) == get_assembly(tile_ast)

def test_copyto_equivalence():
    alias_ast = [parser.AliasStmt(3, "knownLabel"), parser.AssignOp("emp", "knownLabel")]
    tile_ast = [parser.AssignOp("emp", "3")]
    assert get_assembly(alias_ast) == get_assembly(tile_ast)

def test_copyfrom_address():
    code = [parser.AssignOp(parser.AddressOf("3"), "emp")]
    assert get_assembly(code) == ["copyfrom [3]"]

def test_copyfrom_addressof_alias():
    code = [parser.AliasStmt(3, "knownLabel"), parser.AssignOp(parser.AddressOf("knownLabel"), "emp")]
    assert get_assembly(code) == ["copyfrom [3]"]

def test_copyto_address():
    code = [parser.AssignOp("emp", parser.AddressOf("3"))]
    assert get_assembly(code) == ["copyto [3]"]

def test_copyto_addressof_alias():
    code = [parser.AliasStmt(3, "knownLabel"), parser.AssignOp("emp", parser.AddressOf("knownLabel"))]
    assert get_assembly(code) == ["copyto [3]"]

def test_copyfrom_undefined_label():
    code = [parser.AssignOp("unknownLabel", "emp")]

    with pytest.raises(ValueError):
        get_assembly(code)

def test_copyto_undefined_label():
    code = [parser.AssignOp("emp", "unknownLabel")]
    with pytest.raises(ValueError):
        get_assembly(code)

def test_copyfrom_undefined_addressof_alias():
    code = [parser.AssignOp(parser.AddressOf("unknownLabel"), "emp")]

    with pytest.raises(ValueError):
        get_assembly(code)

def test_copyto_undefined_addressof_alias():
    code = [parser.AssignOp("emp", parser.AddressOf("unknownLabel"))]

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

def test_incr_address_withnumber():
    code = [parser.IncrOp(parser.AddressOf("0"))]
    assert get_assembly(code) == ["incr [0]"]

def test_incr_address_withlabel():
    code = [parser.AliasStmt("0", "mylabel"), parser.IncrOp(parser.AddressOf("mylabel"))]
    assert get_assembly(code) == ["incr [0]"]

##########################################

def test_decr_withnumber():
    code = [parser.DecrOp("0")]
    assert get_assembly(code) == ["decr 0"]

def test_decr_withlabel():
    code = [parser.AliasStmt("0", "mylabel"), parser.DecrOp("mylabel")]
    assert get_assembly(code) == ["decr 0"]

def test_decr_address_withnumber():
    code = [parser.DecrOp(parser.AddressOf("0"))]
    assert get_assembly(code) == ["decr [0]"]

def test_decr_address_withlabel():
    code = [parser.AliasStmt("0", "mylabel"), parser.DecrOp(parser.AddressOf("mylabel"))]
    assert get_assembly(code) == ["decr [0]"]

################# add ####################

def test_add_tilenumber():
    code = [parser.AddOp("3")]
    assert get_assembly(code) == ["add 3"]

def test_add_addressed_tilenumber():
    code = [parser.AddOp(parser.AddressOf("3"))]
    assert get_assembly(code) == ["add [3]"]

def test_add_tilealias():
    code = [
        parser.AliasStmt(tile_no="3", symbolic_name="myTile"),
        parser.AssignOp("inbox", "emp"),
        parser.AssignOp("emp", "myTile"),
        parser.AddOp("myTile")
    ]
    assert get_assembly(code) == clean_output("""
    inbox
    copyto 3
    add 3
    """)

def test_add_addressed_tilealias():
    code = [
        parser.AliasStmt(tile_no="3", symbolic_name="myTile"),
        parser.AssignOp("inbox", "emp"),
        parser.AssignOp("emp", "myTile"),
        parser.AddOp(parser.AddressOf("myTile"))
    ]
    assert get_assembly(code) == clean_output("""
    inbox
    copyto 3
    add [3]
    """)


def test_add_undefined_alias():
    code = [parser.AddOp("myTile")]
    with pytest.raises(ValueError):
        get_assembly(code)

def test_add_undefined_addressOfAlias():
    code = [parser.AddOp(parser.AddressOf("myTile"))]
    with pytest.raises(ValueError):
        get_assembly(code)

################ sub ######################

def test_sub_tilenumber():
    code = [parser.SubOp("3")]
    assert get_assembly(code) == ["sub 3"]

def test_sub_addressed_tilenumber():
    code = [parser.SubOp(parser.AddressOf("3"))]
    assert get_assembly(code) == ["sub [3]"]

def test_sub_tilealias():
    code = [
        parser.AliasStmt("5", "myTile"),
        parser.SubOp("myTile")
    ]
    assert get_assembly(code) == clean_output("""
    sub 5
    """)

def test_sub_addressed_tilealias():
    code = [
        parser.AliasStmt("5", "myTile"),
        parser.SubOp(parser.AddressOf("myTile"))
    ]
    assert get_assembly(code) == clean_output("""
    sub [5]
    """)

