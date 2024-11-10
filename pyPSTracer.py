import re
import rich_click as click  # Import rich-click instead of click
from rich import print
from rich.console import Console

console = Console()

def remove_comments(script_content):
    """Removes single-line and multi-line comments from a PowerShell script."""
    # Remove multi-line comments <# ... #>
    script_content = re.sub(r'<#.*?#>', '', script_content, flags=re.DOTALL)
    # Remove single-line comments #
    script_content = re.sub(r'#.*', '', script_content)
    return script_content

def find_function_lines(script_content, function_name):
    """Finds all lines of a specific function within the script."""
    # Split content into lines for line-by-line processing
    lines = script_content.splitlines()
    
    # Regular expression to find the function definition
    function_start_pattern = re.compile(rf'^\s*function\s+{re.escape(function_name)}\s*\{{')
    function_lines = []
    in_function = False
    open_braces = 0

    for i, line in enumerate(lines):
        # If we find the start of the function
        if function_start_pattern.match(line):
            in_function = True
            open_braces = 1  # First brace encountered
            function_lines.append(line)
            continue
        
        # If we're inside the function, add the line
        if in_function:
            function_lines.append(line)
            # Count braces to determine the end of the function
            open_braces += line.count("{") - line.count("}")
            if open_braces == 0:
                break  # End of function

    return function_lines

@click.command()
@click.argument('script_path', type=click.Path(exists=True))
@click.argument('target_function', type=str)
def analyze_function(script_path, target_function):
    """Analyzes a specific function in a PowerShell script to identify dependent functions."""
    
    # Read the script content
    with open(script_path, 'r', encoding='utf-8') as file:
        script_content = file.read()
    
    # Remove comments before performing analysis
    script_content_no_comments = remove_comments(script_content)
    
    # Regular expression to detect all functions in the script
    function_pattern = re.compile(r'function\s+([a-zA-Z0-9_\-\.]+)\s*\{?', re.MULTILINE | re.IGNORECASE)
    all_functions = function_pattern.findall(script_content_no_comments)

    # Display all functions found for debugging
    console.print("[bold yellow]Functions found in the file:[/bold yellow]", all_functions)
    
    # Check if the target function is in the file
    if target_function not in all_functions:
        console.print(f"[bold red]Error:[/bold red] The function '{target_function}' was not found in the file.")
        return
    
    # Get all lines of the target function
    target_function_lines = find_function_lines(script_content_no_comments, target_function)
    
    # Display the lines of the target function
    console.print(f"[bold green]Lines of the function '{target_function}':[/bold green]")
    for line in target_function_lines:
        console.print(line)
    
    # Find dependent functions within the target function
    dependent_functions = []
    for func in all_functions:
        # Exclude the target function itself to avoid false positives
        if func != target_function:
            # Check if any of the other functions are called within the lines of the target function
            for line in target_function_lines:
                if re.search(rf'\b{re.escape(func)}\b', line):
                    dependent_functions.append(func)
                    break  # Found it, no need to keep searching this function
    
    # Display the dependent functions found
    if dependent_functions:
        console.print(f"[bold cyan]Dependent functions found in '{target_function}':[/bold cyan] {dependent_functions}")
    else:
        console.print(f"[bold cyan]No dependent functions found in '{target_function}'.[/bold cyan]")

if __name__ == "__main__":
    analyze_function()

