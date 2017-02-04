import hrmcompiler.parser as parser

def check_multiple_labels(program_ast):
    ast_labels = (ast_item for ast_item in program_ast if type(ast_item) == parser.LabelStmt)
    label_names_set = set()
    
    for label in ast_labels:
        if label.label_name in label_names_set:
            raise ValueError("the label {0} is declared more than once!".format(label.label_name))

        label_names_set.add(label.label_name)
    return True

def check_undefined_label_jump(program_ast):
    ast_labels = set(ast_item.label_name for ast_item in program_ast if type(ast_item) == parser.LabelStmt)
    jmp_labels = set(ast_item.label_name for ast_item in program_ast if type(ast_item) in [parser.JumpOp, parser.JumpCondOp])

    undefined_labels = jmp_labels.difference(ast_labels)
    if undefined_labels:
        raise ValueError("the following labels are referenced by `jmp` operations, but don't exist: {0}".format(list(undefined_labels)))

    return True

def perform_label_checks(program_ast):
    check_multiple_labels(program_ast)
    check_undefined_label_jump(program_ast)
