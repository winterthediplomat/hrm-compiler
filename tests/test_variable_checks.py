import pytest
from hrmcompiler import parser
from hrmcompiler import semantic_check
from io import StringIO

def test_aliasedvar():
    code = """
    alias 0 tmp

    emp = tmp
    tmp = emp
    """
    with StringIO(code) as f:
        ast = parser.parse_it(f)

    assert semantic_check.perform_variable_checks(ast)


def test_position():
    code = """
    emp = 0
    0 = emp
    """
    with StringIO(code) as f:
        ast = parser.parse_it(f)

    assert semantic_check.perform_variable_checks(ast)

def test_unaliased():
    code_listings = [
            # AssignOf
            """unaliased = emp""",
            """emp = unaliased""",
            """*unaliased = emp""",
            """emp = *unaliased""",
            # AddOp, SubOp
            "emp += unaliased",
            "emp -= unaliased",
            "emp += *unaliased",
            "emp -= *unaliased",
            # IncrOp, DecrOp
            "incr unaliased",
            "decr unaliased",
            "incr *unaliased",
            "decr *unaliased"
    ]
    for code in code_listings:
        with StringIO(code) as f:
            ast = parser.parse_it(f)
        with pytest.raises(ValueError):
            assert semantic_check.perform_variable_checks(ast)


def test_aliasedvar_typo():
    code_listings = [
            # AssignOf
            """unaliased = emp""",
            """emp = unaliased""",
            """*unaliased = emp""",
            """emp = *unaliased""",
            # AddOp, SubOp
            "emp += unaliased",
            "emp -= unaliased",
            "emp += *unaliased",
            "emp -= *unaliased",
            # IncrOp, DecrOp
            "incr unaliased",
            "decr unaliased",
            "incr *unaliased",
            "decr *unaliased"
    ]
    for code in code_listings:
        code = "alias 0 aliased\n" + code
        with StringIO(code) as f:
            ast = parser.parse_it(f)
        with pytest.raises(ValueError):
            assert semantic_check.perform_variable_checks(ast)


def test_nested_aliasedvar():
    code = """
    alias 0 tmp

    if ez then
        emp = tmp
    endif
    """
    with StringIO(code) as f:
        ast = parser.parse_it(f)

    assert semantic_check.perform_variable_checks(ast)

def test_nested_aliasedvar_typo():
    code_listings = [
            """
            alias 0 test

            if ez then
                jneg woot
                if ez then
                    if ez then
                        emp = tes
                    endif
                endif
            endif
            """,
            """
            if ez then
                jneg woot
                if ez then
                    emp = *test
                endif
            endif
            """
    ]
    for code in code_listings:
        with StringIO(code) as f:
            ast = parser.parse_it(f)
        with pytest.raises(ValueError):
            assert semantic_check.perform_variable_checks(ast)

