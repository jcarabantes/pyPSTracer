import re
import os
# import click
import rich_click as click
from rich.console import Console

console = Console()

def remove_comments(script_content):
    """Removes comments and empty whitespace lines from a PowerShell script."""
    script_content = re.sub(r'<#.*?#>', '', script_content, flags=re.DOTALL)  # Multi-line comments
    script_content = re.sub(r'#.*', '', script_content)  # Single-line comments
    script_content = "\n".join(line for line in script_content.splitlines() if line.strip())  # Remove empty lines
    return script_content

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

def extract_function_with_dependencies(script_content, target_function, verbose=False):
    """Extracts the target function and all its dependencies."""
    all_functions_with_lines = find_functions_with_lines(script_content)
    all_functions = {func[0]: func[1] for func in all_functions_with_lines}

    if target_function not in all_functions:
        console.print(f"[bold red]Error:[/bold red] The function '{target_function}' was not found.")
        return []

    extracted_functions = set()
    functions_to_process = [target_function]
    extracted_lines = []

    while functions_to_process:
        current_function = functions_to_process.pop()
        if current_function in extracted_functions:
            continue

        current_function_lines = find_function_lines(script_content, current_function)
        if not current_function_lines:
            console.print(f"[bold yellow]Warning:[/bold yellow] Function '{current_function}' not found.")
            continue

        extracted_lines.extend(current_function_lines)
        extracted_lines.append("")  # Add a blank line for readability
        extracted_functions.add(current_function)

        # Check for dependencies in the current function
        for func in all_functions:
            if func != current_function:
                for line in current_function_lines:
                    if re.search(rf'\b{re.escape(func)}\b', line):
                        functions_to_process.append(func)
                        break

    if verbose:
        console.print(f"[bold cyan]Functions detected and extracted:[/bold cyan]")
        for func in extracted_functions:
            console.print(f" - [bold blue]{func}[/bold blue]")

    return extracted_lines

@click.command(
    context_settings=dict(help_option_names=['-h', '--help']),
    help="""
    Analyzes a PowerShell script to identify a function and its nested ones.
    It extracts them in a single file.
        """
)
@click.argument('script_path', type=click.Path(exists=True))
@click.argument('function_name', type=str)
@click.argument('output_file', type=click.Path())
@click.option('-v', '--verbose', is_flag=True, help="Enable verbose output (lists detected functions).")
def main(script_path, function_name, output_file, verbose):
    """
    Extracts a function and its dependencies from a PowerShell script and saves to an output file.
    """
    with open(script_path, 'r', encoding='utf-8') as file:
        script_content = file.read()

    # Remove comments and whitespace
    script_content_no_comments = remove_comments(script_content)

    # Extract the function and its dependencies
    extracted_lines = extract_function_with_dependencies(script_content_no_comments, function_name, verbose)

    if not extracted_lines:
        console.print(f"[bold red]Error:[/bold red] No functions extracted.")
        return

    # Save to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("\n".join(extracted_lines))

    console.print(f"[bold green]Function '{function_name}' and its dependencies extracted to:[/bold green] {output_file}")

if __name__ == "__main__":
    main()
