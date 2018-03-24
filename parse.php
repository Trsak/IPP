<?php
/**
 * @author Petr Sopf <xsopfp00@stud.fit.vutbr.cz>
 * @project IPPcode18
 * @file parse.php
 */

//Error constants
const ERROR_PARAM = 10;
const ERROR_FILE_IN = 11;
const ERROR_FILE_OUT = 12;
const ERROR_CODE = 21;

//Scanner constants
const FILE_END = -2;
const INST_HEADER = -1;
const INST_MOVE = 0;
const INST_CREATEFRAME = 1;
const INST_PUSHFRAME = 2;
const INST_POPFRAME = 3;
const INST_DEFVAR = 4;
const INST_CALL = 5;
const INST_RETURN = 6;
const INST_PUSHS = 7;
const INST_POPS = 8;
const INST_ADD = 9;
const INST_SUB = 10;
const INST_MUL = 11;
const INST_IDIV = 12;
const INST_LT = 13;
const INST_GT = 14;
const INST_EQ = 15;
const INST_AND = 16;
const INST_OR = 17;
const INST_NOT = 18;
const INST_INT2CHAR = 19;
const INST_STRI2INT = 20;
const INST_READ = 21;
const INST_WRITE = 22;
const INST_CONCAT = 23;
const INST_STRLEN = 24;
const INST_GETCHAR = 25;
const INST_SETCHAR = 26;
const INST_TYPE = 27;
const INST_LABEL = 28;
const INST_JUMP = 29;
const INST_JUMPIFEQ = 30;
const INST_JUMPIFNEQ = 31;
const INST_DPRINT = 32;
const INST_BREAK = 33;
const TYPE_INT = 40;
const TYPE_STRING = 41;
const TYPE_BOOL = 42;
const TYPE_FLOAT = 43;
const FRAME_GLOBAL = 50;
const FRAME_LOCAL = 51;
const FRAME_TEMPORARY = 52;
const SEPARATOR = 60;
const UNKNOWN = 100;
const END = 101;
const NEWLINE = 102;

/**
 * Scanner is used for tokenization of chars from STDIN
 */
class Scanner
{
    /**
     * Changes current file position indicator in STDIN
     * New position is calculated by (current position - $num)
     * @param int $num How many chars to go back
     * @return void
     */
    public function unGet($num)
    {
        fseek(STDIN, ftell(STDIN) - $num);
    }

    /**
     * Returns next token
     * Implemented as finite automaton
     * @param int $commentsCount Reference to variable used to count comments
     * @param bool $gettingValue If true, all chars until first white char will be returned
     * @return array Index 0 contains token constant, index 1 contains it's value
     */
    public function getNextToken(&$commentsCount, $gettingValue = false)
    {
        $state = 0;

        while (true) {
            //Get next char from STDIN
            $char = fgetc(STDIN);

            switch ($state) {
                case 0:
                    if ($char == ".") {
                        //Might be introductory row
                        $state = 1;
                    } elseif ($char == PHP_EOL) {
                        //New line
                        return [NEWLINE, ""];
                    } elseif (ctype_space($char)) {
                        //Get rid of spaces
                        while (ctype_space($char = fgetc(STDIN))) {
                            if ($char == PHP_EOL) {
                                return [NEWLINE, ""];
                            }
                            continue;
                        }

                        $this->unGet(1);
                    } elseif ($char == "#") {
                        //Comments
                        ++$commentsCount;
                        $state = 2;
                    } elseif ($char == "@" && !$gettingValue) {
                        //Separator
                        $this->unGet(2);
                        if (ctype_space(fgetc(STDIN))) {
                            fwrite(STDERR, "ERROR: Spaces before separator are not allowed!\n");
                            exit(ERROR_CODE);
                        }
                        fgetc(STDIN);

                        return [SEPARATOR, "@"];
                    } else {
                        //Something else
                        $string = $char;
                        $ignore = false;

                        while (!ctype_space($char = fgetc(STDIN))) {
                            if ($char === false) {
                                break;
                            } elseif ($char == "@" && !$gettingValue) {
                                $this->unGet(1);
                                break;
                            } elseif ($char == "#") {
                                ++$commentsCount;
                                $ignore = true;

                                while (($char = fgetc(STDIN)) != PHP_EOL) {
                                    continue;
                                }
                                $this->unGet(1);
                            } elseif ($char == "\\") {
                                $escapeSequence = fgetc(STDIN) . fgetc(STDIN) . fgetc(STDIN);
                                if (!ctype_digit($escapeSequence)) {
                                    fwrite(STDERR, "ERROR: Wrong escape sequence!\n");
                                    exit(ERROR_CODE);
                                }

                                $char .= $escapeSequence;
                            }

                            if (!$ignore) {
                                $string .= $char;
                            }
                        }

                        if ($char == PHP_EOL) {
                            $this->unGet(1);
                        }

                        //Check if token is instruction
                        switch (strtolower($string)) {
                            case "move":
                                return [INST_MOVE, $string];
                            case "createframe":
                                return [INST_CREATEFRAME, $string];
                            case "pushframe":
                                return [INST_PUSHFRAME, $string];
                            case "popframe":
                                return [INST_POPFRAME, $string];
                            case "defvar":
                                return [INST_DEFVAR, $string];
                            case "call":
                                return [INST_CALL, $string];
                            case "return":
                                return [INST_RETURN, $string];
                            case "pushs":
                                return [INST_PUSHS, $string];
                            case "pops":
                                return [INST_POPS, $string];
                            case "add":
                                return [INST_ADD, $string];
                            case "sub":
                                return [INST_SUB, $string];
                            case "mul":
                                return [INST_MUL, $string];
                            case "idiv":
                                return [INST_IDIV, $string];
                            case "lt":
                                return [INST_LT, $string];
                            case "gt":
                                return [INST_GT, $string];
                            case "eq":
                                return [INST_EQ, $string];
                            case "and":
                                return [INST_AND, $string];
                            case "or":
                                return [INST_OR, $string];
                            case "not":
                                return [INST_NOT, $string];
                            case "int2char":
                                return [INST_INT2CHAR, $string];
                            case "stri2int":
                                return [INST_STRI2INT, $string];
                            case "read":
                                return [INST_READ, $string];
                            case "write":
                                return [INST_WRITE, $string];
                            case "concat":
                                return [INST_CONCAT, $string];
                            case "strlen":
                                return [INST_STRLEN, $string];
                            case "getchar":
                                return [INST_GETCHAR, $string];
                            case "setchar":
                                return [INST_SETCHAR, $string];
                            case "type":
                                return [INST_TYPE, $string];
                            case "label":
                                return [INST_LABEL, $string];
                            case "jump":
                                return [INST_JUMP, $string];
                            case "jumpifeq":
                                return [INST_JUMPIFEQ, $string];
                            case "jumpifneq":
                                return [INST_JUMPIFNEQ, $string];
                            case "dprint":
                                return [INST_DPRINT, $string];
                            case "break":
                                return [INST_BREAK, $string];
                        }

                        //Check for case sensitive cases
                        switch ($string) {
                            case "int":
                                return [TYPE_INT, "int"];
                            case "string":
                                return [TYPE_STRING, "string"];
                            case "bool":
                                return [TYPE_BOOL, "bool"];
                            case "float":
                                return [TYPE_FLOAT, "float"];
                            case "GF":
                                return [FRAME_GLOBAL, "GF"];
                            case "LF":
                                return [FRAME_LOCAL, "LF"];
                            case "TF":
                                return [FRAME_TEMPORARY, "TF"];
                            default:
                                if ($string == false) {
                                    return [FILE_END, $string];
                                }
                                return [UNKNOWN, $string];
                        }
                    }
                    break;
                case 1:
                    //Check for introductory row
                    $string = $char;
                    $ignore = false;

                    while (($char = fgetc(STDIN)) != PHP_EOL) {
                        if ($char == "#") {
                            ++$commentsCount;
                            $ignore = true;
                        }

                        if (!$ignore) {
                            $string .= $char;
                        }
                    }
                    $this->unGet(1);

                    if (trim(strtolower($string)) != "ippcode18") {
                        //It is not introductory row token, return unknown
                        return [UNKNOWN, "." . $string];
                    }

                    //It is introductory row
                    return [INST_HEADER, ""];
                case 2:
                    //In case of comment, just ignore everything until new line
                    while (($char = fgetc(STDIN)) != PHP_EOL) {
                        if (feof(STDIN)) {
                            break;
                        }
                        continue;
                    }

                    return [NEWLINE, ""];

            }
        }

        return [UNKNOWN, ""];
    }
}

/**
 * Parses STDIN and checks for syntax a lexical errors
 */
class Parse
{
    /**
     * @var Scanner Instance of Scanner
     */
    private $scanner;

    /**
     * @var int Current instruction order
     */
    private $order;

    /**
     * @var int Current instruction's argument position
     */
    private $arg;

    /**
     * @var XMLWriter Instance of XMLWriter
     */
    private $xml;

    /**
     * @var int Current comments count
     */
    private $commentsCount;

    /**
     * Parse constructor
     * Creates instances of Scanner and XMLWriter
     * Sets default variable values and starts generating XML
     */
    public function __construct()
    {
        $this->scanner = new Scanner;
        $this->order = 0;
        $this->arg = 0;
        $this->commentsCount = 0;

        //Start generating XML
        $this->xml = new XMLWriter();
        $this->xml->openMemory();
        $this->xml->setIndent(4);
        $this->xml->startDocument("1.0", "UTF-8");
        $this->xml->setIndentString(" ");

        $this->xml->startElement('program');

        $this->addXMLAtribute("language", "IPPcode18");

        //Run parser
        $this->start();

        //End of XML generation
        $this->xml->endElement();;
        $this->xml->endDocument();
    }

    /**
     * Returns the whole generated XML
     * @return string Output XML
     */
    public function getXML()
    {
        return $this->xml->outputMemory();
    }

    /**
     * Returns current instruction order
     * @return int
     */
    public function getInstructionsNumber()
    {
        return $this->order;
    }

    /**
     * Returns comments count
     * @return int
     */
    public function getCommentsCount()
    {
        return $this->commentsCount;
    }

    /**
     * Starts parsing of whole STDIN
     */
    private function start()
    {
        //Get first token
        $token = $this->scanner->getNextToken($this->commentsCount);

        //First token must be instruction introductory header
        if ($token[0] == INST_HEADER) {
            //Run until the end of STDIN
            while (!feof(STDIN)) {
                $this->instruction();
            }
        } else {
            fwrite(STDERR, "ERROR: Missing .IPPcode18 header on first line!\n");
            exit(ERROR_CODE);
        }
    }

    /**
     * Processing instruction tokens
     */
    private function instruction()
    {
        //Check if there is new line after last token / introductory header
        $token = $this->scanner->getNextToken($this->commentsCount);

        if ($token[0] != NEWLINE) {
            fwrite(STDERR, "ERROR: Every instruction must be on it's own line!\n");
            exit(ERROR_CODE);
        }

        //Get next token other than new line
        $token = $this->scanner->getNextToken($this->commentsCount);

        while ($token[0] == NEWLINE) {
            $token = $this->scanner->getNextToken($this->commentsCount);
        }

        if ($token[0] >= INST_MOVE && $token[0] <= INST_BREAK) {
            //Start parsing instructions
            $this->arg = 0;
            $this->xml->startElement("instruction");
            $this->addXMLAtribute("order", ++$this->order);

            switch ($token[0]) {
                case INST_MOVE:
                    $this->addXMLAtribute("opcode", "MOVE");
                    $this->variable();
                    $this->symb();
                    break;
                case INST_CREATEFRAME:
                    $this->addXMLAtribute("opcode", "CREATEFRAME");
                    break;
                case INST_PUSHFRAME:
                    $this->addXMLAtribute("opcode", "PUSHFRAME");
                    break;
                case INST_POPFRAME:
                    $this->addXMLAtribute("opcode", "POPFRAME");
                    break;
                case INST_DEFVAR:
                    $this->addXMLAtribute("opcode", "DEFVAR");
                    $this->variable();
                    break;
                case INST_CALL:
                    $this->addXMLAtribute("opcode", "CALL");
                    $this->label();
                    break;
                case INST_RETURN:
                    $this->addXMLAtribute("opcode", "RETURN");
                    break;
                case INST_PUSHS:
                    $this->addXMLAtribute("opcode", "PUSHS");
                    $this->symb();
                    break;
                case INST_POPS:
                    $this->addXMLAtribute("opcode", "POPS");
                    $this->variable();
                    break;
                case INST_ADD:
                    $this->addXMLAtribute("opcode", "ADD");
                    $this->variable();
                    $this->symb();
                    $this->symb();
                    break;
                case INST_SUB:
                    $this->addXMLAtribute("opcode", "SUB");
                    $this->variable();
                    $this->symb();
                    $this->symb();
                    break;
                case INST_MUL:
                    $this->addXMLAtribute("opcode", "MUL");
                    $this->variable();
                    $this->symb();
                    $this->symb();
                    break;
                case INST_IDIV:
                    $this->addXMLAtribute("opcode", "IDIV");
                    $this->variable();
                    $this->symb();
                    $this->symb();
                    break;
                case INST_LT:
                    $this->addXMLAtribute("opcode", "LT");
                    $this->variable();
                    $this->symb();
                    $this->symb();
                    break;
                case INST_GT:
                    $this->addXMLAtribute("opcode", "GT");
                    $this->variable();
                    $this->symb();
                    $this->symb();
                    break;
                case INST_EQ:
                    $this->addXMLAtribute("opcode", "EQ");
                    $this->variable();
                    $this->symb();
                    $this->symb();
                    break;
                case INST_AND:
                    $this->addXMLAtribute("opcode", "AND");
                    $this->variable();
                    $this->symb();
                    $this->symb();
                    break;
                case INST_OR:
                    $this->addXMLAtribute("opcode", "OR");
                    $this->variable();
                    $this->symb();
                    $this->symb();
                    break;
                case INST_NOT:
                    $this->addXMLAtribute("opcode", "NOT");
                    $this->variable();
                    $this->symb();
                    break;
                case INST_INT2CHAR:
                    $this->addXMLAtribute("opcode", "INT2CHAR");
                    $this->variable();
                    $this->symb();
                    break;
                case INST_STRI2INT:
                    $this->addXMLAtribute("opcode", "STRI2INT");
                    $this->variable();
                    $this->symb();
                    $this->symb();
                    break;
                case INST_READ:
                    $this->addXMLAtribute("opcode", "READ");
                    $this->variable();
                    $this->type();
                    break;
                case INST_WRITE:
                    $this->addXMLAtribute("opcode", "WRITE");
                    $this->symb();
                    break;
                case INST_CONCAT:
                    $this->addXMLAtribute("opcode", "CONCAT");
                    $this->variable();
                    $this->symb();
                    $this->symb();
                    break;
                case INST_STRLEN:
                    $this->addXMLAtribute("opcode", "STRLEN");
                    $this->variable();
                    $this->symb();
                    break;
                case INST_GETCHAR:
                    $this->addXMLAtribute("opcode", "GETCHAR");
                    $this->variable();
                    $this->symb();
                    $this->symb();
                    break;
                case INST_SETCHAR:
                    $this->addXMLAtribute("opcode", "SETCHAR");
                    $this->variable();
                    $this->symb();
                    $this->symb();
                    break;
                case INST_TYPE:
                    $this->addXMLAtribute("opcode", "TYPE");
                    $this->variable();
                    $this->symb();
                    break;
                case INST_LABEL:
                    $this->addXMLAtribute("opcode", "LABEL");
                    $this->label();
                    break;
                case INST_JUMP:
                    $this->addXMLAtribute("opcode", "JUMP");
                    $this->label();
                    break;
                case INST_JUMPIFEQ:
                    $this->addXMLAtribute("opcode", "JUMPIFEQ");
                    $this->label();
                    $this->symb();
                    $this->symb();
                    break;
                case INST_JUMPIFNEQ:
                    $this->addXMLAtribute("opcode", "JUMPIFNEQ");
                    $this->label();
                    $this->symb();
                    $this->symb();
                    break;
                case INST_DPRINT:
                    $this->addXMLAtribute("opcode", "DPRINT");
                    $this->symb();
                    break;
                case INST_BREAK:
                    $this->addXMLAtribute("opcode", "BREAK");
                    break;
                default:
                    break;
            }

            $this->xml->endElement();
        } else {
            if (feof(STDIN)) {
                return;
            }

            fwrite(STDERR, "ERROR: Expected instruction, obtained something else!\n");
            exit(ERROR_CODE);
        }
    }

    /**
     * Gets value of constants
     * @return string value
     */
    private function value()
    {
        $token = $this->scanner->getNextToken($this->commentsCount, true);

        if ($token[0] == NEWLINE) {
            $token[1] = "";
            $this->scanner->unGet(1);
        }

        return $token[1];
    }

    /**
     * Gets variable/label name and checks it's validity
     * @return string variable/label name
     */
    private function name()
    {
        $token = $this->scanner->getNextToken($this->commentsCount);
        if ($token[0] == NEWLINE) {
            $token[1] = "";
            $this->scanner->unGet(1);
        }

        if (($token[1] != "") && preg_match("/[^A-ZÁ-Ža-zá-ž0-9\-\*\$%_&]/", $token[1])) {
            fwrite(STDERR, "ERROR: Variable or label name contains illegal characters!\n");
            exit(ERROR_CODE);
        }

        if (ctype_digit($token[1][0])) {
            fwrite(STDERR, "ERROR: Variable or label name can not start with number!\n");
            exit(ERROR_CODE);
        }

        return $token[1];
    }

    /**
     * Checks if next token is valid frame
     * @return string frame
     */
    private function frame()
    {
        $token = $this->scanner->getNextToken($this->commentsCount);

        if ($token[0] >= FRAME_GLOBAL && $token[0] <= FRAME_TEMPORARY) {
            return $token[1];
        } else {
            fwrite(STDERR, "ERROR: Expected frame, obtained something else!\n");
            exit(ERROR_CODE);
        }
    }

    /**
     * Checks if next token is separator
     * @return string separator
     */
    private function separator()
    {
        $token = $this->scanner->getNextToken($this->commentsCount);

        if ($token[0] == SEPARATOR) {
            return $token[1];
        } else {
            fwrite(STDERR, "ERROR: Expected separator, obtained something else!\n");
            exit(ERROR_CODE);
        }
    }

    /**
     * Checks if next token is type and generates xml for it
     */
    private function type()
    {
        $token = $this->scanner->getNextToken($this->commentsCount);

        if ($token[0] >= TYPE_INT && $token[0] <= TYPE_FLOAT) {
            $this->xml->startElement("arg" . (++$this->arg));
            $this->addXMLAtribute("type", "type");
            $this->xml->text($token[1]);
            $this->xml->endElement();
        } else {
            fwrite(STDERR, "ERROR: Expected type, obtained something else!\n");
            exit(ERROR_CODE);
        }
    }

    /**
     * Generates xml for label
     */
    private function label()
    {
        $name = $this->name();

        $this->xml->startElement("arg" . (++$this->arg));
        $this->addXMLAtribute("type", "label");
        $this->xml->text($name);
        $this->xml->endElement();
    }

    /**
     * Checks if next token is valid symbol and generates xml for it
     */
    private function symb()
    {
        $token = $this->scanner->getNextToken($this->commentsCount);

        //Symbol can be only constant or variable
        if (($token[0] >= FRAME_GLOBAL && $token[0] <= FRAME_TEMPORARY) || ($token[0] >= TYPE_INT && $token[0] <= TYPE_FLOAT)) {
            $symb = $token[1];
            $sep = $this->separator();

            $this->xml->startElement("arg" . (++$this->arg));

            if ($token[0] >= FRAME_GLOBAL && $token[0] <= FRAME_TEMPORARY) {
                //Symbol is variable
                $name = $this->name();
                $this->addXMLAtribute("type", "var");
                $this->xml->text(strtoupper($symb) . $sep . $name);
            } else {
                //Symbol is constant
                $name = $this->value();
                $this->addXMLAtribute("type", $token[1]);

                if ($token[0] == TYPE_STRING) {
                    //Replace chars in string with xml entities
                    $char = array("<", ">", "&");
                    $replacement = array("&lt;", "&gt;", "&amp;");
                    str_replace($name, $replacement, $char);
                } elseif ($token[0] == TYPE_BOOL) {
                    //Check for valid bool value
                    if ($name != "true" && $name != "false") {
                        fwrite(STDERR, "ERROR: Wrong bool value!\n");
                        exit(ERROR_CODE);
                    }
                }

                $this->xml->text($name);
            }

            $this->xml->endElement();
        } else {
            fwrite(STDERR, "ERROR: Expected symbol, obtained something else!\n");
            exit(ERROR_CODE);
        }

    }

    /**
     * Generates xml for variable
     */
    private function variable()
    {
        $frame = $this->frame();
        $sep = $this->separator();
        $name = $this->name();

        $this->xml->startElement("arg" . (++$this->arg));
        $this->addXMLAtribute("type", "var");
        $this->xml->text(strtoupper($frame) . $sep . $name);
        $this->xml->endElement();
    }

    /**
     * Generates xml attribute
     * @param string $attribute attribute name
     * @param string $value attribute value
     */
    private function addXMLAtribute($attribute, $value)
    {
        $this->xml->startAttribute($attribute);
        $this->xml->text($value);
        $this->xml->endAttribute();
    }
}


//Program options
$shortOptions = "";
$longOptions = array(
    "help",
    "stats:",
    "comments",
    "loc"
);

$options = getopt($shortOptions, $longOptions);

//Parse parameters
if ((empty($options) && $argc == 1) || (!empty($options) && isset($options["stats"]))) {
    $logFile = false;
    $logLoc = false;
    $logComents = false;

    if (isset($options["stats"])) {
        $logFile = $options["stats"];
    }

    if (isset($options["loc"])) {
        $logLoc = true;
    }

    if (isset($options["comments"])) {
        $logComents = true;
    }

    if ($logFile && !$logLoc && !$logComents) {
        fwrite(STDERR, "ERROR: Missing --loc or --comments parametr for stats!\n");
        exit(ERROR_PARAM);
    } elseif ($logFile && ($logLoc && $logComents) && $argc != 4) {
        fwrite(STDERR, "ERROR: Bad parameters usage! Use --help.\n");
        exit(ERROR_PARAM);
    } elseif ($logFile && ((!$logLoc || !$logComents) && $argc != 3)) {
        fwrite(STDERR, "ERROR: Bad parameters usage! Use --help.\n");
        exit(ERROR_PARAM);
    }

    //Run parser
    $parse = new Parse;

    //Log stats
    if ($logFile) {
        $content = "";
        foreach ($options as $key => $option) {
            if ($key == "loc") {
                $content .= $parse->getInstructionsNumber() . "\n";
            } elseif ($key == "comments") {
                $content .= $parse->getCommentsCount() . "\n";
            }
        }

        $writeStats = @file_put_contents($logFile, $content);
        if (!$writeStats) {
            fwrite(STDERR, "ERROR: Permissions denied for stats file.\n");
            exit(ERROR_FILE_OUT);
        }
    }

    //Output XML
    echo $parse->getXML();

    exit(0);
} elseif (isset($options["help"]) && $argc == 2) {
    echo "-------- Program help --------\nProgram reads source code of IPPcode18 from STDIN, then makes lexical and syntactic analysis of it.\n
    If analysis ends successfully, XML with program representation is printed to STDOUT.\n";
} else {
    fwrite(STDERR, "ERROR: Bad parameters usage! Use --help.\n");
    exit(ERROR_PARAM);
}