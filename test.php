<?php
header("Content-Type: text/html; charset=UTF-8");

class Test
{
    private $files;
    private $data;
    private $settings;
    private $runtime;
    private $reason;
    private $passed;

    public function __construct($files, $data, $settings)
    {
        $this->files = $files;
        $this->data = $data;
        $this->settings = $settings;
        $this->run();
    }

    private function run()
    {
        $test_start = microtime(true);

        if ($this->data["exitcode"] != 0) {
            $results = $this->compareExitCode();
        } else {
            $results = $this->compareOutput();
        }

        $test_end = microtime(true);

        $this->runtime = round(($test_end - $test_start) * 100, 2);
        $this->passed = $results[0];
        $this->reason = $results[1];
    }

    private function compareOutput()
    {
        $result = array();

        exec("php5.6 " . $this->settings["parser"] . " < " . $this->files["src"] . " 2> /dev/null", $out, $exitCode);
        $xml = implode("\n", $out);

        if ($exitCode != 0) {
            $result[0] = false;
            $result[1] = "Parser ended with exit code " . $exitCode . " (expected 0).";
            return $result;
        }

        $temp = tmpfile();
        fwrite($temp, $xml);
        fseek($temp, 0);
        $tempData = stream_get_meta_data($temp);

        exec("python3.6 " . $this->settings["interpret"] . " --source=\"" . $tempData["uri"] . "\" ", $outInterpret, $exitCode);
        file_put_contents($tempData["uri"], $outInterpret);

        if ($exitCode != 0) {
            $result[0] = false;
            $result[1] = "Interpret ended with exit code " . $exitCode . " (expected 0).";
            return $result;
        }

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

    private function compareExitCode()
    {
        $result = array();

        if ($this->data["exitcode"] == 21) {
            exec("php5.6 " . $this->settings["parser"] . " < " . $this->files["src"] . " 2> /dev/null", $null, $exitCode);

            if ($exitCode == 21) {
                $result[0] = true;
                $result[1] = "Parser ended with expected exit code (21).";
            } else {
                $result[0] = false;
                $result[1] = "Parser ended with exit code " . $exitCode . " (expected 21).";
            }
        } else {
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

    public function getTestName()
    {
        $info = pathinfo ($this->files["src"]);
        $name = $info["filename"];
        $name = str_replace("_", " ", $name);
        return ucfirst($name);
    }

    public function getTestLocation()
    {
        return $this->files["src"];
    }

    public function getResult()
    {
        return $this->passed;
    }

    public function getReason()
    {
        return $this->reason;
    }

    public function getRuntime()
    {
        return $this->runtime;
    }
}

class TestsFactory
{
    public static function runTest($srcFile, $settings)
    {
        $filesPath = substr($srcFile, 0, -4);

        $files = array();
        $files["src"] = $srcFile;
        $files["out"] = $filesPath . ".out";
        $files["in"] = $filesPath . ".in";
        $files["rc"] = $filesPath . ".rc";

        $data = array();
        $data["output"] = self::getTestFileContent($filesPath . ".out", null);
        $data["stdin"] = self::getTestFileContent($filesPath . ".in", null);
        $data["exitcode"] = self::getTestFileContent($filesPath . ".rc", 0);

        return new Test($files, $data, $settings);
    }

    private static function getTestFileContent($file, $default)
    {
        if (!file_exists($file)) {
            $newFile = fopen($file, "w");

            if ($default != null) {
                fwrite($newFile, $default);
            }

            fclose($newFile);
            return ($default != null) ? $default : "";
        } else {
            return file_get_contents($file);
        }
    }
}

$time_start = microtime(true);

$settings = array(
    "dir" => getcwd(),
    "recursively" => false,
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
    "recursive"
);

$options = getopt($shortOptions, $longOptions);
if (isset($options["help"]) && $argc != 2) {
    echo "Help\n";
    exit(0);
} elseif (count($argv) !== (count($options) + 1)) {
    fwrite(STDERR, "ERROR: Bad parameters usage! Use --help.\n");
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
    fwrite(STDERR, "ERROR: Tests directory (" . $settings["dir"] . ") does not exist or isn not a directory!\n");
    exit(11);
} elseif (!file_exists($settings["parser"])) {
    fwrite(STDERR, "ERROR: Parser file (" . $settings["parser"] . ") does not exist!\n");
    exit(11);
} elseif (!file_exists($settings["interpret"])) {
    fwrite(STDERR, "ERROR: Interpret file (" . $settings["interpret"] . ") does not exist!\n");
    exit(11);
}

$dir = new RecursiveDirectoryIterator($settings["dir"]);
$ite = new RecursiveIteratorIterator($dir);
$files = new RegexIterator(($settings["recursively"] === true) ? $ite : $dir, "/^.*\.(src)$/", RegexIterator::GET_MATCH);

$tests = [];
$testsNumber = 0;
$testsFailed = 0;

foreach ($files as $file) {
    $tests[] = TestsFactory::runTest($file[0], $settings);

    if (!$tests[$testsNumber]->getResult()) {
        ++$testsFailed;
    }

    ++$testsNumber;
}

$time_end = microtime(true);

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