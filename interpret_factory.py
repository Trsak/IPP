INSTRUCTIONS = ["MOVE", "CREATEFRAME", "PUSHFRAME", "POPFRAME", "DEFVAR", "CALL", "RETURN", "PUSHS", "POPS", "ADD",
                "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR", "NOT", "INT2CHAR", "STRI2INT", "INT2FLOAT",
                "FLOAT2INT", "READ", "WRITE", "CONCAT", "STRLEN", "GETCHAR", "SETCHAR", "TYPE", "LABEL", "JUMP",
                "JUMPIFEQ", "JUMPIFNEQ", "DPRINT", "BREAK"]


class IPPcodeParseError(Exception):
    pass


class InterpretFactory:
    def __init__(self):
        self.instructions = []

    def add_instruction(self, opcode, args):
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
                self.count_args(len(args), 3, opcode)
                self.var(args[0])
                self.symb(args[1])
                self.symb(args[2])
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
        except IndexError:
            raise IPPcodeParseError("missing arguments for %s instruction" % opcode)

    @staticmethod
    def count_args(actual, needed, opcode):
        if actual != needed:
            raise IPPcodeParseError("too many or missing arguments for %s instruction" % opcode)

    def var(self, arg):
        pass

    def symb(self, arg):
        pass

    def label(self, arg):
        pass

    def type(self, arg):
        pass
