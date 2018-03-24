import sys


class Frames:
    def __init__(self):
        self.global_frame = []
        self.local_frame = None
        self.temporary_frame = None

    def add_to_global_frame(self, variable):
        if self.get_from_global_grame(variable.name, False):
            sys.stderr.write("ERROR: Variable %s already defined in global frame!\n" % variable.name)
            exit(52)
        self.global_frame.append(variable)

    def get_from_global_grame(self, name, error_if_not_found=True):
        for var in self.global_frame:
            if var.name == name:
                return var

        if error_if_not_found:
            sys.stderr.write("ERROR: Variable %s is not defined!\n" % name)
            exit(54)

        return None
