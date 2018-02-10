import argparse
import sys
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--help", action="store_true")
parser.add_argument("--source")
args = parser.parse_args()

if args.help:
    if len(sys.argv) != 2:
        sys.stderr.write("ERROR: Can not combine --help with other parameters!\n")
        exit(10)

    print("-------- Program help --------")
    print("Program loads XML file from --source parametr and interprets it.")
    exit(0)

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

    order = 1
    for child in root:
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

except FileNotFoundError:
    sys.stderr.write("ERROR: Can not open source file!\n")
    exit(11)
except ET.ParseError as e:
    sys.stderr.write("ERROR: Source file has wrong XML format (%s)!\n" % str(e))
    exit(31)
