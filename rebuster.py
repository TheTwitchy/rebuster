#!/usr/bin/env python
VERSION="0.2"

import sys
import signal
import re
import subprocess
import shlex
import os
import random
import base64

#Try to import argparse, not available until Python 2.7
try:
    import argparse
except ImportError:
    sys.stderr.write("error: Failed to import argparse module. Needs python 2.7+.")
    quit()

#Print some info to stdout
def print_info(*args):
    sys.stdout.write("rebuster: info: ")
    sys.stdout.write(" ".join(map(str,args)) + "\n")

#Print an error to stderr
def print_err(*args):
    sys.stderr.write("rebuster: error: ")
    sys.stderr.write(" ".join(map(str,args)) + "\n")


#Simple mutational input generation.
#Input is a list of sample strings, output is a single mutated string
def get_simple_mutation(samples):
    #Select a random sample
    mutational_sample = samples[random.randint(0, len(samples) - 1)]
    mutational_sample = mutational_sample[:-1]

    #Select a random number of mutations on this sample
    num_of_mutations = random.randint(1, 4)
    for i in range(0, num_of_mutations):
        #Select the length of this mutation
        mutation_length = random.randint(1, 4)
        #Select where in the string this mutation will start
        mutation_start = random.randint(0, len(mutational_sample) - 1)
        #Select if this mutation will displace (0) or replace (1) characters
        mutation_type = random.randint(0,1)
        
        #Turn the string into a list (so individual characters can be changed inline)
        mutation_arr = list(mutational_sample)
        
        #If this is a displace mutation, then add enough characters to handle it
        if mutation_type == 0:
            for k in range(0, mutation_length):
            #The 'a' is just a placeholder
                mutation_arr.insert(mutation_start, "a")

        for j in range(0, mutation_length):
            if mutation_start + j >= len(mutation_arr):
                break
            mutation_arr[mutation_start + j] = chr(random.randint(0,255))
    return "".join(mutation_arr)
        

#Given a command with the '##' arg, turn it into a command list and insert the sample appropriately. Return None on error
def build_val_cmd_list(command, sample):
    args = shlex.split(command)
    for i in range(len(args)):
        if args[i] == "##":
            args[i] = sample
            return args
    return None

#Handles early quitters.
def signal_handler(signal, frame):
    print ""
    quit(0)

#A function to signal child proceses not to forward signals (like SIGINT)
def preexec():
    os.setpgrp()

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
    signal.signal(signal.SIGTERM, signal_handler)
    
    #Setup the argparser and all args
    parser = argparse.ArgumentParser(prog="rebuster", description="A regex fuzzer to find blacklist bypasses", epilog="Written by TheTwitchy. For more information, see https://github.com/TheTwitchy/rebuster")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s "+VERSION)
    parser.add_argument("-r", "--regex", help="regex under test", required=True, dest="regex")
    parser.add_argument("-s", "--syntax", help="regex syntax specification", choices=["perl"], default="perl")
    parser.add_argument("-i", "--inputfile", help="input sample filename, one sample per line", type=argparse.FileType("r"), default="-")
    parser.add_argument("-c", "--command", help="validation test command", required=True)
    #parser.add_argument("-o", "--output", help="output filename", type=argparse.FileType("w"), default=sys.stdout)
    parser.add_argument("-n", "--notification", help="notification frequency (0 for none)", type=int, default=10000)
    parser.add_argument("-V", "--verbose", help="more verbose output", action="store_true", default=False)
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

    #Load verbose output flag
    use_verbose_output = args.verbose

    #Load notification frequency
    notification_freq = args.notification
    
    ##Input validation (beyond type checking)
    #Check to make sure all the samples validate via both the regex and the validation command
    for sample in samples:
        #Take the newline off the end
        sample = sample[:-1]

        #Check the sample against the regex under test
        match_obj = re.match(regex, sample)

        if not match_obj:
            print_err("The sample '"+sample+"' does not match the regex '"+regex+"'. All samples should fail to bypass the regex.")
            quit(1);
        
        #Check the sample against the validation program
        cmd_list = build_val_cmd_list(cmds, sample)
        child = subprocess.Popen(cmd_list, stdout=FNULL, stderr=subprocess.STDOUT, preexec_fn = preexec)
        retval = child.wait()
        
        if retval != 0:
            print_err("The sample '"+sample+"' does not pass the validation command. Make sure all samples are valid and parseable.")
            quit(1)
    
    #Now check to make sure that the validation command can fail
    test_sample = "1234567890qwertyuiop!@#$%^&*()0987654321lkjhgdfdsa"
    cmd_list = build_val_cmd_list(cmds, test_sample)
    child = subprocess.Popen(cmd_list, stdout=FNULL, stderr=subprocess.STDOUT, preexec_fn = preexec)
    retval = child.wait()

    if retval == 0:
        print_err("The validation command did not recognize a failure case. Make sure the validation command gives a non-zero return on parse failure.")

    #At this point we are ready to begin testing
    attempt_count = 0
    bypass_found = False

    while not bypass_found:
        attempt_count = attempt_count + 1
        test_sample = get_simple_mutation(samples)
        match_obj = re.match(regex, test_sample)
        if use_verbose_output:
            print_info("Testing the sample '"+test_sample+"'.")
        
        if not match_obj:
            #This means the sample passed through the regex. Send to the validation command to see if it passes that test
            if use_verbose_output:
                print_info("Sample passed regex test. Sending to validation command.")
            cmd_list = build_val_cmd_list(cmds, test_sample)
            try:
                child = subprocess.Popen(cmd_list, stdout=FNULL, stderr=subprocess.STDOUT, preexec_fn = preexec)
                retval = child.wait()
            except TypeError:
                #There was an exception, probably safe to assume the sample failed...
                retval = 1
                if use_verbose_output:
                    print_info("The sample caused the validation command to throw an unhandled exception.")
            
            if retval == 0:
                print_info("Success! Bypass found, base64 encoded value is '" + base64.b64encode(test_sample) + "'")
                bypass_found = True
                quit(0)#Just quit for now, maybe someday we'll want to do some cleanup

            elif use_verbose_output:
                print_info("Sample failed to validate. Regenerating sample.")
        elif use_verbose_output:
            print_info("Sample failed to bypass regex. Regenerating sample.")
        
        if not notification_freq == 0 and (attempt_count % notification_freq) == 0:
            print_info("Tested " + str(attempt_count) + " samples.")


if __name__ == "__main__":
    main()
