# Description

![Help Image](img/help.png)

pyPSTracer is a Python-based tool designed to trace function calls within a specific PowerShell function, helping you identify dependencies and nested function calls. Useful for extracting specific functions from known PowerShell scripts like **PowerView**, **PowerUp**, and others. This facilitates the use of selected functions in engagements while minimizing AV detection through obfuscation.

## Features

- Parses PowerShell scripts to locate a specific function and trace all internal function calls.
- Ignores comments, both single-line (`#`) and multi-line (`<# ... #>`), ensuring accurate results.
- Provides a list of dependent functions that can be selectively extracted.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/jcarabantes/pyPSTracer/edit/main/README.md
   cd pyPSTracer
   ```

2. Set up a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # For Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Usage

The main script is located at `pyPSTracer.py`. To run it, specify the path to the PowerShell script you want to analyze and the target function name to trace dependencies.

```bash
python pyPSTracer.py <path_to_script> <target_function_name>
```

You can list all detected functions and include verbose to see the code of the specified function:
```bash
python pyPSTracer.py <path_to_script> <target_function_name> -v -l
```

### Example

To trace function calls within the `Get-ModulePrivateFunction` function of a PowerShell script:

```bash
python pyPSTracer.py ExamplePS.psm1 Get-ModulePrivateFunction
```

The output will display all dependent functions that `Get-ModulePrivateFunction` calls within the specified script.

### Known Errors
The function detection regex must be improved probably because some FP still exists

### Possible To Do
Recursion is not implemented and could be nice with a "save file" option