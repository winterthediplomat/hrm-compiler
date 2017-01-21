from pyparsing import Word, alphanums, nums, ZeroOrMore, Group, Keyword
from collections import namedtuple

assign = Group(Word(alphanums) + "=" + Word(alphanums))
alias = Group(Keyword("alias") + Word(nums) + Word(alphanums))
add = Group(Word("emp") + "+=" + Word(alphanums))
outbox = Keyword("outbox")
label = Group(Word(alphanums) + ":")
jump = Group(Keyword("jmp") + Word(alphanums))
program_line = (assign | alias | add | outbox | label | jump)
program = ZeroOrMore(program_line)

AssignOp = namedtuple("AssignOp", ["src", "dst"])
AliasStmt = namedtuple("AliasStmt", ["tile_no", "symbolic_name"])
AddOp = namedtuple("AddOp", ["addend"])
OutboxOp = namedtuple("OutboxOp", [])
LabelStmt = namedtuple("LabelStmt", ["label_name"])
JumpOp = namedtuple("JumpOp", ["label_name"])


class BytecodeConverter(object):
    def __init__(self):
        self.bytecode_list = list()
        self.aliases = dict()
        self.labels = list()

    def add_tokenized(self, tokensType, parseActionInfo):
        string_, line, tokens = parseActionInfo
        {
                "assign": self.add_assign,
                "alias": self.add_alias,
                "add": self.add_addop,
                "outbox": self.add_outbox,
                "label": self.add_label,
                "jump": self.add_jump
        }[tokensType](string_, line, tokens)
        return None

    def add_assign(self, string_, line, tokens):
        src, dst = tokens[2], tokens[0]

        if dst == "inbox": raise ValueError("Cannot assign to `inbox`!")
        if src == "outbox": raise ValueError("Cannot read from `outbox`!")

        self.bytecode_list.append(AssignOp(src, dst))

    def add_alias(self, string_, line, tokens):
        tile_no, sym_name = tokens[1], tokens[2]

        try:
            tile_no = int(tile_no)
        except TypeError:
            raise ValueError("usage: `alias <tile_number> <symbolic_name>`")

        self.aliases[sym_name] = tile_no
        self.bytecode_list.append(AliasStmt(tile_no, sym_name))

    def add_addop(self, string_, line, tokens):
        addend = tokens[2]

        self.bytecode_list.append(AddOp(addend))

    def add_outbox(self, string_, line, tokens):
        self.bytecode_list.append(OutboxOp())

    def add_label(self, string_, line, tokens):
        self.labels.append(tokens[0])
        self.bytecode_list.append(LabelStmt(tokens[0]))

    def add_jump(self, string_, line, tokens):
        self.bytecode_list.append(JumpOp(tokens[1]))

bcc = BytecodeConverter()

assign.setParseAction(lambda s, line, tokens: bcc.add_tokenized("assign", (s, line, tokens[0])))
alias.setParseAction(lambda s, line, tokens: bcc.add_tokenized("alias", (s, line, tokens[0])))
add.setParseAction(lambda s, line, tokens: bcc.add_tokenized("add", (s, line, tokens[0])))
outbox.setParseAction(lambda s, line, tokens: bcc.add_tokenized("outbox", (s, line, tokens[0])))
label.setParseAction(lambda s, line, tokens: bcc.add_tokenized("label", (s, line, tokens[0])))
jump.setParseAction(lambda s, line, tokens: bcc.add_tokenized("jump", (s, line, tokens[0])))
