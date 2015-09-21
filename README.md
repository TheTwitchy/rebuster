# rebuster
A regular expression fuzzer, used for blacklist bypasses.

##Description
rebuster is a tool designed to brute-force bypasses for blacklists the rely on regular expressions to detect and/or remove offending input. It does this by taking the regular expression, a list of samples that are known to fail the blacklist, and a  validation command usedto verify the possible output is valid, in addition to several other inputs. rebuster first checks all samples to ensure they meet all requirements, and that the regex and validation command are working as intended. Once everything is verified, rebuster will randomly choose a sample, mutate it randomly by changing some characters in the string, then pass it to the regular expression for evaluation. If the test case fails to bypass the regex, it is thrown away, and the process starts over. If the test case passes the regex, then it is handed to the validation command for sanity checking. If the test case fails parsing here, it is thrown away. If it passes all checks, it is marked as a success, shown to the user, and rebuster exits. rebuster includes a simple example for testing.

rebuster has been developed and tested in Kali Linux, and requires no external libraries or packages.

For any feature requests, bugs, or discussion, please open an issue at https://github.com/TheTwitchy/rebuster

###Inputs
| Name            | Description                                                               |
| :-------------- |:------------------------------------------------------------------------- |
| regex           | The regular expression for which you wish to find a bypass. Generally, this will be something that attempts to detect or remove what may be malicious input.|
| samples file    | A newline-delimited file containing a list of strings used as a starting point to generate a bypass. Every string in this file should fail at bypassing the regex, and should pass validation. |
| validation cmd  | A shell command that takes a test case and attempts to parse it to determine if it is sane. The test sample will be passed via command line, replacing the '##' string in the args. Upon parsing a successful test case, this must return a zero value, and upon failure, this command must return a non-zero value. This command and any related binaries are supplied by the user, and should be a simple file that attempts to emulate or exercise the backend functionality for which a bypass is needed. |
| regex syntax    | The regex syntax. Currently only supports perl-like syntax. | 

##Example 
The rebuster repo includes a simple example to demonstrate the basic usage. The math_val.py script takes a single argument containing a simple expression to be evaluated such as 'mul 1 2 3 4', then returns the result of the expression (24 in this case). The regular expression blocking access to the 'mul' command is '^mul [\d]*'. Samples have been provided for several variations of the 'mul' command, and an answer should normally be located in less that 10k tries.

###Usage
```shell
root@kali:~# rebuster.py -r "^mul [\d]*" -i example/samples.txt -c "example/math_val.py ##"
```

###Test Run
```shell
          _               _            
         | |             | |           
 _ __ ___| |__  _   _ ___| |_ ___ _ __ 
| '__/ _ \ '_ \| | | / __| __/ _ \ '__|
| | |  __/ |_) | |_| \__ \ ||  __/ |   
|_|  \___|_.__/ \__,_|___/\__\___|_|   
                                       
                          version 0.1

rebuster: info: Successfully loaded 3 samples.
rebuster: info: Tested 10000 samples.
rebuster: info: Success! Bypass found, base64 encoded value is 'TXVsIDYgNzUgNzIK'
```
