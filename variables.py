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
            symb_var = self.get_var(symb, True)
            variable.value = symb_var.value
            variable.variable_type = symb_var.variable_type

    def get_var(self, var, check_if_initialized=False):
        if var == "stack":
            return Variable("stack")

        frame, name = var[1].split("@")

        variable = None

        if frame == "GF":
            variable = self.frames.get_from_global_frame(name)
        elif frame == "TF":
            variable = self.frames.get_from_temporary_frame(name)
        elif frame == "LF":
            variable = self.frames.get_from_local_frame(name)

        if variable.variable_type == TYPE_NONE and check_if_initialized:
            sys.stderr.write("ERROR: %s is not initialized!\n" % var[1])
            exit(56)

        return variable

    def print_var(self, symb, debug=False):
        if symb[0] == "var":
            variable = self.get_var(symb, True)
            data_type = variable.variable_type
            value = variable.value
        else:
            data_type, value = self.get_symbol_type_and_value(symb)

        if data_type == TYPE_FLOAT:
            value = float.hex(value)

        if value is None:
            sys.stderr.write("ERROR: %s does not have value!\n" % symb[1])
            exit(56)

        if debug:
            sys.stderr.write(value)
        else:
            print(value)

    def aritmetic_operation(self, var, symb1, symb2, operation):
        if var is None and symb1 is None and symb2 is None:
            variable = self.get_var("stack")
            symb2_type, symb2_value = self.pop_data_stack()
            symb1_type, symb1_value = self.pop_data_stack()
        else:
            variable = self.get_var(var)
            symb1_type, symb1_value = self.get_symbol_type_and_value(symb1)
            symb2_type, symb2_value = self.get_symbol_type_and_value(symb2)

        if symb1_type != TYPE_FLOAT and symb1_type != TYPE_INT:
            sys.stderr.write("ERROR: Aritmetic instructions requires two float or int types!\n")
            self.wrong_operands_exit(symb1, symb2, types=[TYPE_FLOAT, TYPE_INT])
        elif operation == "idiv" and symb1_type != TYPE_INT:
            sys.stderr.write("ERROR: IDIV instruction requires two int types!\n")
            self.wrong_operands_exit(symb1, symb2, types=[TYPE_INT])
        elif operation == "div" and symb1_type != TYPE_FLOAT:
            sys.stderr.write("ERROR: DIV instruction requires two float types!\n")
            self.wrong_operands_exit(symb1, symb2, types=[TYPE_FLOAT])
        elif symb1_type != symb2_type:
            sys.stderr.write("ERROR: Aritmetic instruction requires same types!\n")
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
        elif operation == "div":
            try:
                variable.value = symb1_value / symb2_value
            except ZeroDivisionError:
                sys.stderr.write("ERROR: IDIV division by zero!\n")
                exit(57)

        if var is None and symb1 is None and symb2 is None:
            self.data_stack.append([variable.variable_type, variable.value])

    def relation_operator(self, var, symb1, symb2, operator):
        if var is None and symb1 is None and symb2 is None:
            variable = self.get_var("stack")
            symb2_type, symb2_value = self.pop_data_stack()
            symb1_type, symb1_value = self.pop_data_stack()
        else:
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

        if var is None and symb1 is None and symb2 is None:
            self.data_stack.append([variable.variable_type, variable.value])

    def bool_operator(self, var, symb1, symb2, operator):
        if var is None and symb1 is None and symb2 is None:
            variable = self.get_var("stack")
            symb2_type, symb2_value = self.pop_data_stack()

            if operator == "not":
                symb1_type, symb1_value = symb2_type, symb2_value
            else:
                symb1_type, symb1_value = self.pop_data_stack()
        else:
            variable = self.get_var(var)
            symb1_type, symb1_value = self.get_symbol_type_and_value(symb1)
            symb2_type, symb2_value = self.get_symbol_type_and_value(symb2)

        if symb1_type != symb2_type or symb1_type != TYPE_BOOL:
            sys.stderr.write("ERROR: Bool instructions can only have two symbols with bool types!\n")
            self.wrong_operands_exit(symb1, symb2, types=[TYPE_BOOL])

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

        if var is None and symb1 is None and symb2 is None:
            self.data_stack.append([variable.variable_type, variable.value])

    def get_symbol_type_and_value(self, symb, check_if_initialized=True):
        if symb[0] == "var":
            var = self.get_var(symb, check_if_initialized)

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
        symb_type, symb_value = self.get_symbol_type_and_value(symb, False)

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
        if var is None and symb is None:
            variable = self.get_var("stack")
            symb_type, symb_value = self.pop_data_stack()
        else:
            variable = self.get_var(var)
            symb_type, symb_value = self.get_symbol_type_and_value(symb)

        if symb_type != TYPE_INT:
            sys.stderr.write("ERROR: INT2CHAR requires symbol with int type!\n")
            self.wrong_operands_exit(symb, types=[TYPE_INT])

        variable.variable_type = TYPE_STRING
        try:
            variable.value = chr(symb_value)
        except ValueError:
            sys.stderr.write("ERROR: INT2CHAR requires symbol with valid ordinary char value in UNICODE!\n")
            exit(58)

        if var is None and symb is None:
            self.data_stack.append([variable.variable_type, variable.value])

    def stri_to_int(self, var, symb1, symb2):
        if var is None and symb1 is None and symb2 is None:
            variable = self.get_var("stack")
            symb2_type, symb2_value = self.pop_data_stack()
            symb1_type, symb1_value = self.pop_data_stack()
        else:
            variable = self.get_var(var)
            symb1_type, symb1_value = self.get_symbol_type_and_value(symb1)
            symb2_type, symb2_value = self.get_symbol_type_and_value(symb2)

        if symb1_type != TYPE_STRING:
            sys.stderr.write("ERROR: STRI2INT must have first symbol with string type!\n")
            self.wrong_operands_exit(symb1, types=[TYPE_STRING])
        elif symb2_type != TYPE_INT:
            sys.stderr.write("ERROR: STRI2INT must have second symbol with int type!\n")
            self.wrong_operands_exit(symb2, types=[TYPE_INT])

        variable.variable_type = TYPE_INT
        try:
            variable.value = ord(symb1_value[symb2_value])
        except IndexError:
            sys.stderr.write("ERROR: STRI2INT string out of range!\n")
            exit(58)

        if var is None and symb1 is None and symb2 is None:
            self.data_stack.append([variable.variable_type, variable.value])

    def is_equal(self, symb1, symb2):
        if symb1 is None and symb2 is None:
            symb2_type, symb2_value = self.pop_data_stack()
            symb1_type, symb1_value = self.pop_data_stack()
        else:
            symb2_type, symb2_value = self.get_symbol_type_and_value(symb2)
            symb1_type, symb1_value = self.get_symbol_type_and_value(symb1)

        if symb1_type != symb2_type:
            sys.stderr.write("ERROR: Both symbols in JUMPIFEQ must be same type!\n")
            exit(53)

        return symb1_value == symb2_value

    def is_not_equal(self, symb1, symb2):
        if symb1 is None and symb2 is None:
            symb2_type, symb2_value = self.pop_data_stack()
            symb1_type, symb1_value = self.pop_data_stack()
        else:
            symb2_type, symb2_value = self.get_symbol_type_and_value(symb2)
            symb1_type, symb1_value = self.get_symbol_type_and_value(symb1)

        if symb1_type != symb2_type:
            sys.stderr.write("ERROR: Both symbols in JUMPIFNEQ must be same type!\n")
            exit(53)

        return symb1_value != symb2_value

    def clear_stack(self):
        self.data_stack = []

    def push_stack(self, symb):
        symb_type, symb_value = self.get_symbol_type_and_value(symb)
        self.data_stack.append([symb_type, symb_value])

    def pop_stack(self, var):
        variable = self.get_var(var)
        variable.variable_type, variable.value = self.pop_data_stack()

    def pop_data_stack(self):
        if len(self.data_stack) == 0:
            sys.stderr.write("ERROR: Data stack is empty!\n")
            exit(56)

        return self.data_stack.pop()

    def concat_strings(self, var, symb1, symb2):
        variable = self.get_var(var)
        symb1_type, symb1_value = self.get_symbol_type_and_value(symb1)
        symb2_type, symb2_value = self.get_symbol_type_and_value(symb2)

        if symb1_type != TYPE_STRING or symb2_type != TYPE_STRING:
            sys.stderr.write("ERROR: CONCAT needs two string symbols!\n")
            self.wrong_operands_exit(symb1, symb2, types=[TYPE_STRING])

        variable.variable_type = TYPE_STRING
        variable.value = symb1_value + symb2_value

    def len_string(self, var, symb):
        variable = self.get_var(var)
        symb_type, symb_value = self.get_symbol_type_and_value(symb)

        if symb_type != TYPE_STRING:
            sys.stderr.write("ERROR: STRLEN needs string symbol!\n")
            self.wrong_operands_exit(symb, types=[TYPE_STRING])

        variable.variable_type = TYPE_INT
        variable.value = len(symb_value)

    def get_char(self, var, symb1, symb2):
        variable = self.get_var(var)
        symb1_type, symb1_value = self.get_symbol_type_and_value(symb1)
        symb2_type, symb2_value = self.get_symbol_type_and_value(symb2)

        if symb1_type != TYPE_STRING:
            sys.stderr.write("ERROR: GETCHAR's first symbol must be string!\n")
            self.wrong_operands_exit(symb1, types=[TYPE_STRING])
        elif symb2_type != TYPE_INT:
            sys.stderr.write("ERROR: GETCHAR's second symbol must be int!\n")
            self.wrong_operands_exit(symb2, types=[TYPE_INT])

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

        if variable.variable_type != TYPE_STRING:
            sys.stderr.write("ERROR: SETCHAR needs string var!\n")
            exit(53)
        elif symb1_type != TYPE_INT:
            sys.stderr.write("ERROR: SETCHAR's first symbol must be int!\n")
            self.wrong_operands_exit(symb1, types=[TYPE_INT])
        elif symb2_type != TYPE_STRING:
            sys.stderr.write("ERROR: SETCHAR's second symbol must be string!\n")
            self.wrong_operands_exit(symb2, types=[TYPE_STRING])

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
                value = float.fromhex(value)
            except (ValueError, TypeError):
                value = float(0)
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

    def int_to_float(self, var, symb):
        variable = self.get_var(var)
        symb_type, symb_value = self.get_symbol_type_and_value(symb)

        if symb_type != TYPE_INT:
            sys.stderr.write("ERROR: INT2FLOAT requires symbol with int type!\n")
            self.wrong_operands_exit(symb, types=[TYPE_INT])

        variable.variable_type = TYPE_FLOAT
        variable.value = float(symb_value)

    def float_to_int(self, var, symb):
        variable = self.get_var(var)
        symb_type, symb_value = self.get_symbol_type_and_value(symb)

        if symb_type != TYPE_FLOAT:
            sys.stderr.write("ERROR: FLOAT2INT requires symbol with float type!\n")
            self.wrong_operands_exit(symb, types=[TYPE_FLOAT])

        variable.variable_type = TYPE_INT
        variable.value = int(symb_value)

    def wrong_operands_exit(self, *symbols, types=None):
        if types is None:
            types = []

        for symb in symbols:
            data_type, value = self.get_symbol_type_and_value(symb)
            if data_type not in types:
                if symb[0] == "var":
                    exit(53)
                else:
                    exit(52)


class Variable:
    def __init__(self, name):
        self.name = name
        self.variable_type = TYPE_NONE
        self.value = None
