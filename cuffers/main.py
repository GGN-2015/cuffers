import os
import hashlib
import json
import sys
import string
import random

from tqdm import tqdm



# generate random string for filename
def generate_random_string(length=32):
    characters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


# generate a json file with the name of all the ".bin" file generated
def generate_summary_json_file(filename: str, output_json_path, ls: list):
    json_content = {
        "name": filename,
        "list": ls
    }
    fp = open(output_json_path, "w", encoding="utf-8") # output utf-8 filename
    json.dump(json_content, fp, ensure_ascii=False, indent=4)
    fp.close()



# default hash function is sha256
def default_hash_function(byte_sequence: bytes) -> str:
    sha256_hash = hashlib.sha256()
    sha256_hash.update(byte_sequence)
    return "sha256-" + sha256_hash.hexdigest() # return a string as a file name



# single thread function
# do not load whole file into memory
def save_content_and_return_hash(file_path, output_path, lpos, rpos, hash_function) -> str:

    # input phase
    fp = open(file_path, "rb") # read in binary mode
    fp.seek(lpos)
    binary_content = fp.read(rpos - lpos) # read bytes from file
    fp.close()

    # output phase
    hash_name        = hash_function(binary_content) + ".bin" # all output filenames should end with ".bin"
    output_file_name = os.path.join(output_path, hash_name)
    ofp = open(output_file_name, "wb")
    ofp.write(binary_content)
    ofp.close()

    # return phase: return the name of the hashfile
    return hash_name



# get an available summary file name
def get_summary_file_name(output_path):
    index = 0

    # map index to file name
    def get_filename_by_index(index) -> str:
        return os.path.join(output_path, "summary.%d.json" % index)
    
    # availabel check
    while os.path.isfile(get_filename_by_index(index)):
        index += 1

    # now "get_filename_by_index(index)" is an available summary file name
    return get_filename_by_index(index)



# split a large file into smaller files
# return the count of the smaller file generated
def split_file(file_path, output_path, max_file_size=1048675, hash_function=default_hash_function) -> int:
    assert os.path.isfile(file_path)
    assert os.path.isdir(output_path)

    filename         = os.path.basename(file_path) # get the filename of the file
    bytes_count      = os.path.getsize(file_path)  # get the size of a certain file
    output_json_path = get_summary_file_name(output_path)

    if bytes_count == 0: # do not generate any file if the file is empty
        generate_summary_json_file(filename, output_json_path, [])
        return 0
    
    # this feature will be replaced with a multi-process function
    hash_arr = []
    for i in tqdm(range(0, bytes_count, max_file_size)):
        lpos = i
        rpos = min(lpos + max_file_size, bytes_count)
        hash_arr.append(save_content_and_return_hash(file_path, output_path, lpos, rpos, hash_function))
    
    generate_summary_json_file(filename, output_json_path, hash_arr) # save a summary json file
    return len(hash_arr)



def get_content_by_filename(abs_filepath: str) -> bytes: # load whole file into memory
    fp = open(abs_filepath, "rb")
    content = fp.read()
    fp.close()
    return content



def merge_all_files_listed_in_summary(input_path: str, sum_file: str): # output to the dir of input_path

    # loading phase
    sum_file_path = os.path.join(input_path, sum_file)
    assert os.path.isfile(sum_file_path)
    fp = open(sum_file_path, "r", encoding="utf-8")
    json_content = json.load(fp)
    fp.close()

    # parsing phase
    assert isinstance(json_content, dict)
    name     = json_content.get("name", generate_random_string() + ".bin")
    hash_arr = json_content.get("list", [])
    assert isinstance(hash_arr, list)

    # output content into new file
    output_path  = os.path.dirname(input_path)
    output_file  = os.path.join(output_path, name)
    if os.path.isfile(output_file):
        sys.stderr.write("\033[1;33mwarning\033[0m: cuffers: file \033[1;33m%s\033[0m already exists, operation ignored.\n" % output_file)
        return
    fp = open(output_file, "wb")
    for i in tqdm(range(len(hash_arr))):
        hash_filename = os.path.join(input_path, hash_arr[i])
        fp.write(get_content_by_filename(hash_filename))
    fp.close()



def merge_file_in_dir(input_path): # check summary files and merge them back to whole files
    assert os.path.isdir(input_path)
    summary_fils = [
        filename 
        for filename in os.listdir(input_path) 
        if filename.startswith("summary.") and filename.endswith(".json")
    ]
    for sum_file in summary_fils:
        merge_all_files_listed_in_summary(input_path, sum_file)