import re
import copy
import time

from .util_funcs import print_render_info_start, print_render_info_end


KSV_METAS: set[str] = {"if", "elif", "else", "for", "while", "with", "match", "case", "universal_indent_down",}
KSV_METAS_INDENT_UP: set[str] = {"if", "for", "while", "with", "match", "case",}
KSV_METAS_INDENT_STAY: set[str] = {"elif", "else",}
KSV_METAS_INDENT_DOWN: set[str] = {"universal_indent_down",}


def check_line_for_meta(line: str) -> str | None:
    if re.match(r"\s*<\$\s*if.*\$>.*", line):     # ksv if
        return "if"
    if re.match(r"\s*<\$\s*elif.*\$>.*", line):   # ksv elif
        return "elif"
    if re.match(r"\s*<\$\s*else.*\$>.*", line):   # ksv else
        return "else"
    if re.match(r"\s*<\$\s*for.*\$>.*", line):    # ksv for
        return "for"
    if re.match(r"\s*<\$\s*while.*\$>.*", line):  # ksv while
        return "while"
    if re.match(r"\s*<\$\s*with.*\$>.*", line):   # ksv with
        return "with"
    if re.match(r"\s*<\$\s*match.*\$>.*", line):  # ksv match
        return "match"
    if re.match(r"\s*<\$\s*case.*\$>.*", line):   # ksv case
        return "case"
    if re.match(r"\s*<\$\s*end.*\$>.*", line):    # ksv universal_indent_down ('end*' keyword)
        return "universal_indent_down"
    return None


def render_single_line(line: str, variables :dict) -> str:
    inline_templates: list[str] = re.findall(r"</.*?/>", line)
    exec_locals: dict = variables
    templated_line: str = copy.copy(line) + '\n'

    if len(inline_templates) > 0:
        for inline_template in inline_templates:
            exec(f"templated_line = str({inline_template[3:-3]})", locals=exec_locals)
            templated_line = templated_line.replace(inline_template, exec_locals['templated_line'])

    return templated_line


def meta_to_py_line(line: str) -> str:
    converted_line: str = copy.copy(line)

    beginning_meta: list[str] = re.findall(r"^\s*<\$\s*", line)
    trailing_meta: list[str] = re.findall(r"\s*\$>.*$", line)

    converted_line = converted_line.replace(beginning_meta[0], '')
    converted_line = converted_line.replace(trailing_meta[0], '')

    return converted_line


def templated_to_executable(content: str) -> str:
    all_lines: list[str] = content.split('\n')[:-1]
    executable_content: str = "KSV_RENDERED_CONTENT = ''\n"
    depth_level: int = 0

    for line in all_lines:
        meta = check_line_for_meta(line)
        if meta is not None:
            if meta in KSV_METAS_INDENT_UP:
                executable_content += ' ' * 4 * depth_level
                executable_content += meta_to_py_line(line) + '\n'
                depth_level += 1

            elif meta in KSV_METAS_INDENT_STAY:
                executable_content += ' ' * 4 * ( depth_level - 1 )
                executable_content += meta_to_py_line(line) + '\n'

            if meta in KSV_METAS_INDENT_DOWN:
                depth_level -= 1
        else:
            executable_content += ' ' * 4 * depth_level
            executable_content += f"KSV_RENDERED_CONTENT += render_single_line('''{line}''', locals())\n"

    return executable_content


def execute_content(content: str, variables: dict) -> str:
    exec_locals: dict = variables
    exec(content, locals=exec_locals)
    rendered_content: str = exec_locals['KSV_RENDERED_CONTENT']
    return rendered_content


def render(content: str, variables: dict, logging: bool=True, filepath: str=None) -> str:
    """
    Render the given content with KaravaiSV templating engine with the provided python variables.

    This function basically is the main entry point for rendering content using the KaravaiSV templating engine.
    It takes content via a python string and renders any KaravaiSV templating syntax found within it using the provided python variables.

    Args:
        content (str): The content to be rendered.
        variables (dict): A dictionary of variables to be used in the rendering process.
        logging (bool, optional): If True, logs the rendering process and time taken. Defaults to True.
        filepath (str, optional): The path to the file being rendered, used for logging purposes. Defaults to None. Makes sense only if logging is True.

    Returns:
        str: The rendered content as a string.
    """
    if logging:
        start_time: float = time.time()
        print_render_info_start(filepath)

    executable_content: str = templated_to_executable(content)
    rendered_content: str = execute_content(executable_content, variables)

    if logging:
        end_time: float = time.time()
        ellapsed_time: float = end_time - start_time
        print_render_info_end(filepath, ellapsed_time)

    return rendered_content
