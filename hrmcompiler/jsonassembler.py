# -*- coding: utf-8 -*-
import hrmcompiler.parser as p
from hrmcompiler.assembler import Assembler as HRMAssembler

class Assembler(object):
    def __init__(self):
        self.code = []
        self.aliases = dict()
        self._gen_label_cnt = 1

    def _convert_operand(self, operand):
        if operand.startswith("["):
            return {"Address": int(operand.replace("[", "").replace("]", ""))}
        elif operand.isdigit():
            return {"Cell": int(operand.replace("[", "").replace("]", ""))}
        else:
            return {"Label": operand}


    def _jsonize(self, command):
        try:
            operation, operand = command.split(" ")
            return {"operation": operation, "operand": self._convert_operand(operand)}
        except ValueError:
            if command.endswith(":"):
                return {"operation": "label", "operand": {"Label": command.replace(":", "")}}
            else:
                return {"operation": command}

    def convert(self, bytecodeList):
        internal_assembler = HRMAssembler()
        internal_assembler.convert(bytecodeList)

        self.code = [self._jsonize(command) for command in internal_assembler.code]
