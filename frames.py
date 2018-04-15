import sys


class Frames:
    def __init__(self):
        self.get_vars_stats = None
        self.frame_stack = []
        self.global_frame = []
        self.local_frame = None
        self.temporary_frame = None
        self.stat_vars = 0
        self.vars_current = 0

    def push_frame(self):
        if self.temporary_frame is not None:
            if self.local_frame is not None:
                self.vars_current -= len(self.local_frame)

            self.frame_stack.append(self.temporary_frame)
            self.local_frame = self.temporary_frame
            self.temporary_frame = None
        else:
            sys.stderr.write("ERROR: TF not defined!\n")
            exit(55)

    def pop_frame(self):
        if len(self.frame_stack) != 0:
            if self.temporary_frame is not None:
                self.vars_current -= len(self.temporary_frame)
            if self.local_frame is not None:
                self.vars_current -= len(self.local_frame)

            self.temporary_frame = self.frame_stack.pop()
            self.vars_current += len(self.temporary_frame)
            try:
                self.local_frame = self.frame_stack[-1]
                self.vars_current += len(self.local_frame)
            except IndexError:
                self.local_frame = None
        else:
            sys.stderr.write("ERROR: Frame stack is empty!\n")
            exit(55)

    def add_to_global_frame(self, variable):
        self.vars_stats_add()

        if self.get_from_global_frame(variable.name, False):
            sys.stderr.write("ERROR: Variable %s already defined in global frame!\n" % variable.name)
            exit(52)
        self.global_frame.append(variable)

    def add_to_local_frame(self, variable):
        self.vars_stats_add()

        if self.local_frame is None:
            sys.stderr.write("ERROR: LF is not initialized!\n")
            exit(55)

        if not self.get_from_local_frame(variable.name, False):
            self.local_frame.append(variable)

    def add_to_temporary_frame(self, variable):
        self.vars_stats_add()

        if self.temporary_frame is None:
            sys.stderr.write("ERROR: TF is not initialized!\n")
            exit(55)

        if self.get_from_temporary_frame(variable.name, False):
            sys.stderr.write("ERROR: Variable %s already defined in temporary frame!\n" % variable.name)
            exit(52)
        self.temporary_frame.append(variable)

    def get_from_local_frame(self, name, error_if_not_found=True):
        if self.local_frame is None:
            sys.stderr.write("ERROR: LF is not defined!\n")
            exit(55)

        for var in self.local_frame:
            if var.name == name:
                return var

        if error_if_not_found:
            sys.stderr.write("ERROR: Variable %s is not defined in LF!\n" % name)
            exit(54)

        return None

    def get_from_temporary_frame(self, name, error_if_not_found=True):
        if self.temporary_frame is None:
            sys.stderr.write("ERROR: TF is not defined!\n")
            exit(55)

        for var in self.temporary_frame:
            if var.name == name:
                return var

        if error_if_not_found:
            sys.stderr.write("ERROR: Variable %s is not defined in TF!\n" % name)
            exit(54)

        return None

    def get_from_global_frame(self, name, error_if_not_found=True):
        for var in self.global_frame:
            if var.name == name:
                return var

        if error_if_not_found:
            sys.stderr.write("ERROR: Variable %s is not defined in GF!\n" % name)
            exit(54)

        return None

    def vars_stats_add(self):
        self.vars_current += 1
        if self.vars_current > self.stat_vars:
            self.stat_vars = self.vars_current
