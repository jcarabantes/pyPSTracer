import re
import os
import click
from rich.console import Console

console = Console()

def remove_comments(script_content):
    """Removes comments and empty whitespace lines from a PowerShell script."""
    # Remove multi-line comments <# ... #>
    script_content = re.sub(r'<#.*?#>', '', script_content, flags=re.DOTALL)
    # Remove single-line comments #
    script_content = re.sub(r'#.*', '', script_content)
    # Remove empty or whitespace-only lines
    script_content = "\n".join(line for line in script_content.splitlines() if line.strip())
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

@click.command()
@click.argument('script_path', type=click.Path(exists=True))
@click.argument('function_name', type=str)
@click.argument('output_file', type=click.Path())
def extraction(script_path, function_name, output_file):
    with open(script_path, 'r', encoding='utf-8') as file:
        script_content = file.read()

    script_content_no_comments = remove_comments(script_content)
    function_lines = find_function_lines(script_content_no_comments, function_name)

    if not function_lines:
        console.print(f"[bold red]Error:[/bold red] Function '{function_name}' not found in the script.")
        return

    # Append the function to the output file
    with open(output_file, 'a', encoding='utf-8') as file:
        file.write("\n".join(function_lines) + "\n")

    console.print(f"[bold green]Function '{function_name}' extracted and appended to:[/bold green] {output_file}")

if __name__ == "__main__":
    extraction()
