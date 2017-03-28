# -*- coding: utf-8 -*-

# ################################
import hrmcompiler.parser as p
import hrmcompiler.assembler as a
import hrmcompiler.semantic_check as checker
import hrmcompiler.conversion as conversion
from pprint import pprint

def main(args):
    with open(args.fname) as src:
        result_ast = p.parse_it(src)

        checker.perform_label_checks(result_ast)

        result_ast = conversion.convert_ifnz_to_ifez(result_ast)
        result_ast = conversion.convert_iftojump(result_ast)


        print("if2jump")
        pprint(result_ast)
        print("minimize_labels")
        pprint(conversion.minimize_labels(result_ast))

        assembler = a.Assembler()
        assembler.convert(result_ast)

        print(" ------------------------ ")
        print("\n".join(assembler.code))

