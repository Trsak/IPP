import sys

TYPE_NONE = 0
TYPE_INT = 1
TYPE_BOOL = 2
TYPE_STRING = 3
TYPE_FLOAT = 4


class VariablesFactory:
    def __init__(self, frames):
        self.frames = frames
        self.data_stack = []

    def def_var(self, var):
        frame, name = var[1].split("@")
        new_variable = Variable(name)

        if frame == "GF":
            self.frames.add_to_global_frame(new_variable)
        elif frame == "TF":
            self.frames.add_to_temporary_frame(new_variable)
        elif frame == "LF":
            self.frames.add_to_local_frame(new_variable)

    def move_to_var(self, var, symb):
        variable = self.get_var(var)

        if symb[0] == "string":
            variable.variable_type = TYPE_STRING
            variable.value = symb[1]
        elif symb[0] == "int":
            variable.variable_type = TYPE_INT
            variable.value = symb[1]
        elif symb[0] == "float":
            variable.variable_type = TYPE_FLOAT
            variable.value = symb[1]
        elif symb[0] == "bool":
            variable.variable_type = TYPE_BOOL
            variable.value = symb[1]
        elif symb[0] == "var":
            symb_var = self.get_var(symb)
            variable.value = symb_var.value
            variable.variable_type = symb_var.variable_type

    def get_var(self, var):
        frame, name = var[1].split("@")

        if frame == "GF":
            return self.frames.get_from_global_frame(name)
        elif frame == "TF":
            return self.frames.get_from_temporary_frame(name)
        elif frame == "LF":
            return self.frames.get_from_local_frame(name)

    def print_var(self, symb, debug=False):
        if symb[0] == "var":
            variable = self.get_var(symb)
            value = variable.value
        else:
            symb_type, value = self.get_symbol_type_and_value(symb)

        if debug:
            sys.stderr.write(value)
        else:
            print(value)

    def aritmetic_operation(self, var, symb1, symb2, operation):
        variable = self.get_var(var)
        symb1_type, symb1_value = self.get_symbol_type_and_value(symb1)
        symb2_type, symb2_value = self.get_symbol_type_and_value(symb2)

        if symb1_type != symb2_type or (symb1_type != TYPE_FLOAT and symb1_type != TYPE_INT):
            sys.stderr.write("ERROR: Aritmetic instruction requires two float or int types!\n")
            exit(53)
        elif operation == "idiv" and symb1_type != TYPE_INT:
            sys.stderr.write("ERROR: IDIV instruction requires two int types!\n")
            exit(53)

        variable.variable_type = symb1_type
        if operation == "add":
            variable.value = symb1_value + symb2_value
        elif operation == "sub":
            variable.value = symb1_value - symb2_value
        elif operation == "mul":
            variable.value = symb1_value * symb2_value
        elif operation == "idiv":
            try:
                variable.value = symb1_value // symb2_value
            except ZeroDivisionError:
                sys.stderr.write("ERROR: IDIV division by zero!\n")
                exit(57)

    def relation_operator(self, var, symb1, symb2, operator):
        variable = self.get_var(var)
        symb1_type, symb1_value = self.get_symbol_type_and_value(symb1)
        symb2_type, symb2_value = self.get_symbol_type_and_value(symb2)

        if symb1_type != symb2_type:
            sys.stderr.write("ERROR: Both symbols must have same type for relation operators use!\n")
            exit(53)

        variable.variable_type = TYPE_BOOL
        if operator == "lt":
            variable.value = str(symb1_value < symb2_value).lower()
        elif operator == "gt":
            variable.value = str(symb1_value > symb2_value).lower()
        elif operator == "eq":
            variable.value = str(symb1_value == symb2_value).lower()

    def bool_operator(self, var, symb1, symb2, operator):
        variable = self.get_var(var)
        symb1_type, symb1_value = self.get_symbol_type_and_value(symb1)
        symb2_type, symb2_value = self.get_symbol_type_and_value(symb2)

        if symb1_type != symb2_type or symb1_type != TYPE_BOOL:
            sys.stderr.write("ERROR: Bool instructions can only have two symbols with bool types!\n")
            exit(53)

        if symb1_value == "true":
            symb1_actual = True
        else:
            symb1_actual = False

        if symb2_value == "true":
            symb2_actual = True
        else:
            symb2_actual = False

        variable.variable_type = TYPE_BOOL
        if operator == "and":
            variable.value = str(symb1_actual and symb2_actual).lower()
        elif operator == "or":
            variable.value = str(symb1_actual or symb2_actual).lower()
        elif operator == "not":
            variable.value = str(not symb1_actual).lower()

    def get_symbol_type_and_value(self, symb):
        if symb[0] == "var":
            var = self.get_var(symb)
            return var.variable_type, var.value
        elif symb[0] == "float":
            return TYPE_FLOAT, symb[1]
        elif symb[0] == "int":
            return TYPE_INT, symb[1]
        elif symb[0] == "bool":
            return TYPE_BOOL, symb[1]
        elif symb[0] == "string":
            return TYPE_STRING, symb[1]

    def get_type(self, var, symb):
        variable = self.get_var(var)
        symb_type, symb_value = self.get_symbol_type_and_value(symb)

        variable.variable_type = TYPE_STRING
        if symb_type == TYPE_STRING:
            variable.value = "string"
        elif symb_type == TYPE_INT:
            variable.value = "int"
        elif symb_type == TYPE_FLOAT:
            variable.value = "float"
        elif symb_type == TYPE_BOOL:
            variable.value = "bool"
        else:
            variable.value = ""

    def int_to_char(self, var, symb):
        variable = self.get_var(var)
        symb_type, symb_value = self.get_symbol_type_and_value(symb)

        if symb_type != TYPE_INT:
            sys.stderr.write("ERROR: INT2CHAR requires symbol with int type!\n")
            exit(53)

        variable.variable_type = TYPE_STRING
        try:
            variable.value = chr(symb_value)
        except ValueError:
            sys.stderr.write("ERROR: INT2CHAR requires symbol with valid ordinary char value in UNICODE!\n")
            exit(58)

    def stri_to_int(self, var, symb1, symb2):
        variable = self.get_var(var)
        symb1_type, symb1_value = self.get_symbol_type_and_value(symb1)
        symb2_type, symb2_value = self.get_symbol_type_and_value(symb2)

        if symb1_type != TYPE_STRING or symb2_type != TYPE_INT:
            sys.stderr.write(
                "ERROR: INT2CHAR must have first symbol with string type and second symbol with int type!\n")
            exit(53)

        variable.variable_type = TYPE_INT
        try:
            variable.value = ord(symb1_value[symb2_value])
        except IndexError:
            sys.stderr.write("ERROR: STRI2INT string out of range!\n")
            exit(58)

    def is_equal(self, symb1, symb2):
        symb1_type, symb1_value = self.get_symbol_type_and_value(symb1)
        symb2_type, symb2_value = self.get_symbol_type_and_value(symb2)

        if symb1_type != symb2_type:
            sys.stderr.write("ERROR: Both symbols in JUMPIFEQ must be same type!\n")
            exit(53)

        return symb1_value == symb2_value

    def is_not_equal(self, symb1, symb2):
        symb1_type, symb1_value = self.get_symbol_type_and_value(symb1)
        symb2_type, symb2_value = self.get_symbol_type_and_value(symb2)

        if symb1_type != symb2_type:
            sys.stderr.write("ERROR: Both symbols in JUMPIFNEQ must be same type!\n")
            exit(53)

        return symb1_value != symb2_value

    def push_stack(self, symb):
        symb_type, symb_value = self.get_symbol_type_and_value(symb)
        self.data_stack.append([symb_type, symb_value])

    def pop_stack(self, var):
        if len(self.data_stack) == 0:
            sys.stderr.write("ERROR: Data stack is empty!\n")
            exit(56)

        variable = self.get_var(var)
        variable.variable_type, variable.value = self.data_stack.pop()

    def concat_strings(self, var, symb1, symb2):
        variable = self.get_var(var)
        symb1_type, symb1_value = self.get_symbol_type_and_value(symb1)
        symb2_type, symb2_value = self.get_symbol_type_and_value(symb2)

        if symb1_type != TYPE_STRING or symb2_type != TYPE_STRING:
            sys.stderr.write("ERROR: CONCAT needs two string symbols!\n")
            exit(53)

        variable.variable_type = TYPE_STRING
        variable.value = symb1_value + symb2_value

    def len_string(self, var, symb):
        variable = self.get_var(var)
        symb_type, symb_value = self.get_symbol_type_and_value(symb)

        if symb_type != TYPE_STRING:
            sys.stderr.write("ERROR: STRLEN needs string symbol!\n")
            exit(53)

        variable.variable_type = TYPE_INT
        variable.value = len(symb_value)

    def get_char(self, var, symb1, symb2):
        variable = self.get_var(var)
        symb1_type, symb1_value = self.get_symbol_type_and_value(symb1)
        symb2_type, symb2_value = self.get_symbol_type_and_value(symb2)

        if symb1_type != TYPE_STRING or symb2_type != TYPE_INT:
            sys.stderr.write("ERROR: GETCHAR needs first string symbol and second int symbol!\n")
            exit(53)

        variable.variable_type = TYPE_STRING
        try:
            variable.value = symb1_value[symb2_value]
        except IndexError:
            sys.stderr.write("ERROR: GETCHAR string out of range!\n")
            exit(58)

    def set_char(self, var, symb1, symb2):
        variable = self.get_var(var)
        symb1_type, symb1_value = self.get_symbol_type_and_value(symb1)
        symb2_type, symb2_value = self.get_symbol_type_and_value(symb2)

        if variable.variable_type != TYPE_STRING or symb1_type != TYPE_INT or symb2_type != TYPE_STRING:
            sys.stderr.write("ERROR: SETCHAR needs string var, first int symbol and second string symbol!\n")
            exit(53)

        try:
            if symb1_value > (len(variable.value) - 1) or symb1_value < 0:
                raise IndexError

            variable.value = variable.value[:symb1_value] + symb2_value[0] + variable.value[symb1_value + 1:]
        except IndexError:
            sys.stderr.write("ERROR: SETCHAR string out of range!\n")
            exit(58)

    def read_var(self, var, var_type):
        var_type = var_type[1]
        try:
            value = input()
        except (EOFError, KeyboardInterrupt):
            value = None

        if var_type == "float":
            var_type = TYPE_FLOAT
            try:
                value = float(value)
            except (ValueError, TypeError):
                value = 0
        elif var_type == "int":
            var_type = TYPE_INT
            try:
                value = int(value)
            except (ValueError, TypeError):
                value = 0
        elif var_type == "bool":
            var_type = TYPE_BOOL
            if value is not None:
                value = value.lower()
            if value != "true" and value != "false":
                value = "false"
        elif var_type == "string":
            var_type = TYPE_STRING
            if value is None:
                value = ""

        variable = self.get_var(var)
        variable.variable_type = var_type
        variable.value = value


class Variable:
    def __init__(self, name):
        self.name = name
        self.variable_type = TYPE_NONE
        self.value = None
