# cuffers
a python module to split a large file into smaller files.

## install from github release
1. go [https://github.com/GGN-2015/cuffers/releases](https://github.com/GGN-2015/cuffers/releases) and download a `.whl` file.
2. use `pip install cuffers-<version>-py3-none-any.whl` to install the package into your local environment.

## install from pypi

```bash
pip install cuffers
```

## usage

### split file into small files (no more than 1MB)
```bash
python3 -m cuffers <input_file> <output_folder>
```
`<output_folder>` will be automatically generated when you run this command, and all fractions will be saved in that folder along with a file named `summary.<index>.json`.

### merge fractions into a whole file
```bash
python3 -m cuffers --merge <input_folder>
```
a merged file will be generated based on the fractions in `<input_folder>` and the `name` stated in `<input_folder>/summary.<index>.json`. the newly generated file will be placed right outside the folder `<input_folder>`, and if there has already been a file with the same name, the merge operation will be ignored (and you will get a warning output to stderr).
