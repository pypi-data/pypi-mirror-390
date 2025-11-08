from __future__ import annotations

import textwrap

# https://ipython.readthedocs.io/en/8.27.0/sphinxext.html#directive-and-options
# admonition directive: https://sphinx-immaterial.readthedocs.io/en/latest/admonitions.html#admonition-directive
# .. code-example:: title\n    ::collapsible:: open


def py_to_rst(
    lines: str | list[str],
) -> str:
    if isinstance(lines, str):
        lines = lines.splitlines()

    rst_text = ""

    i = 0

    while i < len(lines):
        # line = lines[i].rstrip()

        i, rst_text = _get_rst_text(i=i, lines=lines, rst_text=rst_text)

    return rst_text


def _get_rst_text(i: int, lines: list[str], rst_text: str, *, indent: int = 0) -> tuple[int, str]:
    while i < len(lines):
        line = lines[i].rstrip()

        if line.startswith("# END"):
            i += 1

        elif line.startswith("# TABS"):
            name = line.replace("# TABS", "").strip()

            content, sum_idx = _process_tabs(
                i=i,
                lines=lines,  # all the lines
                name=name,
            )
            rst_text += content

            i += sum_idx

        elif line.startswith('"""'):
            text_block, sum_idx = _extract_text_block(lines=lines, start_index=i)

            rst_text += text_block + "\n\n"

            i += sum_idx

        # title symbol: -
        elif line.startswith("# -"):
            title_text, _ = _process_line(line, "# -")
            if len(title_text):
                rst_text += title_text + "\n" + "-" * len(title_text) + "\n\n"

            i += 1

        # title symbol: *
        elif line.startswith("# *"):
            sub_title_text, _ = _process_line(line, "# *")

            if len(sub_title_text):
                rst_text += sub_title_text + "\n" + "*" * len(sub_title_text) + "\n\n"

            i += 1

        elif line.startswith("# ="):
            sub_title_text, _ = _process_line(line, "# =")

            if len(sub_title_text):
                rst_text += sub_title_text + "\n" + "=" * len(sub_title_text) + "\n\n"

            i += 1

        # title symbol: ~
        elif line.startswith("# %%"):
            sub_sub_title_text, _ = _process_line(line, "# %%")

            if len(sub_sub_title_text):
                rst_text += sub_sub_title_text + "\n" + "~" * len(sub_sub_title_text) + "\n\n"

            i += 1

        else:
            if not lines[i].strip():
                i += 1
                continue

            # the i now is at the end of the code block
            i, code_block = _process_code_block(i=i, lines=lines)

            rst_text += code_block

    if indent:
        rst_text = textwrap.indent(rst_text, " " * indent)

    return i, rst_text


# ----------------------------------------------------------------------

# CLODE_BLOCKS = {
#     "simple": '.. ipython:: python\n\n',
#     "block": '.. code-example::\n\n    .. ipython:: python\n\n',
#     # "collapsible": '.. code-example::\n    :collapsible:\n\n    .. ipython:: python\n\n',
#     # "collapsible_open": '.. code-example::\n    :collapsible: open\n\n    .. ipython:: python\n\n',
# }


def _process_code_block(i: int, lines: list[str], indentation: int = 0) -> tuple[int, str]:
    code_block = ""

    stop_if = lambda x: (  # noqa: E731
        not lines[x].startswith('"""')
        and not lines[x].startswith("# -")
        and not lines[x].startswith("# *")
        and not lines[x].startswith("# %%")
        and not lines[x].startswith("# TAB")
        and not lines[x].startswith("# END")
    )

    while i < len(lines) and stop_if(i):
        # if lines[i].startswith('# .. unnest'):
        #
        #     indentation -= 4
        #     i += 1
        #     continue

        line = lines[i].rstrip()

        if line.startswith("# .."):
            # .. code-example:: title\n    ::collapsible:: open

            text = process_directive_options(line.lstrip("# "), indentation=indentation)

            code_block += textwrap.indent(text, " " * indentation) + "\n\n"

            indentation += 4
            i += 1

            continue  # skip the string ..

        if line.startswith("# loop-out"):
            # todo: raise error if not an integer at the end
            n = int(line.split()[-1])
            indentation -= 4 * n
            i += 1

            continue

        if line.startswith("'''"):
            text_block, sum_idx = _extract_text_block(lines=lines, start_index=i, symbol="'''")

            text_block = textwrap.indent(text_block, " " * indentation)

            code_block += text_block + "\n"

            i += sum_idx

        else:
            code_line = textwrap.indent(line, " " * indentation)

            code_block += code_line + "\n"
            i += 1
    # the i now is at the end of the code block
    return i, code_block


def process_directive_options(line: str, indentation: int) -> str:
    # Find the content inside square brackets
    start = line.find("[")
    end = line.find("]")

    if start == -1 or end == -1:
        return line

    # Extract the content inside brackets and split by commas
    bracket_content = line[start + 1 : end]
    items_list = [item.strip() for item in bracket_content.split(",")]

    # Remove the bracketed content from the original line
    cleaned_line = line[:start].strip() + line[end + 1 :].strip()

    for i in items_list:
        # cleaned_line += f"\n{' ' * (indentation + 4)}{i}"
        cleaned_line += f"\n{' ' * 4}{i}"

    return cleaned_line


# ----------------------------------------------------------------------


def _process_tabs(i: int, lines: list[str], name: str) -> tuple[str, int]:
    """
    https://jbms.github.io/sphinx-immaterial/content_tabs.html#ref-this-tab-set
    """

    tab_lines, sum_idx = extract_until_tab_end(lines=lines[i:])

    sections = extract_sections(lines=tab_lines)

    tabs_block = ".. md-tab-set::\n"
    tabs_block += " " * 4 + ":class: custom-tab-set-style\n"
    if name:
        tabs_block += " " * 4 + f":name: {name}\n"

    tabs_block += "\n"
    for title, section_lines in sections.items():
        title = title.rstrip()

        tabs_block += " " * 4 + f".. md-tab-item:: {title}\n\n"

        _, content = _get_rst_text(i=0, lines=section_lines, rst_text="", indent=8)

        tabs_block += content

    return tabs_block, sum_idx


def extract_until_tab_end(lines: list[str]) -> tuple[list[str], int]:
    for i, line in enumerate(lines):
        if line.strip().endswith("END"):
            return lines[:i], i + 1

    # If no terminating line is found, return the whole list and the index beyond the last element
    return lines, len(lines)


def extract_sections(lines: list[str]) -> dict:
    """
    Splits a list of strings into chunks based on lines starting with '# %%'.
    Each chunk's key is obtained from the line following '# %%', and the value is a list of strings up to the next '# %%'.

    Parameters:
        lines (list[str]): The list of string lines to process.

    Returns:
        dict: A dictionary where each key is a title extracted from a line starting with '# %%',
              and each value is a list of lines up to the next '# %%'.
    """

    def _process_line(line, marker):
        if line.startswith(marker):
            return line[len(marker) :].lstrip(), True
        return line, False

    sections = {}
    current_key = None
    current_chunk: list = []

    for line in lines:
        line_processed, is_marker = _process_line(line, "# %%")
        if is_marker:
            if current_key is not None:
                sections[current_key] = current_chunk
            current_key = line_processed
            current_chunk = []
        else:
            current_chunk.append(line)

    # Adding the last chunk if it exists
    if current_key is not None:
        sections[current_key] = current_chunk

    return sections


# ----------------------------------------------------------------------


def _process_line(line, marker):
    if line.startswith(marker):
        return line[len(marker) :].lstrip(), True
    return line, False


def _extract_text_block(
    lines: list[str], start_index: int, symbol: str = '"""'
) -> tuple[str, int]:
    lines = lines[start_index:]

    end_index = 0
    while end_index < len(lines):
        if symbol in lines[end_index]:
            break
        end_index += 1

    lines = lines[: end_index + 1]

    # Extract the text block lines, excluding the initial and final `"""`.
    text_block_str = "".join(lines).strip().strip(symbol)

    return text_block_str, end_index + 1
