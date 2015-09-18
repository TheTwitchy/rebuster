#!/usr/bin/env python
VERSION="0.1"

import sys
import signal
import re
import subprocess
import shlex
import os
import random

#Try to import argparse, not available until Python 2.7
try:
    import argparse
except ImportError:
    sys.stderr.write("error: Failed to import argparse module. Needs python 2.7+.")
    quit()


def print_info(*args):
    sys.stdout.write("rebuster: info: ")
    sys.stdout.write(" ".join(map(str,args)) + "\n")

def print_err(*args):
    sys.stderr.write("rebuster: error: ")
    sys.stderr.write(" ".join(map(str,args)) + "\n")


#Simple mutational input generation
def get_simple_mutation(samples):
    #Select a random sample
    mutational_sample = samples[random.randint(0, len(samples) - 1)]
    
    #Select a random number of mutations on this sample
    num_of_mutations = random.randint(1, 10)
    for i in range(0, num_of_mutations):
        #Select the length of this mutation
        mutation_length = random.randint(1,4)
        
        

#Given a command with the '##' arg, turn it into a command list and insert the sample appropriately. Return None on error
def build_val_cmd_list(command, sample):
    args = shlex.split(command)
    for i in range(len(args)):
        if args[i] == "##":
            args[i] = sample
            return args
    return None

def signal_handler(signal, frame):
    print ""
    quit()

#Because every real hacker tool needs an awesome splash screen
#Courtesy of patorjk.com.
def print_intro():
    print("          _               _            \n" \
"         | |             | |           \n" \
" _ __ ___| |__  _   _ ___| |_ ___ _ __ \n" \
"| '__/ _ \ '_ \| | | / __| __/ _ \ '__|\n" \
"| | |  __/ |_) | |_| \__ \ ||  __/ |   \n" \
"|_|  \___|_.__/ \__,_|___/\__\___|_|   \n" \
"                                       \n" \
"                          version " + VERSION + "\n")


def main():
    #Signal handler to catch CTRL-C (quit immediately)
    signal.signal(signal.SIGINT, signal_handler)
    
    #Setup the argparser and all args
    parser = argparse.ArgumentParser(prog="rebuster", description="A regex fuzzer to find blacklist bypasses", epilog="Written by TheTwitchy. For more information, see https://github.com/TheTwitchy/rebuster")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s "+VERSION)
    parser.add_argument("-r", "--regex", help="regex under test", required=True, dest="regex")
    parser.add_argument("-s", "--syntax", help="regex syntax specification", choices=["perl"], default="perl")
    parser.add_argument("-i", "--inputfile", help="input sample filename, one sample per line", type=argparse.FileType("r"), default="-")
    parser.add_argument("-c", "--command", help="validation test command", required=True)
    #parser.add_argument("-o", "--output", help="output filename", type=argparse.FileType("w"), default=sys.stdout)
    args = parser.parse_args()
    
    print_intro()

    #Load the regex under test
    regex = args.regex

    #Load the syntax
    syntax = args.syntax

    #Load the samples from the input file
    samples = args.inputfile.readlines()
    if (len(samples) < 1):
        print_err("The input file has no samples.")
        quit(1)
    print_info("Successfully loaded " + str(len(samples)) + " samples.")
    
    #Load the validation command
    cmds = args.command
    if "##" not in cmds:
        print_err("Validation command is missing the test sample flag '##'.")
        quit(1)
    FNULL = open(os.devnull, "w")

    #Load the output file
    #output = args.output
    
    ##Input validation (beyond type checking)
    #Check to make sure all the samples validate via both the regex and the validation command
    for sample in samples:
        #Take the newline off the end
        sample = sample[:-1]

        #Check the sample against the regex under test
        match_obj = re.match(regex, sample)

        if match_obj:
            print_err("The sample '"+sample+"' matches the regex '"+regex+"'. All samples should fail to bypass the regex.")
            quit(1);
        
        #Check the sample against the validation program
        cmd_list = build_val_cmd_list(cmds, sample)
        retval = subprocess.call(cmd_list, stdout=FNULL, stderr=subprocess.STDOUT)
        
        if retval != 0:
            print_err("The sample '"+sample+"' does not pass the validation command. Make sure all samples are valid and parseable.")
            quit(1)
    
    #Now check to make sure that the validation command can fail
    test_sample = "1234567890qwertyuiop!@#$%^&*()0987654321lkjhgdfdsa"
    cmd_list = build_val_cmd_list(cmds, test_sample)
    retval = subprocess.call(cmd_list, stdout=FNULL, stderr=subprocess.STDOUT)

    if retval == 0:
        print_err("The validation command did not recognize a failure case. Make sure the validation command gives a non-zero return on parse failure.")

    #At this point we are ready to begin testing
    get_simple_mutation(samples)

if __name__ == "__main__":
    main()
