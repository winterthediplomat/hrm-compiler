import hrmcompiler.parser as parser
from io import StringIO
import pyparsing
import pytest


#######################################################

def test_assign():
    code = "emp = inbox"
    with StringIO(code) as f:
        ast = parser.parse_it(f)

        assert ast[0].src == "inbox"
        assert ast[0].dst == "emp"


def test_assign_to_inbox():
    code = "inbox = emp"
    with StringIO(code) as f:
        with pytest.raises(ValueError):
            ast = parser.parse_it(f)

@pytest.mark.skip(reason="we may want this behavior in the future...")
def test_assign_to_outbox():
    code = "outbox = emp"
    with StringIO(code) as f:
        with pytest.raises(ValueError):
            ast = parser.parse_it(f)

def test_assign_from_outbox():
    code = "emp = outbox"
    with StringIO(code) as f:
        with pytest.raises(ValueError):
            ast = parser.parse_it(f)

def test_assign_to_alias():
    code = "myTile = emp"
    with StringIO(code) as f:
        ast = parser.parse_it(f)

    assert ast[0].src == "emp"
    assert ast[0].dst == "myTile"

def test_assign_to_tilenumber():
    code = "3 = emp"
    with StringIO(code) as f:
        ast = parser.parse_it(f)

    assert ast[0].src == "emp"
    assert ast[0].dst == "3"

def test_assign_from_alias():
    code = "emp = myTile"
    with StringIO(code) as f:
        ast = parser.parse_it(f)

    assert ast[0].src == "myTile"
    assert ast[0].dst == "emp"

def test_assign_from_tile():
    code = "emp = 3"
    with StringIO(code) as f:
        ast = parser.parse_it(f)

    assert ast[0].src == "3"
    assert ast[0].dst == "emp"

#######################################################

def test_aliases():
    code = "alias 5 test"
    with StringIO(code) as f:
        ast = parser.parse_it(f)

    assert ast[0].symbolic_name == "test"
    assert ast[0].tile_no == 5

def test_aliases_tileno_is_not_a_number():
    code = "alias kek 4"
    with StringIO(code) as f:
        with pytest.raises(pyparsing.ParseException):
            ast = parser.parse_it(f)

#######################################################

def test_add():
    code = "emp += test"
    with StringIO(code) as f:
        ast = parser.parse_it(f)

        assert ast[0].addend == "test"

def test_add_tilenumber():
    code = "emp += 3"
    with StringIO(code) as f:
        ast = parser.parse_it(f)

    assert ast[0].addend == "3"

def test_add_to_nonEmp():
    """ for now, you cannot add to something different than `emp` """
    code = "nonemp += test"
    with StringIO(code) as f:
        with pytest.raises(pyparsing.ParseException):
            ast = parser.parse_it(f)

def test_add_address_of_tile():
    code = "emp += *test"
    with StringIO(code) as f:
        ast = parser.parse_it(f)

    assert ast[0].addend == parser.AddressOf("test")

def test_add_address_of_number():
    code = "emp += *3"
    with StringIO(code) as f:
        ast = parser.parse_it(f)

    assert ast[0].addend == parser.AddressOf("3")

#######################################################

def test_sub():
    code = "emp -= test"
    with StringIO(code) as f:
        ast = parser.parse_it(f)

    assert ast[0].subtraend == "test"

def test_sub_from_nonEmp():
    """ for now, you cannot sub from something different than `emp` """
    code = "nonemp -= test"
    with StringIO(code) as f:
        with pytest.raises(pyparsing.ParseException):
            parser.parse_it(f)


#######################################################

def test_incr_withlabel():
    code = "incr mylabel"
    with StringIO(code) as f:
        ast = parser.parse_it(f)

    assert type(ast[0]) == parser.IncrOp
    assert ast[0].label_name == "mylabel"

def test_incr_withnumber():
    code = "incr 0"
    with StringIO(code) as f:
        ast = parser.parse_it(f)

    assert type(ast[0]) == parser.IncrOp
    assert ast[0].label_name == "0"

def test_decr_withlabel():
    code = "decr mylabel"
    with StringIO(code) as f:
        ast = parser.parse_it(f)

    assert type(ast[0]) == parser.DecrOp
    assert ast[0].label_name == "mylabel"

def test_decr_withnumber():
    code = "decr 0"
    with StringIO(code) as f:
        ast = parser.parse_it(f)

    assert type(ast[0]) == parser.DecrOp
    assert ast[0].label_name == "0"

