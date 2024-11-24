import re
import os
import rich_click as click
from rich.console import Console

console = Console()

def banner():
    """Print banner"""
    print("""
                  8888888b.   .d8888b. 88888888888                                       
                  888   Y88b d88P  Y88b    888                                           
                  888    888 Y88b.         888                                           
88888b.  888  888 888   d88P  "Y888b.      888  888d888 8888b.   .d8888b .d88b.  888d888 
888 "88b 888  888 8888888P"      "Y88b.    888  888P"      "88b d88P"   d8P  Y8b 888P"   
888  888 888  888 888              "888    888  888    .d888888 888     88888888 888     
888 d88P Y88b 888 888        Y88b  d88P    888  888    888  888 Y88b.   Y8b.     888     
88888P"   "Y88888 888         "Y8888P"     888  888    "Y888888  "Y8888P "Y8888  888     
888           888                                                                        
888      Y8b d88P                                                                        
888       "Y88P"                                                                         

Simple PS Function Tracer
  Author: Javi Carabantes
""")

def remove_comments(script_content, original_file_path):
    """Removes comments and empty whitespace lines from a PowerShell script,
       saving the result to a new file. Overwrites the file if it already exists."""

    # Generate the new file path
    new_file_path = original_file_path.replace(".ps1", "_no_comments.ps1")
    
    # Inform the user about the saved file
    console.print(f"[bold green]Comments and empty lines removed. The new file is saved as:[/bold green] {new_file_path}")
    if os.path.exists(new_file_path):
        console.print(f"[bold yellow]Note:[/bold yellow] {new_file_path} already exists and will be overwritten.")
    
    # Remove multi-line comments <# ... #>
    script_content = re.sub(r'<#.*?#>', '', script_content, flags=re.DOTALL)
    # Remove single-line comments #
    script_content = re.sub(r'#.*', '', script_content)
    
    # Remove empty or whitespace-only lines
    script_content = "\n".join(line for line in script_content.splitlines() if line.strip())

    # Save the updated script to the file
    with open(new_file_path, 'w', encoding='utf-8') as new_file:
        new_file.write(script_content)
    
    return script_content, new_file_path


def find_function_lines(script_content, function_name):
    """Finds all lines of a specific function within the script."""
    lines = script_content.splitlines()
    function_start_pattern = re.compile(rf'^\s*function\s+{re.escape(function_name)}\s*\{{')
    function_lines = []
    in_function = False
    open_braces = 0

    for line in lines:
        if function_start_pattern.match(line):
            in_function = True
            open_braces = 1
            function_lines.append(line)
            continue
        if in_function:
            function_lines.append(line)
            open_braces += line.count("{") - line.count("}")
            if open_braces == 0:
                break

    return function_lines

def find_functions_with_lines(script_content):
    """Finds all functions in the script and returns their names along with their line numbers."""
    function_pattern = re.compile(
        r'^\s?function\s+([a-zA-Z0-9_\-\.]+)\s*\{?', re.MULTILINE | re.IGNORECASE)
    functions_with_lines = []
    for match in function_pattern.finditer(script_content):
        function_name = match.group(1)
        start_pos = match.start()
        line_number = script_content.count('\n', 0, start_pos) + 1
        functions_with_lines.append((function_name, line_number))
    return functions_with_lines

@click.command(
    context_settings=dict(help_option_names=['-h', '--help']),
    help="""
    Analyzes a PowerShell script to identify functions and dependencies.

    This script processes the provided PowerShell script by:

      - Removing comments.


      - Saving the processed script to a new file named '_no_comments.ps1'.
    """
)
@click.argument('script_path', type=click.Path(exists=True))
@click.argument('target_function', type=str)
@click.option('-v', '--verbose', is_flag=True, help="Enable verbose output - this will show the function code")
@click.option('-l', '--list', is_flag=True, help="List all functions detected in the script")
def analyze_function(script_path, target_function, verbose, list):
    """Analyzes a specific function in a PowerShell script to identify dependent functions."""
    with open(script_path, 'r', encoding='utf-8') as file:
        script_content = file.read()
    script_content_no_comments, new_file_path = remove_comments(script_content, script_path)
    all_functions_with_lines = find_functions_with_lines(script_content_no_comments)
    all_functions = [func[0] for func in all_functions_with_lines]
    if list:
        console.print("[bold yellow]Functions found in the file:[/bold yellow]", all_functions)
    if target_function not in all_functions:
        console.print(
            f"""[bold red]Error:[/bold red] the function '{target_function}' was not found in the file.""")
        return
    target_function_lines = find_function_lines(script_content_no_comments, target_function)
    if verbose:
        console.print(f"""[bold green]Lines of the function '{target_function}':[/bold green]""")
    for line in target_function_lines:
        if verbose:
            console.print(line)
    dependent_functions = []
    for func, line_number in all_functions_with_lines:
        if func != target_function:
            for line in target_function_lines:
                if re.search(rf'\b{re.escape(func)}\b', line):
                    dependent_functions.append((func, line_number))
                    break
    if dependent_functions:
        console.print(f"[bold cyan]Dependent functions found in '{target_function}':[/bold cyan]")
        for func, line in dependent_functions:
            console.print(f" - [bold blue]{func} is declared at[/bold blue] line {line}")
    else:
        console.print(f"""
        [bold cyan]No dependent functions found in '{target_function}'.[/bold cyan]""")

if __name__ == "__main__":
    banner()
    analyze_function()