import sys
import os

from .main import split_file
from .main import merge_file_in_dir



# check: shell parameters count
if len(sys.argv) != 3:
    sys.stderr.write("usage: python3 -m cuffers  <file> <output_path>\n")
    sys.stderr.write("       python3 -m cuffers --merge <input_path>\n")
    exit(1)



# read the parameters from sys.argv
intput_path = sys.argv[1] #  input_path: should be a file
output_path = sys.argv[2] # output_path: should be a directory



# run merge logic
if intput_path == "--merge":
    if not os.path.isdir(output_path):
        sys.stderr.write("cuffers: input folder not exists: %s\n" % output_path)
        exit(1)
    merge_file_in_dir(output_path)
    exit(0)



# check: input file available
if not os.path.isfile(intput_path):
    sys.stderr.write("cuffers: input file not exists: %s\n" % intput_path)
    exit(1)



# create output folder if it is not exist
fail = False
try:
    if not os.path.isdir(output_path):
        os.makedirs(output_path, exist_ok=True)
except:
    sys.stderr.write("cuffers: create output folder failed: %s\n" % intput_path)
    fail=True
if fail: # quit if can not create output folder
    exit(1)



# todo: check create file is enabled in output_path



split_file(intput_path, output_path) # split the file into smaller files