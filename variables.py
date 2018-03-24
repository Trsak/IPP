import sys

TYPE_NONE = 0
TYPE_INT = 1
TYPE_BOOL = 2
TYPE_STRING = 3
TYPE_FLOAT = 4


class VariablesFactory:
    def __init__(self, frames):
        self.frames = frames

    def def_var(self, var):
        frame, name = var[1].split("@")
        new_variable = Variable(name)

        if frame == "GF":
            self.frames.add_to_global_frame(new_variable)

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

    def get_var(self, var):
        frame, name = var[1].split("@")

        if frame == "GF":
            return self.frames.get_from_global_grame(name)

    def print_var(self, symb, debug=False):
        if symb[0] == "var":
            variable = self.get_var(symb)

        if debug:
            sys.stderr.write(variable.value)
        else:
            print(variable.value)

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


class Variable:
    def __init__(self, name):
        self.name = name
        self.variable_type = TYPE_NONE
        self.value = None
