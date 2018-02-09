<?php
//TODO: File open permissions

class TestResult
{
    private $test;
    private $runtime;
    private $exitcode;
    private $exitcodeSame;
    private $outputTested;
    private $outputSame;
    private $testPassed;

    public function __construct($test, $runtime, $exitcode, $exitcodeSame, $outputTested, $outputSame, $testPassed)
    {
        $this->test = $test;
        $this->runtime = $runtime;
        $this->exitcode = $exitcode;
        $this->exitcodeSame = $exitcodeSame;
        $this->outputTested = $outputTested;
        $this->outputSame = $outputSame;
        $this->testPassed = $testPassed;
    }

    /**
     * @return mixed
     */
    public function getOutputTested()
    {
        return $this->outputTested;
    }

    /**
     * @return mixed
     */
    public function getExitcode()
    {
        return $this->exitcode;
    }

    /**
     * @return mixed
     */
    public function getTest()
    {
        return $this->test;
    }

    /**
     * @return mixed
     */
    public function getRuntime()
    {
        return $this->runtime;
    }

    /**
     * @return mixed
     */
    public function getExitcodeSame()
    {
        return $this->exitcodeSame;
    }

    /**
     * @return mixed
     */
    public function getOutputSame()
    {
        return $this->outputSame;
    }

    /**
     * @return mixed
     */
    public function getTestPassed()
    {
        return $this->testPassed;
    }
}

$time_start = microtime(true);

$settings = array(
    "dir" => "./",
    "recursively" => false,
    "parser" => "./parse.php",
    "interpret" => "./interpret.py"
);

///Program options
$shortOptions = "";
$longOptions = array(
    "help",
    "directory:",
    "parse-script:",
    "int-script:",
    "recursive"
);

$options = getopt($shortOptions, $longOptions);
if (isset($options["help"]) && $argc != 2) {
    echo "Help\n";
    exit(0);
} elseif (count($argv) !== (count($options) + 1)) {
    error_log("ERROR: Bad parameters usage! Use --help.");
    exit(10);
} else {
    foreach ($options as $option => $value) {
        switch ($option) {
            case "directory":
                $settings["dir"] = $value;
                break;
            case "recursive":
                $settings["recursively"] = true;
                break;
            case "parse-script":
                $settings["parser"] = $value;
                break;
            case "int-script":
                $settings["interpret"] = $value;
                break;
        }
    }
}

if (!file_exists($settings["dir"]) || !is_dir($settings["dir"])) {
    error_log("ERROR: Tests directory (" . $settings["dir"] . ") does not exist or isn not a directory!");
    exit(11);
} elseif (!file_exists($settings["parser"])) {
    error_log("ERROR: Parser file (" . $settings["parser"] . ") does not exist!");
    exit(11);
} elseif (!file_exists($settings["interpret"])) {
    error_log("ERROR: Interpret file (" . $settings["interpret"] . ") does not exist!");
    exit(11);
}

$dir = new RecursiveDirectoryIterator($settings["dir"]);
$ite = new RecursiveIteratorIterator($dir);
$files = new RegexIterator(($settings["recursively"] === true) ? $ite : $dir, "/^.*\.(src)$/", RegexIterator::GET_MATCH);

$tests = [];
$testsNumber = 0;
$testsFailed = 0;

foreach ($files as $file) {
    $filePath = $file[0];
    $testFiles = substr($filePath, 0, -4);

    if (!file_exists($testFiles . ".out")) {
        $newOut = fopen($testFiles . ".out", "w");
        $outputExpected = "";
        fclose($newOut);
    } else {
        $outputExpected = file_get_contents($testFiles . ".out");
    }

    if (!file_exists($testFiles . ".in")) {
        $newIn = fopen($testFiles . ".in", "w");
        $in = "";
        fclose($newIn);
    } else {
        $in = file_get_contents($testFiles . ".in");
    }

    if (!file_exists($testFiles . ".rc")) {
        $newRc = fopen($testFiles . ".rc", "w");
        $rc = 0;
        fwrite($newRc, "0");
        fclose($newRc);
    } else {
        $rc = file_get_contents($testFiles . ".rc");
    }

    $test_start = microtime(true);
    $xml = exec("php5.6 " . $settings["parser"] . " < " . $filePath);
    $temp = tmpfile();
    fwrite($temp, $xml);
    fseek($temp, 0);
    $data = stream_get_meta_data($temp);

    $output = exec("python3.6 " . $settings["interpret"] . " --source=" . $data["uri"] . " > " . $data["uri"], $o, $exitcode);
    $diff = exec("diff " . $data["uri"] . " " . $testFiles . ".out");
    fclose($temp);
    $test_end = microtime(true);

    $outputSame = true;
    $exitcodeSame = true;

    if ($rc != $exitcode) {
        $exitcodeSame = false;
        $outputSame = false;
        ++$testsFailed;
    } elseif (!empty($diff)) {
        $outputSame = false;
        ++$testsFailed;
    }

    $tests[] = new TestResult($filePath, round(($test_end - $test_start) * 100, 2), $exitcode, $exitcodeSame, (($rc == 0 and $exitcodeSame) ? true : false), $outputSame, ($exitcodeSame && $outputSame));
    ++$testsNumber;
}

$time_end = microtime(true);
header("Content-Type: text/html; charset=UTF-8");

echo "
<!DOCTYPE html>
<html>
<head>
<meta charset=\"UTF-8\">
<title>Tests report</title>
<style type='text/css'>
body {
    text-align: center;
}

table {
    margin: 10px auto;
    width: 100%;
    max-width: 500px;
    border-collapse: collapse;
}

.tests {
    max-width: 800px;
}

tr {
    height: 50px;
    background-color: #e8ecef;
    border-bottom: rgba(0, 0, 0, 0.05) 1px solid;
}

td {
    box-sizing: border-box;
}

th {
    font-weight: bold;
}

tr.head {
    height: 70px;
    background-color: #63acb7;
    color: #f6f3f7;
    font-size: 26px;
}

.tests tr.head {
    height: 25px;;
    background-color: #63acb7;
    color: #f6f3f7;
    font-size: 22px;
    
}

.tests td {
    border: rgba(0, 0, 0, 0.05) 1px solid;
    text-align: left;
}

.tests td.center {
    text-align: center;
    width: 1%;
}

.success {
    background-color: #82ddaa;
}

.failure {
    background-color: #dd8295;
}

.tests .head th {
    padding: 10px;
}

.tests td {
    padding: 4px;
}

</style>
</head>
<body>
<table class='summary'>
    <tr class='head'>
        <th colspan='2'>Summary</th>  
    </tr>
    <tr>
        <th>Runtime</th>
        <td>" . round(($time_end - $time_start) * 100, 2) . " ms</td>    
    </tr>
    <tr>
        <th>Tests total</th>
        <td>" . $testsNumber . "</td>    
    </tr>
    <tr class='" . (($testsFailed == 0) ? "success" : "failure") . "'>
        <th colspan='2'>" . (($testsFailed == 0) ? "ALL TESTS PASSED" : $testsFailed . " TESTS FAILED") . "</th>  
    </tr>
</table>


<table class='tests'>
    <tr class='head'>
        <th>Test</th>  
        <th>Runtime</th>  
        <th>Exitcode</th>  
        <th>Output</th>  
    </tr>";

foreach ($tests as $test) {
    $output = "SAME";

    if (!$test->getOutputTested()) {
        $output = "----";
    } elseif (!$test->getOutputSame()) {
        $output = "DIFF";
    }

    echo "
    <tr>
        <td class='" . (($test->getTestPassed()) ? "success" : "failure") . "'>" . $test->getTest() . "</td>  
        <td class='center'>" . $test->getRuntime() . " ms</td>  
        <td class='center " . (($test->getExitcodeSame()) ? "success" : "failure") . "'>" . $test->getExitcode() . "</td>  
        <td class='center " . (($test->getOutputSame()) ? "success" : "failure") . "'>" . $output . " </td >  
    </tr > ";
}

echo "
</table >
</body >
</html >
    ";

exit(0);