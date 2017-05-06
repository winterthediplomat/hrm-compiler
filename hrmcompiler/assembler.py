# -*- coding: utf-8 -*-
import hrmcompiler.parser as p

class Assembler(object):
    def __init__(self):
        self.code = []
        self.aliases = dict()
        self._gen_label_cnt = 1

    def convert_alias(self, aliasObj):
        self.aliases[aliasObj.symbolic_name] = aliasObj.tile_no

    def convert_assign(self, assignObj):
        if(assignObj.src != "emp" and assignObj.dst != "emp"):
            raise ValueError("This assigment does not copy from or to `emp`:", assignObj)

        if assignObj.src == "emp":
            # copyto
            destination_tile = self._alias_to_tile(assignObj.dst)
            self.code.append("copyto {0}".format(destination_tile))

        if assignObj.dst == "emp":
            if assignObj.src == "inbox":
                self.code.append("inbox")
            else:
                self._handle_copyfrom(assignObj)

    def _handle_copyfrom(self, assignObj):
        source_tile = self._alias_to_tile(assignObj.src)
        self.code.append("copyfrom {0}".format(source_tile))

    def convert_add(self, addObj):
        tile_to_add = self._alias_to_tile(addObj.addend)
        self.code.append("add {0}".format(tile_to_add))

    def convert_sub(self, subObj):
        tile_to_sub = self._alias_to_tile(subObj.subtraend)
        self.code.append("sub {0}".format(tile_to_sub))

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

    def _alias_to_tile(self, candidate_alias):
        if type(candidate_alias) == p.AddressOf:
            is_address = True
            candidate_alias = candidate_alias.addressee
        else:
            is_address = False

        if candidate_alias in self.aliases:
            tile_no = self.aliases[candidate_alias]
        else:
            try:
                tile_no = int(candidate_alias)
            except TypeError:
                raise ValueError("the given tile is not an alias, an address nor an int!", candidate_alias)

        if is_address:
            return "[{0}]".format(tile_no)
        else:
            return tile_no


    def convert_incrop(self, incrObj):
        tile = self._alias_to_tile(incrObj.label_name)
        self.code.append("bump+ {tile}".format(tile=tile))

    def convert_decrop(self, decrObj):
        tile = self._alias_to_tile(decrObj.label_name)
        self.code.append("bump- {tile}".format(tile=tile))

    def convert_if(self, ifObj):
        def create_adhoc_assembler():
            new_assembler = Assembler()
            new_assembler.aliases = self.aliases
            new_assembler._gen_label_cnt = self._gen_label_cnt
            return new_assembler

        label_cnt = self._gen_label_cnt
        self._gen_label_cnt += 1

        true_branch_assembler = create_adhoc_assembler()
        true_branch_assembler.convert(ifObj.true_branch)
        self._gen_label_cnt = true_branch_assembler._gen_label_cnt

        false_branch_assembler = create_adhoc_assembler()
        false_branch_assembler.convert(ifObj.false_branch)
        self._gen_label_cnt = false_branch_assembler._gen_label_cnt

        self.convert_condjump(p.JumpCondOp("_hrm_"+str(label_cnt), "j"+ifObj.condition))
        for false_branch_codeline in false_branch_assembler.code:
            self.code.append(false_branch_codeline)
        self.convert_jump(p.JumpOp("_hrm_endif_"+str(label_cnt)))
        self.convert_label(p.LabelStmt("_hrm_"+str(label_cnt)))
        for true_branch_codeline in true_branch_assembler.code:
            self.code.append(true_branch_codeline)
        self.convert_label(p.LabelStmt("_hrm_endif_"+str(label_cnt)))

    def convert(self, bytecodeList):
        for bytecode in bytecodeList:
            typeToFunMapping = {
                p.AliasStmt: self.convert_alias,
                p.AssignOp: self.convert_assign,
                p.OutboxOp: self.convert_outbox,
                p.AddOp: self.convert_add,
                p.SubOp: self.convert_sub,
                p.LabelStmt: self.convert_label,
                p.JumpOp: self.convert_jump,
                p.JumpCondOp: self.convert_condjump,
                p.IncrOp: self.convert_incrop,
                p.DecrOp: self.convert_decrop,
                p.IfOp: self.convert_if
            }

            try:
                typeToFunMapping[type(bytecode)](bytecode)
            except KeyError:
                print("could not convert `{0}`".format(bytecode))
