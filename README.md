# file-diff

Provides a file diff with parameters to support dynamic filtering

## requires

python3 and the installed requirements.txt file

Download python3 from [here](https://www.python.org/downloads/)

Once python3 is installed, use pip to install the dependencies:

`python3 -m pip install -r requirements.txt`

From that, you can run the command as specified below.

### required attributes

- --left: the source file to compare from
- --right: the destination file to compare against
- --table: the table type lookup (arp/mac)

### optional attributes

- --help: gets the help menu
- --ignore: a comma separated set of strings to use if you want to ignore lines from being tested
- --only: a comma separated set of strings to use if you want to only test lines with the specified values
- --skip_numbers: a comma separated set of numbers to include which lines you want to skip in both files, eg.: --skip_numbers 1,4,5-10,12

### examples

Compare two files that are arp tables:

```txt
python3 search_tool.py --left <arp_file> --right <arp_file_2> --table arp
```

This will generate an HTML file in your directory that contains a report of the found/missing ARP entries.