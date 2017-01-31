# -*- coding: utf-8 -*-

from argparse import ArgumentParser

# ################################
import parser as p
import assembler as a

def main(args):
    with open(args.fname) as src:
        p.program.parseFile(src, parseAll=True)
        #print(p.bcc.bytecode_list)

        assembler = a.Assembler()
        assembler.convert(p.bcc.bytecode_list)

        print(" ------------------------ ")
        print("\n".join(assembler.code))

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("fname")

    main(parser.parse_args())
