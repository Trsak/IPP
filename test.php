<?php
/**
 * @author Petr Sopf <xsopfp00@stud.fit.vutbr.cz>
 * @project IPPcode18
 * @file test.php
 */

/**
 * Class for runing and maintaining tests
 */
class Test
{
    /**
     * @var array Test files
     */
    private $files;

    /**
     * @var array Values from test files
     */
    private $data;

    /**
     * @var array User settings
     */
    private $settings;

    /**
     * @var float Test runtime
     */
    private $runtime;

    /**
     * @var string Reason of test's fail/success
     */
    private $reason;

    /**
     * @var bool True if test passed, otherwise false
     */
    private $passed;

    /**
     * Test constructor
     * Sets private variable values and runs test
     * @param $files array Test files
     * @param $data array Values from test files
     * @param $settings array User settings
     */
    public function __construct($files, $data, $settings)
    {
        $this->files = $files;
        $this->data = $data;
        $this->settings = $settings;

        //Run test
        $this->run();
    }

    /**
     * Runs tests
     */
    private function run()
    {
        $test_start = microtime(true);

        if ($this->data["exitcode"] != 0) {
            //We do not have to compare output
            $results = $this->compareExitCode();
        } else {
            //We have to compare interpret output
            $results = $this->compareOutput();
        }

        $test_end = microtime(true);

        //Set test results
        $this->runtime = round(($test_end - $test_start) * 100, 2);
        $this->passed = $results[0];
        $this->reason = $results[1];
    }

    /**
     * Compares outputs, checks if exit codes are 0
     * @return array Result, index 0 is bool value of test result and index 1 is reason for test failure/success
     */
    private function compareOutput()
    {
        $result = array();

        exec("php5.6 " . $this->settings["parser"] . " < " . $this->files["src"] . " 2> /dev/null", $out, $exitCode);
        $xml = implode("\n", $out);

        //Check if parse.php ended with exit code 0
        if ($exitCode != 0) {
            $result[0] = false;
            $result[1] = "Parser ended with exit code " . $exitCode . " (expected 0).";
            return $result;
        }

        $temp = tmpfile();
        fwrite($temp, $xml);
        fseek($temp, 0);
        $tempData = stream_get_meta_data($temp);

        exec("python3.6 " . $this->settings["interpret"] . " --source=\"" . $tempData["uri"] . "\" 2> /dev/null", $outInterpret, $exitCode);
        file_put_contents($tempData["uri"], $outInterpret);

        //Check if parse.php interpret with exit code 0
        if ($exitCode != 0) {
            $result[0] = false;
            $result[1] = "Interpret ended with exit code " . $exitCode . " (expected 0).";
            return $result;
        }

        //Compare outputs
        $diff = exec("diff " . $tempData["uri"] . " " . $this->files["out"] . " 2> /dev/null");
        fclose($temp);

        if (empty($diff)) {
            $result[0] = true;
            $result[1] = "Obtained expected output.";
        } else {
            $result[0] = false;
            $result[1] = "Obtained different output.";
        }

        return $result;
    }

    /**
     * Checks for needed exit codes
     * @return array Result, index 0 is bool value of test result and index 1 is reason for test failure/success
     */
    private function compareExitCode()
    {
        $result = array();

        if ($this->data["exitcode"] == 21) {
            //Check if parse.php exit code is 21
            exec("php5.6 " . $this->settings["parser"] . " < " . $this->files["src"] . " 2> /dev/null", $null, $exitCode);

            if ($exitCode == 21) {
                $result[0] = true;
                $result[1] = "Parser ended with expected exit code (21).";
            } else {
                $result[0] = false;
                $result[1] = "Parser ended with exit code " . $exitCode . " (expected 21).";
            }
        } else {
            //Checks if interpret has needed exit code
            $xml = exec("php5.6 " . $this->settings["parser"] . " < " . $this->files["src"] . " 2> /dev/null");

            $temp = tmpfile();
            fwrite($temp, $xml);
            fseek($temp, 0);
            $tempData = stream_get_meta_data($temp);

            exec("python3.6 " . $this->settings["interpret"] . " --source=" . $tempData["uri"] . " 2> /dev/null", $null, $exitCode);

            if ($exitCode == $this->data["exitcode"]) {
                $result[0] = true;
                $result[1] = "Parser ended with expected exit code (" . $this->data["exitcode"] . ").";
            } else {
                $result[0] = false;
                $result[1] = "Parser ended with exit code " . $exitCode . " (expected " . $this->data["exitcode"] . ").";
            }

            fclose($temp);
        }

        return $result;
    }

    /**
     * Returns readable test name
     * Uppers first char and replaces _ with whitespace
     * @return string Test name
     */
    public function getTestName()
    {
        $info = pathinfo($this->files["src"]);
        $name = $info["filename"];
        $name = str_replace("_", " ", $name);
        return ucfirst($name);
    }

    /**
     * Returns test location
     * @return string location
     */
    public function getTestLocation()
    {
        return $this->files["src"];
    }

    /**
     * Returns test result
     * @return bool result - true on success, false on failure
     */
    public function getResult()
    {
        return $this->passed;
    }

    /**
     * Returns reason of test success/failure
     * @return string reason
     */
    public function getReason()
    {
        return $this->reason;
    }

    /**
     * Returns test runtime
     * @return float runtime
     */
    public function getRuntime()
    {
        return $this->runtime;
    }
}

/**
 * Test factory used to prepare everything needed for test
 */
class TestsFactory
{
    /**
     * Prepares test
     * @param $srcFile string Path to .src file
     * @param $settings
     * @return Test Test run instance
     */
    public static function prepareAndRun($srcFile, $settings)
    {
        //Get file path without extension
        $filesPath = substr($srcFile, 0, -4);

        //Manage all needed files
        $files = array();
        $files["src"] = $srcFile;
        $files["out"] = $filesPath . ".out";
        $files["in"] = $filesPath . ".in";
        $files["rc"] = $filesPath . ".rc";

        //Get data from test files
        $data = array();
        $data["output"] = self::getTestFileContent($filesPath . ".out", null);
        $data["stdin"] = self::getTestFileContent($filesPath . ".in", null);
        $data["exitcode"] = self::getTestFileContent($filesPath . ".rc", 0);

        //Create and return instance of Test
        return new Test($files, $data, $settings);
    }

    /**
     * Gets data from test files
     * If files does not exist, then new one is created and filled with default value
     * @param string $file File path
     * @param string $default Default file value
     * @return string File value
     */
    private static function getTestFileContent($file, $default)
    {
        if (!file_exists($file)) {
            //File does not exist, create new one and fill it with default value
            $newFile = fopen($file, "w");

            if ($default != null) {
                fwrite($newFile, $default);
            }

            fclose($newFile);
            return ($default != null) ? $default : "";
        } else {
            //File exists, just get it's value
            return file_get_contents($file);
        }
    }
}

$time_start = microtime(true);

//Tests settings
$settings = array(
    "dir" => array(getcwd()),
    "recursively" => false,
    "match" => ".*",
    "parser" => getcwd() . "/parse.php",
    "interpret" => getcwd() . "/interpret.py"
);

///Program options
$shortOptions = "";
$longOptions = array(
    "help",
    "directory:",
    "parse-script:",
    "int-script:",
    "testlist:",
    "match:",
    "recursive"
);

$options = getopt($shortOptions, $longOptions);

//Parse parameters
if (isset($options["help"]) && $argc != 2) {
    echo "Help\n";
    exit(0);
} elseif ((count($argv) !== (count($options) + 1)) && !isset($options["testlist"])) {
    fwrite(STDERR, "ERROR: Bad parameters usage! Use --help.\n");
    exit(10);
} elseif (isset($options["directory"]) && isset($options["testlist"])) {
    fwrite(STDERR, "ERROR: Can not use directory parameter with testlist parameter!\n");
    exit(10);
} else {
    foreach ($options as $option => $value) {
        switch ($option) {
            case "directory":
                $settings["dir"][0] = $value;
                break;
            case "testlist":
                if (!is_array($value)) {
                    $settings["dir"][0] = $value;
                } else {
                    $settings["dir"] = $value;
                }
                break;
            case "recursive":
                $settings["recursively"] = true;
                break;
            case "match":
                $settings["match"] = $value;
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

//Check if parse.php and interpret.py exists
if (!file_exists($settings["parser"])) {
    fwrite(STDERR, "ERROR: Parser file (" . $settings["parser"] . ") does not exist!\n");
    exit(11);
} elseif (!file_exists($settings["interpret"])) {
    fwrite(STDERR, "ERROR: Interpret file (" . $settings["interpret"] . ") does not exist!\n");
    exit(11);
}

//Tests variables
$alreadyTestedFiles = array();
$tests = [];
$testsNumber = 0;
$testsFailed = 0;

//Run tests in every specified directory
foreach ($settings["dir"] as $directory) {
    //Check if directory exists
    if (!file_exists($directory) || !is_dir($directory)) {
        fwrite(STDERR, "ERROR: Tests directory (" . $directory . ") does not exist or is not a directory!\n");
        exit(11);
    }

    //Create Iterators to find .src files iin given locations
    $dir = new RecursiveDirectoryIterator($directory);
    $ite = new RecursiveIteratorIterator($dir);
    $files = new RegexIterator(($settings["recursively"] === true) ? $ite : $dir, "/^.*\.(src)$/", RegexIterator::GET_MATCH);

    //Loop through all .src files
    foreach ($files as $file) {
        $fileName = substr(basename($file[0]), 0, -4);

        //Check file name validity with regexp
        if (@preg_match("/" . $settings["match"] . "/", $fileName)) {
            //Check if same test was not already runned
            if (!in_array($file[0], $alreadyTestedFiles)) {
                //Prepare, run and add test to array
                $tests[] = TestsFactory::prepareAndRun($file[0], $settings);

                //Check if test failed
                if (!$tests[$testsNumber]->getResult()) {
                    ++$testsFailed;
                }

                ++$testsNumber;
                $alreadyTestedFiles[] = $file[0];
            }
        }
    }
}

$time_end = microtime(true);

//Start generating output HTML page
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
    max-width: 900px;
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
    background-color: #2a617c;
    color: #f6f3f7;
    font-size: 26px;
}

.tests tr.head {
    height: 25px;;
    background-color: #2a617c;
    color: #f6f3f7;
    font-size: 22px;
    
}

.tests td {
    border: rgba(0, 0, 0, 0.25) 1px solid;
    text-align: left;
}

.tests tr {
    border: rgba(0, 0, 0, 0.25) 1px solid;
}

.tests td.center {
    text-align: center;
    white-space: nowrap;
    width: 1%;
}

.tests td.nowrap {
    white-space: nowrap;
    width: 1%;
    min-width: 300px;
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

.buttons button {
    cursor: pointer;
    background-color: #497d96; 
    color: #ffffff;
    border: none;
    padding: 15px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
}

.buttons button:hover, .buttons button.active {
    background-color: #2a617c; 
}
</style>
<script type='text/javascript'>
function showTests(type) {
    if (type === 0) {
        [].forEach.call(document.querySelectorAll('.test'), function (el) {
            el.style.display = '';
        });
        
        document.getElementById('showAll').classList.add('active');
        document.getElementById('showFailed').classList.remove('active');
        document.getElementById('showSuccessful').classList.remove('active');
    }
    else if (type === 1) {
        [].forEach.call(document.querySelectorAll('.test.success'), function (el) {
            el.style.display = 'none';
        });
        
        [].forEach.call(document.querySelectorAll('.test.failure'), function (el) {
            el.style.display = '';
        });
        
        document.getElementById('showAll').classList.remove('active');
        document.getElementById('showFailed').classList.add('active');
        document.getElementById('showSuccessful').classList.remove('active');
    }
    else if (type === 2) {
        [].forEach.call(document.querySelectorAll('.test.success'), function (el) {
            el.style.display = '';
        });
        
        [].forEach.call(document.querySelectorAll('.test.failure'), function (el) {
            el.style.display = 'none';
        });
        
        document.getElementById('showAll').classList.remove('active');
        document.getElementById('showFailed').classList.remove('active');
        document.getElementById('showSuccessful').classList.add('active');
    }
}
</script>
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

<div class='buttons'>
    <button id='showAll' class='active' onclick='showTests(0)'>Show all tests</button>
    <button id='showFailed' onclick='showTests(1)'>Show failed tests</button>
    <button id='showSuccessful' onclick='showTests(2)'>Show successful tests</button>
</div>

<table class='tests'>
    <tr class='head'>
        <th>Test</th>   
        <th>Reason</th>  
        <th>Runtime</th> 
        <th>Result</th>  
    </tr>";

foreach ($tests as $test) {
    echo "
    <tr class='test " . (($test->getResult()) ? "success" : "failure") . "'>
        <td>" . $test->getTestName() . "</td>  
        <td class='nowrap'>" . $test->getReason() . "</td>  
        <td class='center'>" . $test->getRuntime() . " ms</td>  
        <td class='center'><strong>" . (($test->getResult()) ? "PASS" : "FAIL") . "</strong></td>  
    </tr>";
}

echo "
</table>
</body>
</html>";