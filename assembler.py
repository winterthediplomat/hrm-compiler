# -*- coding: utf-8 -*-
import parser as p

class Assembler(object):
    def __init__(self):
        self.code = []
        self.aliases = dict()

    def convert_alias(self, aliasObj):
        self.aliases[aliasObj.symbolic_name] = aliasObj.tile_no

    def convert_assign(self, assignObj):
        print(assignObj)
        if assignObj.src == "emp":
            # copyto
            destination_tile = -1

            if assignObj.dst in self.aliases:
                destination_tile = self.aliases[assignObj.dst]
            else:
                try:
                    destination_tile = int(assignObj.dst)
                except TypeError:
                    raise ValueError("the given tile ({0}) is not an alias nor an int!".format(assignObj.dst))

            self.code.append("copyto {0}".format(destination_tile))

        if assignObj.dst == "emp":
            if assignObj.src == "inbox":
                self.code.append("inbox")
            else:
                raise NotImplementedError("`copyfrom` is not implemented yet!")


    def convert_outbox(self, outboxObj):
        self.code.append("outbox")

    def convert(self, bytecodeList):
        for bytecode in bytecodeList:
            typeToFunMapping = {
                p.AliasStmt: self.convert_alias,
                p.AssignOp: self.convert_assign,
                p.OutboxOp: self.convert_outbox
            }

            try:
                typeToFunMapping[type(bytecode)](bytecode)
            except KeyError:
                print("could not convert `{0}`".format(bytecode))
