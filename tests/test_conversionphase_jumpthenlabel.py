import pytest
from hrmcompiler import parser as p
from hrmcompiler import conversion

def test_convert_jmpthenlabel_check():
    code = [
        p.LabelStmt("alreadySorted"),
        p.AssignOp(src="inbox", dst="emp"),
        p.IfOp("neg", [p.JumpOp("alreadySorted")], []),
        p.IfOp("ez", [p.JumpOp("alreadySorted")], [p.AssignOp(src="0", dst="emp")])
    ]
    expected_ast = [
        p.LabelStmt("alreadySorted"),
        p.AssignOp(src="inbox", dst="emp"),
        p.JumpCondOp(condition="jneg", label_name="alreadySorted"),
            # pass
        #    p.JumpOp("_hrm_endif_1"),
        # p.LabelStmt("_hrm_endif_1"),
        p.JumpCondOp(condition="jez", label_name="alreadySorted"),
            p.AssignOp(src="0", dst="emp")
        #    p.JumpOp("_hrm_unreachable"),
        # p.LabelStmt("_hrm_unreachable")
    ]
    result_ast = conversion.convert_ifnz_to_ifez(code)
    result_ast = conversion.convert_iftojump(result_ast)
    result_ast = conversion.compress_jumps(result_ast)
    result_ast = conversion.remove_unreachable_code(result_ast)

    ast = conversion.fix_jmp_then_label(result_ast)

    assert ast == expected_ast

def test_convert_jmpthenlabel_conditionaljumps_leading_to_same_instr():
    start_ast = [
        p.JumpCondOp(condition="ez", label_name="output"),
        p.LabelStmt("output"),
        p.OutboxOp()
    ]
    expected_ast = [
        p.OutboxOp()
    ]
    ast = conversion.fix_jmp_then_label(start_ast)
    assert ast == expected_ast

def test_convert_jmpthenlabel_conditionaljumps_multiple():
    start_ast = [
        p.JumpCondOp(condition="jneg", label_name="other"),
        p.JumpCondOp(condition="jez", label_name="output"),
        p.LabelStmt("output"),
        p.OutboxOp(),
        p.LabelStmt("other"),
        p.AssignOp(src="inbox", dst="emp")
    ]
    expected_ast = [
        p.JumpCondOp(condition="jneg", label_name="other"),
        p.OutboxOp(),
        p.LabelStmt("other"),
        p.AssignOp(src="inbox", dst="emp")
    ]
    ast = conversion.fix_jmp_then_label(start_ast)

    assert ast == expected_ast

def test_convert_jmpthenlabel_not_remove_everything():
    code = [p.JumpOp("b"), p.LabelStmt("a")]
    code_ = [p.JumpOp("b"), p.LabelStmt("a"), p.OutboxOp()]

    assert code == conversion.fix_jmp_then_label(code)
    assert code_ == conversion.fix_jmp_then_label(code_)

def test_convert_jmpthenlabel_used_elsewhere():
    start_ast = [
            p.JumpOp(label_name="start"),
            p.LabelStmt("start"),
            p.AssignOp(src="inbox", dst="emp"),
            p.JumpOp("start")
    ]
    expected_ast = [
            p.LabelStmt("start"),
            p.AssignOp(src="inbox", dst="emp"),
            p.JumpOp("start")
    ]
    ast = conversion.fix_jmp_then_label(start_ast)
    assert ast == expected_ast
