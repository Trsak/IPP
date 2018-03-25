import string

from frames import Frames
import re
from variables import *
from xml.sax.saxutils import unescape

FRAMES = ["GF", "TF", "LF"]

TYPES = ["bool", "int", "string", "float"]

INSTRUCTIONS = ["MOVE", "CREATEFRAME", "PUSHFRAME", "POPFRAME", "DEFVAR", "CALL", "RETURN", "PUSHS", "POPS", "ADD",
                "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR", "NOT", "INT2CHAR", "STRI2INT", "INT2FLOAT",
                "FLOAT2INT", "READ", "WRITE", "CONCAT", "STRLEN", "GETCHAR", "SETCHAR", "TYPE", "LABEL", "JUMP",
                "JUMPIFEQ", "JUMPIFNEQ", "DPRINT", "BREAK"]


class IPPcodeParseError(Exception):
    pass


class InterpretFactory:
    def __init__(self):
        self.instructions = []
        self.labels = []
        self.calls = []
        self.names_pattern = re.compile("[^A-ZÁ-Ža-zá-ž0-9\-\*\$%_&]")
        self.frames = Frames()
        self.variables_factory = VariablesFactory(self.frames)

    def add_instruction(self, opcode, args, position):
        if opcode not in INSTRUCTIONS:
            raise IPPcodeParseError("unknown instrustion %s" % opcode)

        try:
            if opcode == "MOVE":
                self.count_args(len(args), 2, opcode)
                self.var(args[0])
                self.symb(args[1])
            elif opcode == "CREATEFRAME":
                self.count_args(len(args), 0, opcode)
            elif opcode == "PUSHFRAME":
                self.count_args(len(args), 0, opcode)
            elif opcode == "POPFRAME":
                self.count_args(len(args), 0, opcode)
            elif opcode == "DEFVAR":
                self.count_args(len(args), 1, opcode)
                self.var(args[0])
            elif opcode == "CALL":
                self.count_args(len(args), 1, opcode)
                self.label(args[0])
            elif opcode == "RETURN":
                self.count_args(len(args), 0, opcode)
            elif opcode == "PUSHS":
                self.count_args(len(args), 1, opcode)
                self.symb(args[0])
            elif opcode == "POPS":
                self.count_args(len(args), 1, opcode)
                self.var(args[0])
            elif opcode == "ADD":
                self.count_args(len(args), 3, opcode)
                self.var(args[0])
                self.symb(args[1])
                self.symb(args[2])
            elif opcode == "SUB":
                self.count_args(len(args), 3, opcode)
                self.var(args[0])
                self.symb(args[1])
                self.symb(args[2])
            elif opcode == "MUL":
                self.count_args(len(args), 3, opcode)
                self.var(args[0])
                self.symb(args[1])
                self.symb(args[2])
            elif opcode == "IDIV":
                self.count_args(len(args), 3, opcode)
                self.var(args[0])
                self.symb(args[1])
                self.symb(args[2])
            elif opcode == "LT":
                self.count_args(len(args), 3, opcode)
                self.var(args[0])
                self.symb(args[1])
                self.symb(args[2])
            elif opcode == "GT":
                self.count_args(len(args), 3, opcode)
                self.var(args[0])
                self.symb(args[1])
                self.symb(args[2])
            elif opcode == "EQ":
                self.count_args(len(args), 3, opcode)
                self.var(args[0])
                self.symb(args[1])
                self.symb(args[2])
            elif opcode == "AND":
                self.count_args(len(args), 3, opcode)
                self.var(args[0])
                self.symb(args[1])
                self.symb(args[2])
            elif opcode == "OR":
                self.count_args(len(args), 3, opcode)
                self.var(args[0])
                self.symb(args[1])
                self.symb(args[2])
            elif opcode == "NOT":
                self.count_args(len(args), 2, opcode)
                self.var(args[0])
                self.symb(args[1])
            elif opcode == "INT2CHAR":
                self.count_args(len(args), 2, opcode)
                self.var(args[0])
                self.symb(args[1])
            elif opcode == "STRI2INT":
                self.count_args(len(args), 3, opcode)
                self.var(args[0])
                self.symb(args[1])
                self.symb(args[2])
            elif opcode == "INT2FLOAT":
                self.count_args(len(args), 2, opcode)
                self.var(args[0])
                self.symb(args[1])
            elif opcode == "FLOAT2INT":
                self.count_args(len(args), 2, opcode)
                self.var(args[0])
                self.symb(args[1])
            elif opcode == "READ":
                self.count_args(len(args), 2, opcode)
                self.var(args[0])
                self.type(args[1])
            elif opcode == "WRITE":
                self.count_args(len(args), 1, opcode)
                self.symb(args[0])
            elif opcode == "CONCAT":
                self.count_args(len(args), 3, opcode)
                self.var(args[0])
                self.symb(args[1])
                self.symb(args[2])
            elif opcode == "STRLEN":
                self.count_args(len(args), 2, opcode)
                self.var(args[0])
                self.symb(args[1])
            elif opcode == "GETCHAR":
                self.count_args(len(args), 3, opcode)
                self.var(args[0])
                self.symb(args[1])
                self.symb(args[2])
            elif opcode == "SETCHAR":
                self.count_args(len(args), 3, opcode)
                self.var(args[0])
                self.symb(args[1])
                self.symb(args[2])
            elif opcode == "TYPE":
                self.count_args(len(args), 2, opcode)
                self.var(args[0])
                self.symb(args[1])
            elif opcode == "LABEL":
                self.count_args(len(args), 1, opcode)
                self.label(args[0])
                self.add_label(args[0], position)
            elif opcode == "JUMP":
                self.count_args(len(args), 1, opcode)
                self.label(args[0])
            elif opcode == "JUMPIFEQ":
                self.count_args(len(args), 3, opcode)
                self.label(args[0])
                self.symb(args[1])
                self.symb(args[2])
            elif opcode == "JUMPIFNEQ":
                self.count_args(len(args), 3, opcode)
                self.label(args[0])
                self.symb(args[1])
                self.symb(args[2])
            elif opcode == "DPRINT":
                self.count_args(len(args), 1, opcode)
                self.symb(args[0])
            elif opcode == "BREAK":
                self.count_args(len(args), 0, opcode)

            self.instructions.append({"opcode": opcode, "args": args})
        except IndexError:
            raise IPPcodeParseError("missing arguments for %s instruction" % opcode)

    def run(self):
        inst_len = len(self.instructions)
        current_inst = 0
        total_inst = 0

        while current_inst < inst_len:
            if self.instructions[current_inst]["opcode"] == "DEFVAR":
                self.variables_factory.def_var(self.instructions[current_inst]["args"][0])
            elif self.instructions[current_inst]["opcode"] == "MOVE":
                self.variables_factory.move_to_var(self.instructions[current_inst]["args"][0],
                                                   self.instructions[current_inst]["args"][1])
            elif self.instructions[current_inst]["opcode"] == "CREATEFRAME":
                self.frames.temporary_frame = []
            elif self.instructions[current_inst]["opcode"] == "PUSHFRAME":
                self.frames.push_frame()
            elif self.instructions[current_inst]["opcode"] == "POPFRAME":
                self.frames.pop_frame()
            elif self.instructions[current_inst]["opcode"] == "CALL":
                self.calls.append(current_inst)
                current_inst = self.jump_to_label(self.instructions[current_inst]["args"][0]) - 1
            elif self.instructions[current_inst]["opcode"] == "RETURN":
                if len(self.calls) == 0:
                    sys.stderr.write("ERROR: CALL stack is empty!\n")
                    exit(55)
                current_inst = self.calls.pop()
            elif self.instructions[current_inst]["opcode"] == "PUSHS":
                self.variables_factory.push_stack(self.instructions[current_inst]["args"][0])
            elif self.instructions[current_inst]["opcode"] == "POPS":
                self.variables_factory.pop_stack(self.instructions[current_inst]["args"][0])
            elif self.instructions[current_inst]["opcode"] == "WRITE":
                self.variables_factory.print_var(self.instructions[current_inst]["args"][0])
            elif self.instructions[current_inst]["opcode"] == "DPRINT":
                self.variables_factory.print_var(self.instructions[current_inst]["args"][0], True)
            elif self.instructions[current_inst]["opcode"] == "ADD":
                self.variables_factory.aritmetic_operation(self.instructions[current_inst]["args"][0],
                                                           self.instructions[current_inst]["args"][1],
                                                           self.instructions[current_inst]["args"][2], "add")
            elif self.instructions[current_inst]["opcode"] == "SUB":
                self.variables_factory.aritmetic_operation(self.instructions[current_inst]["args"][0],
                                                           self.instructions[current_inst]["args"][1],
                                                           self.instructions[current_inst]["args"][2], "sub")
            elif self.instructions[current_inst]["opcode"] == "MUL":
                self.variables_factory.aritmetic_operation(self.instructions[current_inst]["args"][0],
                                                           self.instructions[current_inst]["args"][1],
                                                           self.instructions[current_inst]["args"][2], "mul")
            elif self.instructions[current_inst]["opcode"] == "IDIV":
                self.variables_factory.aritmetic_operation(self.instructions[current_inst]["args"][0],
                                                           self.instructions[current_inst]["args"][1],
                                                           self.instructions[current_inst]["args"][2], "idiv")
            elif self.instructions[current_inst]["opcode"] == "LT":
                self.variables_factory.relation_operator(self.instructions[current_inst]["args"][0],
                                                         self.instructions[current_inst]["args"][1],
                                                         self.instructions[current_inst]["args"][2], "lt")
            elif self.instructions[current_inst]["opcode"] == "GT":
                self.variables_factory.relation_operator(self.instructions[current_inst]["args"][0],
                                                         self.instructions[current_inst]["args"][1],
                                                         self.instructions[current_inst]["args"][2], "gt")
            elif self.instructions[current_inst]["opcode"] == "EQ":
                self.variables_factory.relation_operator(self.instructions[current_inst]["args"][0],
                                                         self.instructions[current_inst]["args"][1],
                                                         self.instructions[current_inst]["args"][2], "eq")
            elif self.instructions[current_inst]["opcode"] == "AND":
                self.variables_factory.bool_operator(self.instructions[current_inst]["args"][0],
                                                     self.instructions[current_inst]["args"][1],
                                                     self.instructions[current_inst]["args"][2], "and")
            elif self.instructions[current_inst]["opcode"] == "OR":
                self.variables_factory.bool_operator(self.instructions[current_inst]["args"][0],
                                                     self.instructions[current_inst]["args"][1],
                                                     self.instructions[current_inst]["args"][2], "or")
            elif self.instructions[current_inst]["opcode"] == "NOT":
                self.variables_factory.bool_operator(self.instructions[current_inst]["args"][0],
                                                     self.instructions[current_inst]["args"][1],
                                                     self.instructions[current_inst]["args"][1], "not")
            elif self.instructions[current_inst]["opcode"] == "INT2CHAR":
                self.variables_factory.int_to_char(self.instructions[current_inst]["args"][0],
                                                   self.instructions[current_inst]["args"][1])
            elif self.instructions[current_inst]["opcode"] == "STRI2INT":
                self.variables_factory.stri_to_int(self.instructions[current_inst]["args"][0],
                                                   self.instructions[current_inst]["args"][1],
                                                   self.instructions[current_inst]["args"][2])
            elif self.instructions[current_inst]["opcode"] == "TYPE":
                self.variables_factory.get_type(self.instructions[current_inst]["args"][0],
                                                self.instructions[current_inst]["args"][1])
            elif self.instructions[current_inst]["opcode"] == "JUMP":
                current_inst = self.jump_to_label(self.instructions[current_inst]["args"][0]) - 1
            elif self.instructions[current_inst]["opcode"] == "JUMPIFEQ":
                if (self.variables_factory.is_equal(self.instructions[current_inst]["args"][1],
                                                    self.instructions[current_inst]["args"][2])):
                    current_inst = self.jump_to_label(self.instructions[current_inst]["args"][0]) - 1
            elif self.instructions[current_inst]["opcode"] == "JUMPIFNEQ":
                if (self.variables_factory.is_not_equal(self.instructions[current_inst]["args"][1],
                                                        self.instructions[current_inst]["args"][2])):
                    current_inst = self.jump_to_label(self.instructions[current_inst]["args"][0]) - 1
            elif self.instructions[current_inst]["opcode"] == "CONCAT":
                self.variables_factory.concat_strings(self.instructions[current_inst]["args"][0],
                                                      self.instructions[current_inst]["args"][1],
                                                      self.instructions[current_inst]["args"][2])
            elif self.instructions[current_inst]["opcode"] == "STRLEN":
                self.variables_factory.len_string(self.instructions[current_inst]["args"][0],
                                                  self.instructions[current_inst]["args"][1])
            elif self.instructions[current_inst]["opcode"] == "GETCHAR":
                self.variables_factory.get_char(self.instructions[current_inst]["args"][0],
                                                self.instructions[current_inst]["args"][1],
                                                self.instructions[current_inst]["args"][2])
            elif self.instructions[current_inst]["opcode"] == "SETCHAR":
                self.variables_factory.set_char(self.instructions[current_inst]["args"][0],
                                                self.instructions[current_inst]["args"][1],
                                                self.instructions[current_inst]["args"][2])
            elif self.instructions[current_inst]["opcode"] == "READ":
                self.variables_factory.read_var(self.instructions[current_inst]["args"][0],
                                                self.instructions[current_inst]["args"][1])
            elif self.instructions[current_inst]["opcode"] == "BREAK":
                sys.stderr.write("--------- DEBUG INFO START ---------\n")
                sys.stderr.write("Instrictions interpreted: %d\n" % total_inst)
                sys.stderr.write("Current instruction number: %d\n" % int(current_inst + 1))
                sys.stderr.write("---------- DEBUG INFO END ----------\n")

            current_inst += 1
            total_inst += 1

    @staticmethod
    def count_args(actual, needed, opcode):
        if actual != needed:
            raise IPPcodeParseError("too many or missing arguments for %s instruction" % opcode)

    def var(self, arg):
        if arg[0] != "var":
            raise IPPcodeParseError("expected variable")

        frame, name = arg[1].split("@")
        if self.names_pattern.match(name) or name[0].isdigit():
            raise IPPcodeParseError("variable name has wrong format")

        if frame not in FRAMES:
            raise IPPcodeParseError("unknown frame")

    def symb(self, arg):
        if arg[0] == "var":
            self.var(arg)
        elif arg[0] == "bool":
            if arg[1] != "true" and arg[1] != "false":
                raise IPPcodeParseError("unknown bool value")
        elif arg[0] == "int":
            try:
                arg[1] = int(arg[1])
            except ValueError:
                raise IPPcodeParseError("wrong int literal")
        elif arg[0] == "float":
            try:
                # TODO: Hexa
                arg[1] = float(arg[1])
            except ValueError:
                raise IPPcodeParseError("wrong float literal")
        elif arg[0] == "string":
            if arg[1] is None:
                arg[1] = ""

            if " " in arg[1]:
                raise IPPcodeParseError("found whitespace in string literal")
            elif "#" in arg[1]:
                raise IPPcodeParseError("found # char in string literal")

            arg[1] = unescape(arg[1])

            i = 0
            for char in arg[1]:
                if char == "\\":
                    try:
                        xyz = int(arg[1][i + 1] + arg[1][i + 2] + arg[1][i + 3])
                        arg[1] = arg[1][:i] + chr(xyz) + arg[1][i + 4:]
                        i -= 3
                    except (ValueError, IndexError):
                        raise IPPcodeParseError("wrong string escape sequence")
                i += 1
        else:
            raise IPPcodeParseError("symbol can only be var, int, float, bool or string")

    def label(self, arg):
        if arg[0] != "label":
            raise IPPcodeParseError("expected label")

        if self.names_pattern.match(arg[1]):
            raise IPPcodeParseError("label name has wrong format")

    def type(self, arg):
        if arg[0] != "type":
            raise IPPcodeParseError("expected type")

        if arg[1] not in TYPES:
            raise IPPcodeParseError("unexpected type")

    def find_label(self, name):
        for label in self.labels:
            if label[0] == name:
                return label

        return None

    def add_label(self, arg, position):
        label = arg[1]

        if not self.find_label(label):
            self.labels.append([label, position])
        else:
            sys.stderr.write("ERROR: Label %s already exists!\n" % label)
            exit(52)

    def jump_to_label(self, arg):
        label = self.find_label(arg[1])

        if not label:
            sys.stderr.write("ERROR: Label %s not found!\n" % arg[1])
            exit(52)
        else:
            return label[1] - 1
