# -*- coding: utf-8 -*-

# ################################
import hrmcompiler.parser as p
import hrmcompiler.assembler as a

def main(args):
    with open(args.fname) as src:
        #p.program.parseFile(src, parseAll=True)
        #print(p.bcc.bytecode_list)
        bcc = p.parse_it(src)
        print(bcc.bytecode_list)


        assembler = a.Assembler()
        assembler.convert(bcc.bytecode_list)

        print(" ------------------------ ")
        print("\n".join(assembler.code))

