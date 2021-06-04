import argparse
import datetime
import sys
import os
from yattag import Doc

def output(results, table_type, ignore_strings, only_strings, skip_lines):

    timestamp = "{0}{1}".format(datetime.datetime.now().hour, datetime.datetime.now().minute)
    file_name = "{0}_{1}.html".format(table_type, timestamp)
    with open(file_name, 'w') as output_file:
        doc, tag, text = Doc().tagtext()
        with tag('html'):
            with tag('style'):
                text("table, th, td { border: 1px solid black; border-spacing: 2px; border-spacing: 2px; font-family: \"Courier New\"}")
                text("#pass { background-color: white }")
                text("#error { background-color: DarkRed; color: White }")
            with tag('body'):
                with tag('h1'):
                    text("{0} TABLE LOOKUP".format(table_type.upper()))
                if ignore_strings:
                    with tag('p'):
                        if type(ignore_strings) == list:
                            val = ",".join(ignore_strings)
                        else:
                            val = ignore_strings
                        text("Filtered to ignore lines with the following: {0}".format(val))
                if only_strings:
                    with tag('p'):
                        if type(only_strings) == list:
                            val = ",".join(only_strings)
                        else:
                            val = only_strings
                        text("Filtered to only contain lines with the following: {0}".format(val))
                if skip_lines:
                    with tag('p'):
                        if type(skip_lines) == list:
                            val = ",".join(skip_lines)
                        else:
                            val = skip_lines
                        text("Filtered to skip the following line numbers: {0}".format(val))
                with tag('table'):
                    with tag('th'):
                        text("Address")
                    with tag('th'):
                        text("Found")
                    with tag('th'):
                        text("Source Line Number")
                    with tag('th'):
                        text("Source Line")
                    with tag('th'):
                        text("Found Line Number")
                    with tag('th'):
                        text("Found Line")
                    for line in results:
                        with tag('tr'):
                            if line["found"] == False:
                                id = "error"
                            else:
                                id = "pass"
                            with tag("td", "id=\"{0}\"".format(id)):
                                text(line["address"])
                            with tag("td", "id=\"{0}\"".format(id)):
                                text(line["found"])
                            with tag("td", "id=\"{0}\"".format(id)):
                                text(line["left_line_number"])
                            if line["found"] == True:
                                with tag("td", "id=\"{0}\"".format(id)):
                                    text(line["left_line"])
                            else:
                                with tag("td", "id=\"{0}\"".format(id)):
                                    text()
                            
                            if line["found"] == True:
                                with tag("td", "id=\"{0}\"".format(id)):
                                    text(line["right_line_number"])
                            else:
                                with tag("td", "id=\"{0}\"".format(id)):
                                    text()
                            if line["found"] == True:
                                with tag("td", "id=\"{0}\"".format(id)):
                                    text(line["right_line"])
                            else:
                                with tag("td", "id=\"{0}\"".format(id)):
                                    text()
                            
        output_file.write(doc.getvalue())


def proceed(line, ignore_strings, only_strings, current_line_number, skip_lines):
    #with each line, we need to determine if it should be processed:
    # ignored due to line content being in the ignore strings
    # ignored due to line content not having an only string value in it
    # ignored due to the line number being in the skip line numbers
    
    proceed = True
    #check if the line contains one of the ignore values
    if ignore_strings:
        for ig_check in ignore_strings:
            #if the ignore line entry is in the left line, ignore this line
            if ig_check in line:
                proceed = False
    #check if the line contains one of the only values
    if only_strings:
        found_only_line = False
        for only_check in only_strings:
            if only_check in line:
                found_only_line = True
        if not found_only_line:
            proceed = False
    #check if the current line number is in the skip lines
    if skip_lines:
        for line_number in skip_lines:
            #if there's a range in the iteration, split it up bottom and top
            if '-' in line_number:
                bottom = line_number.split('-')[0]
                top = line_number.split('-')[1]
                if not current_line_number in range(int(bottom),int(top)):
                    proceed = False
            #if there isn't a range, it's a single number
            else:
                if current_line_number == line_number:
                    proceed = False
    return(proceed)

def lookup(left_content, right_content, ignore_strings, only_strings, skip_lines, lookup_type):
    
    if ignore_strings:
        temp_ignore = ignore_strings.split(',')
        ignore_strings = [x.strip(' ') for x in temp_ignore]
        temp_ignore = None
    elif only_strings:
        temp_only = only_strings.split(',')
        only_strings = [x.strip(' ') for x in temp_only]
        temp_only = None

    #arp table entries go in the order of:
    # Protocol  Address          Age (min)  Hardware Addr   Type   Interface
    # [0]       [1]              [2]        [3]             [4]     [5]

    #mac table entries go in the order of:
    # Vlan    Mac Address       Type        Ports
    # [0]    [1]                [2]         [3]

    if lookup_type == "arp":
        index = 1
    elif lookup_type == "mac":
        index = 1

    line_results = []

    #line number tracking is a bit wonky, as lists start at 0, human line reading starts at 1. So we need to offset the line numbers at the start
    # so that when the iterations start, line number is 1, but the current index of the list is 0.
    left_line_number = 0
    for left_line in left_content:
        left_line_number+=1
        if proceed(left_line, ignore_strings, only_strings, left_line_number, skip_lines):
            
            
            left_line_content = left_line.split()
            left_address = left_line_content[index]
            
            right_line_number = 0
            for right_line in right_content:
                right_address = ""
                message = {
                    "left_line_number":left_line_number,
                    "right_line_number":0,
                    "found":False,
                    "address":left_address,
                    "left_line":left_line,
                    "right_line":right_line
                }

                right_line_number+=1
                if proceed(right_line, ignore_strings, only_strings, right_line_number, skip_lines):
                    right_line_content = right_line.split()
                    right_address = right_line_content[index]

                    #check if there is a match
                    if left_address == right_address:
                        message["right_line_number"] = right_line_number
                        message["found"] = True
                        #no need to check the rest
                        break
            line_results.append(message)

    return(line_results)

def main():
    arg_parser = argparse.ArgumentParser(description="Runs a specialized diff between two files with parameters to provide filter mechanisms, checks the left file to confirm the contents are in the right file.")
    arg_parser.add_argument("-l","--left", type=str, help="Source (left) file to compare from")
    arg_parser.add_argument("-r","--right", type=str, help="Destination (right) file to compare to")
    arg_parser.add_argument("-i","--ignore", type=str, help="List of strings to ignore", default="")
    arg_parser.add_argument("-o","--only", type=str, help="List of strings to only compare if found", default="")
    arg_parser.add_argument("-n","--skip_numbers", type=str, help="List of strings of line numbers to skip", default="")
    arg_parser.add_argument("-t","--table", type=str, help="Table type to lookup: ARP, MAC")

    args = arg_parser.parse_args()

    left_file = args.left
    right_file = args.right
    ignore_strings = args.ignore
    only_strings = args.only
    skip_lines = args.skip_numbers
    table = args.table

    supported_tables = [
        "arp",
        "mac"
    ]

    #check patterns
    should_exit = False
    if not left_file:
        print("Missing source file for comparison.")
        should_exit = True
    if not right_file:
        print("Missing destination file for comparison.")
        should_exit = True
    if ignore_strings and only_strings:
        print("Cannot set both an ignore policy and only policy")
        should_exit = True
    if not os.path.exists(left_file):
        print("Cannot find source file.")
        should_exit = True
    if not os.path.exists(right_file):
        print("Cannot find destination file.")
        should_exit = True
    if not table:
        print("Missing table type specification.")
        should_exit = True
    if not table.lower() in supported_tables:
        print("Table type {0} not currently supported. Supported table types: {1}".format(table, supported_tables))

    if should_exit:
        print("Exiting.")
        sys.exit(1)
    
    #open the left file and read contents to memory
    with open (left_file, 'r') as file_left:
        left_contents = file_left.read().splitlines()
    #open the right file and read contents to memory
    with open(right_file, 'r') as file_right:
        right_contents = file_right.read().splitlines()
   
    results = lookup(left_contents, right_contents, ignore_strings, only_strings, skip_lines, table.lower())
    output(results, table.lower(), ignore_strings, only_strings, skip_lines)

if __name__ == "__main__":
    main()