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

def _check_variable(var_name, aliased_vars, wrong_variables):
    if type(var_name) == parser.AddressOf:
        var_name = var_name.addressee

    if var_name not in aliased_vars:
        try:
            _ = int(var_name)
        except ValueError:
            wrong_variables.append(var_name)

def perform_variable_checks(program_ast, aliased_vars=None, wrong_variables=None):
    if not aliased_vars:
        aliased_vars = ["emp", "inbox"]
        wrong_variables = []

    for ast_item in program_ast:
        if type(ast_item) == parser.IfOp:
            perform_variable_checks(ast_item.true_branch, aliased_vars, wrong_variables)
            perform_variable_checks(ast_item.false_branch, aliased_vars, wrong_variables)
        elif type(ast_item) == parser.AliasStmt:
            aliased_vars.append(ast_item.symbolic_name)
        elif type(ast_item) in [parser.LabelStmt, parser.OutboxOp, parser.JumpOp, parser.JumpCondOp]:
            pass
        elif type(ast_item) == parser.AssignOp:
            _check_variable(ast_item.src, aliased_vars, wrong_variables)
            _check_variable(ast_item.dst, aliased_vars, wrong_variables)
        elif type(ast_item) == parser.AddOp:
            _check_variable(ast_item.addend, aliased_vars, wrong_variables)
        elif type(ast_item) == parser.SubOp:
            _check_variable(ast_item.subtraend, aliased_vars, wrong_variables)
        elif type(ast_item) in [parser.IncrOp, parser.DecrOp]:
            _check_variable(ast_item.label_name, aliased_vars, wrong_variables)
        else:
            print("[warning][perform_variable_checks] found an unhandled type: ", ast_item, ". continuing")

    if wrong_variables:
        print("These variables are not aliased. Please check if they're typos or you forgot to delete them after a refactoring")
        for wrong_var in wrong_variables:
            print(wrong_var)
        raise ValueError("one or more variables are spelled wrong: check the output before to know the affected variables")
    else:
        return True
