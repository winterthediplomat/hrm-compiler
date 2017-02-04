# -*- coding: utf-8 -*-

# ################################
import hrmcompiler.parser as p
import hrmcompiler.assembler as a
import hrmcompiler.semantic_check as checker

def main(args):
    with open(args.fname) as src:
        #p.program.parseFile(src, parseAll=True)
        #print(p.bcc.bytecode_list)
        result_ast = p.parse_it(src)
        print(result_ast)

        checker.perform_label_checks(result_ast)

        assembler = a.Assembler()
        assembler.convert(result_ast)

        print(" ------------------------ ")
        print("\n".join(assembler.code))

