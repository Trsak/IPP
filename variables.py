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
        frame, name = var[1].split("@")

        if frame == "GF":
            variable = self.frames.get_from_global_grame(name)

        if symb[0] == "string":
            variable.variable_type = TYPE_STRING
            variable.value = symb[1]

    def print_var(self, symb):
        if symb[0] == "var":
            frame, name = symb[1].split("@")
            if frame == "GF":
                variable = self.frames.get_from_global_grame(name)
                print(variable.value)




class Variable:
    def __init__(self, name):
        self.name = name
        self.variable_type = TYPE_NONE
        self.value = None
