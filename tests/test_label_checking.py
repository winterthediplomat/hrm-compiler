import pytest
from hrmcompiler import parser
from hrmcompiler import semantic_check
from io import StringIO

def test_singlelabel():
    code = """
    test:
    jmp test
    """
    with StringIO(code) as f:
        ast = parser.parse_it(f)

    assert semantic_check.check_multiple_labels(ast)
    assert semantic_check.check_undefined_label_jump(ast)

def test_double_defined_label():
    code = """
    test:
    test:
    jmp test
    """
    with StringIO(code) as f:
        ast = parser.parse_it(f)

        with pytest.raises(ValueError):
            semantic_check.check_multiple_labels(ast)

        assert semantic_check.check_undefined_label_jump(ast)

def test_jump_to_undefined_label():
    code = """
    notwhatyouwant:
    jmp whatiwant
    """
    with StringIO(code) as f:
        ast = parser.parse_it(f)
        with pytest.raises(ValueError):
            semantic_check.check_undefined_label_jump(ast)

def test_jump_to_undefined_label_condjmp():
    code = """
    notwhatyouwant:
    jez whatiwant
    """
    with StringIO(code) as f:
        ast = parser.parse_it(f)
        with pytest.raises(ValueError):
            semantic_check.check_undefined_label_jump(ast)
