from pyparsing import Word, alphanums, nums, ZeroOrMore, Group, Keyword, pythonStyleComment, Suppress, Optional
from pyparsing import Forward
from collections import namedtuple

addressof = (Suppress("*") + Group(Word(alphanums))) | (Suppress("[") + Group(Word(alphanums)) + Suppress("]"))
assign = Group((Word(alphanums) | addressof) + "=" + (Word(alphanums) | addressof))
alias = Group(Keyword("alias") + Word(nums) + Word(alphanums))
add = Group(Word("emp") + "+=" + (Word(alphanums) | addressof))
sub = Group(Word("emp") + "-=" + (Word(alphanums) | addressof))
outbox = Keyword("outbox")
label = Group(Word(alphanums) + ":")
jump = Group(Keyword("jmp") + Word(alphanums))
condjump = Group((Keyword("jez")|Keyword("jneg")) + Word(alphanums))
incr = Group(Suppress(Keyword("incr") | Keyword("bump+")) + (Word(alphanums) | addressof))
decr = Group(Suppress(Keyword("decr") | Keyword("bump-")) + (Word(alphanums) | addressof))
# compatibility layer
compat_inbox = Keyword("inbox")
compat_add = Group(Keyword("add") + (Word(alphanums) | addressof))
compat_sub = Group(Keyword("sub") + (Word(alphanums) | addressof))
compat_copyfrom = Group(Keyword("copyfrom") + (Word(alphanums) | addressof))
compat_copyto = Group(Keyword("copyto") + (Word(alphanums) | addressof))

program_line = Forward()
_program_line = (
          assign | alias | add | sub | outbox | label | jump | condjump | incr | decr
        | compat_inbox | compat_add | compat_sub | compat_copyfrom | compat_copyto
        | Suppress(pythonStyleComment) )

condition = (Keyword("ez") | Keyword("nz") | Keyword("neg"))
if_block = Group(Suppress(Keyword("if")) + condition + Suppress(Keyword("then"))
           + Group(ZeroOrMore(program_line))
           + Optional(Suppress(Keyword("else")) + Group(ZeroOrMore(program_line)))
           + Suppress(Keyword("endif")))

program_line << (if_block|_program_line)
program = ZeroOrMore(program_line)

AddressOf = namedtuple("AddressOf", ["addressee"])
AssignOp = namedtuple("AssignOp", ["src", "dst"])
AliasStmt = namedtuple("AliasStmt", ["tile_no", "symbolic_name"])
AddOp = namedtuple("AddOp", ["addend"])
SubOp = namedtuple("SubOp", ["subtraend"])
OutboxOp = namedtuple("OutboxOp", [])
LabelStmt = namedtuple("LabelStmt", ["label_name"])
JumpOp = namedtuple("JumpOp", ["label_name"])
JumpCondOp = namedtuple("JumpCondOp", ["label_name", "condition"])
IncrOp = namedtuple("IncrOp", ["label_name"])
DecrOp = namedtuple("DecrOp", ["label_name"])

IfOp = namedtuple("IfOp", ["condition", "true_branch", "false_branch"])

class BytecodeConverter(object):
    def __init__(self):
        self.bytecode_list = list()
        self.aliases = dict()
        self.labels = list()

    def add_tokenized(self, tokensType, parseActionInfo):
        string_, line, tokens = parseActionInfo
        return {
                "assign": self.add_assign,
                "alias": self.add_alias,
                "add": self.add_addop,
                "sub": self.add_subop,
                "outbox": self.add_outbox,
                "label": self.add_label,
                "jump": self.add_jump,
                "condjump": self.add_condjump,
                "incr": self.add_incr,
                "decr": self.add_decr,
                "if": self.add_if,
                "addressof": self.add_addressof,
                # compatibility layer
                "compat_inbox": self.add_inbox,
                "compat_add": self.add_compat_addop,
                "compat_sub": self.add_compat_subop,
                "compat_copyfrom": self.add_compat_copyfromop,
                "compat_copyto": self.add_compat_copytoop,
        }[tokensType](string_, line, tokens)

    def add_assign(self, string_, line, tokens):
        src, dst = tokens[2], tokens[0]

        if dst == "inbox": raise ValueError("Cannot assign to `inbox`!")
        if src == "outbox": raise ValueError("Cannot read from `outbox`!")

        return (AssignOp(src, dst))

    def add_alias(self, string_, line, tokens):
        tile_no, sym_name = tokens[1], tokens[2]

        try:
            tile_no = int(tile_no)
        except TypeError:
            raise ValueError("usage: `alias <tile_number> <symbolic_name>`")

        self.aliases[sym_name] = tile_no
        return (AliasStmt(tile_no, sym_name))

    def add_addop(self, string_, line, tokens):
        addend = tokens[2]

        return (AddOp(addend))

    def add_subop(self, string_, line, tokens):
        subtraend = tokens[2]
        return (SubOp(subtraend))

    def add_outbox(self, string_, line, tokens):
        return (OutboxOp())

    def add_label(self, string_, line, tokens):
        self.labels.append(tokens[0])
        return (LabelStmt(tokens[0]))

    def add_jump(self, string_, line, tokens):
        return (JumpOp(tokens[1]))

    def add_condjump(self, string_, line, tokens):
        return (JumpCondOp(tokens[1], tokens[0]))

    def add_incr(self, string_, line, tokens):
        return IncrOp(tokens[0])

    def add_decr(self, string_, line, tokens):
        return DecrOp(tokens[0])

    def add_if(self, string_, line, tokens):
        try:
            false_branch = list(tokens[2])
        except IndexError:
            false_branch = []
        return IfOp(tokens[0], list(tokens[1]), false_branch)

    def add_addressof(self, string_, line, tokens):
        return AddressOf(tokens[0])

    # compatibility layer

    def add_inbox(self, string_, line, tokens):
        return AssignOp(src="inbox", dst="emp")

    def add_compat_addop(self, string_, line, tokens):
        addend = tokens[1]
        if addend == "emp":
            raise ValueError("`emp` is not a valid tile identifier. syntax: `add <tile number|alias name|address to tile or alias>`")

        return AddOp(addend)

    def add_compat_subop(self, string_, line, tokens):
        subtraend = tokens[1]
        if subtraend == "emp":
            raise ValueError("`emp` is not a valid tile identifier. syntax: `add <tile number|alias name|address to tile or alias>`")

        return SubOp(subtraend)

    def add_compat_copyfromop(self, string_, line, tokens):
        from_ = tokens[1]
        if from_ == "emp":
            raise ValueError("`emp` is not a valid tile identifier. syntax: `copyfrom <tile number|alias name|address to tile or alias>`")

        return AssignOp(src=from_, dst="emp")

    def add_compat_copytoop(self, string_, line, tokens):
        to_ = tokens[1]
        if to_ == "emp":
            raise ValueError("`emp` is not a valid tile identifier. syntax: `copyto <tile number|alias name|address to tile or alias>`")

        return AssignOp(src="emp", dst=to_)


def parse_it(fileObj):
    bcc = BytecodeConverter()

    addressof.setParseAction(lambda s, line, tokens: bcc.add_tokenized("addressof", (s, line, tokens[0])))
    assign.setParseAction(lambda s, line, tokens: bcc.add_tokenized("assign", (s, line, tokens[0])))
    alias.setParseAction(lambda s, line, tokens: bcc.add_tokenized("alias", (s, line, tokens[0])))
    add.setParseAction(lambda s, line, tokens: bcc.add_tokenized("add", (s, line, tokens[0])))
    sub.setParseAction(lambda s, line, tokens: bcc.add_tokenized("sub", (s, line, tokens[0])))
    outbox.setParseAction(lambda s, line, tokens: bcc.add_tokenized("outbox", (s, line, tokens[0])))
    label.setParseAction(lambda s, line, tokens: bcc.add_tokenized("label", (s, line, tokens[0])))
    jump.setParseAction(lambda s, line, tokens: bcc.add_tokenized("jump", (s, line, tokens[0])))
    condjump.setParseAction(lambda s, line, tokens: bcc.add_tokenized("condjump", (s, line, tokens[0])))
    incr.setParseAction(lambda s, line, tokens: bcc.add_tokenized("incr", (s, line, tokens[0])))
    decr.setParseAction(lambda s, line, tokens: bcc.add_tokenized("decr", (s, line, tokens[0])))
    if_block.setParseAction(lambda s, line, tokens: bcc.add_tokenized("if", (s, line, tokens[0])))
    # compatibility layer
    compat_inbox.setParseAction(lambda s, line, tokens: bcc.add_tokenized("compat_inbox", (s, line, tokens[0])))
    compat_add.setParseAction(lambda s, line, tokens: bcc.add_tokenized("compat_add", (s, line, tokens[0])))
    compat_sub.setParseAction(lambda s, line, tokens: bcc.add_tokenized("compat_sub", (s, line, tokens[0])))
    compat_copyfrom.setParseAction(lambda s, line, tokens: bcc.add_tokenized("compat_copyfrom", (s, line, tokens[0])))
    compat_copyto.setParseAction(lambda s, line, tokens: bcc.add_tokenized("compat_copyto", (s, line, tokens[0])))

    return program.parseFile(fileObj, parseAll=True)
