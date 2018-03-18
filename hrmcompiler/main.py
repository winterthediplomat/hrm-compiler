# -*- coding: utf-8 -*-

# ################################
import hrmcompiler.parser as p
import hrmcompiler.assembler as a
import hrmcompiler.jsonassembler as ja
import hrmcompiler.semantic_check as checker
import hrmcompiler.conversion as conversion
from pprint import pprint
import json

def main(args):
    with open(args.fname) as src:
        result_ast = p.parse_it(src)

        checker.perform_label_checks(result_ast)
        checker.perform_variable_checks(result_ast)

        result_ast = conversion.convert_ifnz_to_ifez(result_ast)
        result_ast = conversion.convert_iftojump(result_ast)
        if not args.no_jump_compression:
            result_ast = conversion.compress_jumps(result_ast)
        if not args.no_unreachable:
            result_ast = conversion.remove_unreachable_code(result_ast)
        if not args.no_jmp_then_label:
            result_ast = conversion.fix_jmp_then_label(result_ast)

        assembler = a.Assembler()
        assembler.convert(result_ast)

        with open(args.fname.replace(".hrm", ".json"), "w") as dst:
            json_assembler = ja.Assembler()
            json_assembler.convert(result_ast)
            json.dump(json_assembler.code, dst)

        print(" ------------------------ ")
        print("\n".join(assembler.code))

