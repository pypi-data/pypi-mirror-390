# functuons for printing rendering info

def print_render_info_start(filepath: str) -> None:
    """
    Simple function to print information about rendering start.

    Args:
        filepath (str): The name of the file being rendered. If None, a generic message is printed.

    Returns:
        None
    """
    if filepath is not None:
        print(f"Info: Started rendering '{filepath}'...")
    else:
        print("Info: Started rendering...")


def print_render_info_end(filepath: str, ellapsed_time: float) -> None:
    """
    Simple function to print information about rendering end.

    Args:
        filepath (str): The name of the file being rendered. If None, a generic message is printed.
        ellapsed_time (float): The time taken for rendering in seconds.

    Returns:
        None
    """
    if filepath is not None:
        print(f"Info: Rendering of '{filepath}' completed in {ellapsed_time:.2f} seconds.")
    else:
        print(f"Info: Rendering completed in {ellapsed_time:.2f} seconds.")


# functions for working with files

def read_params_from_yaml(filepath: str) -> dict:
    """
    Reads parameters from a YAML file and returns them as a dictionary.

    Args:
        filepath (str): The path to the YAML file.

    Returns:
        dict: A dictionary containing the parameters read from the YAML file.
    """
    import yaml

    with open(filepath, 'r') as file:
        parameters = yaml.safe_load(file)

    return parameters


def read_source_from_file(filepath: str) -> str:
    """
    Reads source code from a file and returns it as a string.

    Args:
        filepath (str): The path to the source file.

    Returns:
        str: The content of the source file as a string.
    """
    with open(filepath, 'r') as file:
        source_code = file.read()

    return source_code


def write_rendered_to_file(rendered_code: str, filepath: str) -> None:
    """
    Writes the rendered code to a specified file.

    Args:
        rendered_code (str): The rendered code to be written to the file.
        filepath (str): The path to the output file.

    Returns:
        None
    """
    import os
    directory, _ = os.path.split(filepath)
    os.makedirs(directory, exist_ok=True)
    with open(filepath, 'w') as file:
        file.write(rendered_code)
