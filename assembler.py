# -*- coding: utf-8 -*-
import parser as p

class Assembler(object):
    def __init__(self):
        self.code = []
        self.aliases = dict()

    def convert_alias(self, aliasObj):
        self.aliases[aliasObj.symbolic_name] = aliasObj.tile_no

    def convert_assign(self, assignObj):
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

    def convert_add(self, addObj):
        tile_to_add = -1

        if addObj.addend in self.aliases:
            tile_to_add = self.aliases[addObj.addend]
        else:
            try:
                tile_to_add = int(addObj.addend)
            except TypeError:
                raise ValueError("the given tile is not an alias nor an int!", addObj)

        assert tile_to_add != -1
        self.code.append("add {0}".format(tile_to_add))

    def convert_outbox(self, outboxObj):
        self.code.append("outbox")

    def convert_label(self, labelObj):
        self.code.append("{0}:".format(labelObj.label_name))

    def convert_jump(self, jumpObj):
        self.code.append("jmp {0}".format(jumpObj.label_name))

    def convert_condjump(self, condjumpObj):
        self.code.append("{cond} {label}".format(
            cond=condjumpObj.condition,
            label=condjumpObj.label_name))

    def convert(self, bytecodeList):
        for bytecode in bytecodeList:
            typeToFunMapping = {
                p.AliasStmt: self.convert_alias,
                p.AssignOp: self.convert_assign,
                p.OutboxOp: self.convert_outbox,
                p.AddOp: self.convert_add,
                p.LabelStmt: self.convert_label,
                p.JumpOp: self.convert_jump,
                p.JumpCondOp: self.convert_condjump
            }

            try:
                typeToFunMapping[type(bytecode)](bytecode)
            except KeyError:
                print("could not convert `{0}`".format(bytecode))
