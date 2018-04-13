import argparse
import sys
import xml.etree.ElementTree as ET
import interpret_factory as IFactory


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write("ERROR: Error while parsing arguments!\n")
        exit(10)


parser = ArgumentParser(add_help=False)
parser.add_argument("--help", action="store_true")
parser.add_argument("--source")
parser.add_argument("--stats")
parser.add_argument("--insts", action="store_true")
parser.add_argument("--vars", action="store_true")

args = parser.parse_args()

if args.help:
    if len(sys.argv) != 2:
        sys.stderr.write("ERROR: Can not combine --help with other parameters!\n")
        exit(10)

    print("-------- Program help --------")
    print("Program loads XML file from --source parametr and interprets it.")
    print("Usage: python3.6 ./interpret.py --source=source_xml_file")
    exit(0)

if (args.insts or args.vars) and not args.stats:
    sys.stderr.write("ERROR: Missing --stats parametr!\n")
    exit(10)

if not args.source:
    sys.stderr.write("ERROR: Missing --source parametr!\n")
    exit(10)

try:
    tree = ET.parse(args.source)
    root = tree.getroot()
    if root.tag != "program":
        raise ET.ParseError("root element must be program")

    if "language" not in root.attrib:
        raise ET.ParseError("missing attribute language in program element")

    for attrib, value in root.attrib.items():
        if attrib == "language":
            if value != "IPPcode18":
                raise ET.ParseError("language attribute must have 'IPPcode18' value")
        elif attrib != "name" and attrib != "description":
            raise ET.ParseError("program element can only contain language, name or description attributes")

    interpret = IFactory.InterpretFactory()
    order = 1
    for child in root:
        opcode = None
        if child.tag != "instruction":
            raise ET.ParseError("program element can contain only instruction subelements")

        if "opcode" not in child.attrib or "order" not in child.attrib:
            raise ET.ParseError("missing attribute opcode or order in program element")

        for attrib, value in child.attrib.items():
            if attrib == "opcode":
                opcode = value
            elif attrib == "order":
                if int(value) != order:
                    raise ET.ParseError("bad instruction order")
                order += 1
            else:
                raise ET.ParseError("instruction element can only contain opcode or order argument")

        args_list = []
        for arg in child:
            try:
                arg_num = int(arg.tag[3:])
            except ValueError:
                raise ET.ParseError("wrong argument number")

            if "type" not in arg.attrib:
                raise ET.ParseError("missing type attribute in arg element")

            if len(arg.attrib) != 1:
                raise ET.ParseError("non allowed attributes in arg element")

            types = ["int", "bool", "string", "float", "label", "type", "var", "label"]

            if arg.attrib["type"] not in types:
                raise ET.ParseError("non allowed arg type")

            while arg_num > len(args_list):
                args_list.append(None)

            args_list[arg_num - 1] = [arg.attrib["type"], arg.text]

        if None in args_list:
            raise ET.ParseError("missing arguments")

        interpret.add_instruction(opcode, args_list, order)
    interpret.run()

    if args.stats:
        try:
            stats = ""
            for argument in sys.argv:
                if argument == "--vars":
                    stats += "%d\n" % interpret.stat_vars
                elif argument == "--insts":
                    stats += "%d\n" % interpret.total_inst

            file = open(args.stats, "w")
            file.seek(0)
            file.write(stats)
            file.truncate()
        except IOError:
            sys.stderr.write("ERROR: Could not open stats file!\n")
            exit(12)

except FileNotFoundError:
    sys.stderr.write("ERROR: Can not open source file!\n")
    exit(11)
except ET.ParseError as e:
    sys.stderr.write("ERROR: Source file has wrong XML format (%s)!\n" % str(e))
    exit(31)
except IFactory.IPPcodeParseError as e:
    sys.stderr.write("ERROR: Lexical or syntax error in XML (%s)!\n" % str(e))
    exit(32)
