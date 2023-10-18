import os
import ast
import csv

def get_imports(source_code):
    """Parse the source code to get the imported modules."""
    tree = ast.parse(source_code)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.add(n.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module = node.module.split('.')[0]
                imports.add(module)
    return imports


def is_builtin_module(module):
    """Check if a module is a built-in module."""
    try:
        __import__(module)
        return True
    except ImportError:
        return False

def build_dependency_matrix(project_path, differentiate=True):
    """Build a dependency matrix for a Python project."""
    matrix = {}
    python_files = {}

    # Recursively get all Python files in the project directory
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                
                file_path = os.path.join(root, file)
                print(file_path)
                with open(file_path, 'r') as f:
                    source_code = f.read()
                imports = get_imports(source_code)
                python_files[file_path] = imports

    # Form the dependency matrix
    for file, imports in python_files.items():
        matrix[file] = {}
        for other_file in python_files:
            matrix[file][other_file] = 0

    for file, imports in python_files.items():
        for imported_module in imports:
            if differentiate and is_builtin_module(imported_module):
                continue
            for other_file in python_files:
                if imported_module in other_file:
                    matrix[file][other_file] = 1

    return matrix

def print_matrix(matrix):
    """Prints the dependency matrix in a formatted table."""
    # Get all filenames (sorted for consistent output)
    filenames = sorted(matrix.keys())
    
    # Determine the maximum length of the file basenames
    max_basename_len = max(len(os.path.basename(name)) for name in filenames)
    
    # Determine column width based on the maximum basename length
    col_width = max_basename_len + 2  # Added 2 for some padding
    
    # Print header
    header = " " * col_width
    for name in filenames:
        header += os.path.basename(name).ljust(col_width)  # Left-align the header
    print(header)
    
    # Print each row
    for row in filenames:
        line = os.path.basename(row).ljust(col_width)  # Left-align the row name
        for col in filenames:
            line += str(matrix[row][col]).center(col_width)  # Center the number
        print(line)

def export_matrix_to_csv(matrix, csv_filename):
    """Exports the dependency matrix to a CSV file."""
    filenames = sorted(matrix.keys())
    
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        header = [""] + [os.path.basename(name) for name in filenames]
        writer.writerow(header)
        
        # Write each row
        for row in filenames:
            line = [os.path.basename(row)]
            for col in filenames:
                if row == col:
                    line.append("#")
                elif matrix[row][col] == 1:
                    line.append("X")
                else:
                    line.append("")
            writer.writerow(line)

    print(f"Matrix exported to {csv_filename}.")

# Example usage:
import sys
project_path = sys.argv[1]
matrix = build_dependency_matrix(project_path)
print_matrix(matrix)
export_matrix_to_csv(matrix, project_path.split("/")[-2] + ".csv")