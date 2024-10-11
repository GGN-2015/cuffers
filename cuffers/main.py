import os
import hashlib
import json
from tqdm import tqdm



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