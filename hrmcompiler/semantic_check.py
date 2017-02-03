import hrmcompiler.parser as parser

def check_multiple_labels(program_ast):
    ast_labels = (ast_item for ast_item in program_ast if type(ast_item) == parser.LabelStmt)
    label_names_set = set()
    
    for label in ast_labels:
        if label.label_name in label_names_set:
            raise ValueError("the label {0} is declared more than once!".format(label.label_name))

        label_names_set.add(label.label_name)
    return True
