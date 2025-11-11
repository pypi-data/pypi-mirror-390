#!/usr/bin/env -S uv run python
"""
Transforms Ruff output to a JetBrains compatible format for Jupyter notebooks.

This script takes Ruff linter output, processes it to convert line and column references
from their cell-based format to a JetBrains-compatible intermediary format, and prints
the results. It integrates with JetBrains IDEs when working with Jupyter Notebook files.

The script uses the Ruff concise output, which contains information about files,
cells, and line/column numbers, and adjusts these to JetBrains cell offsets to match
JetBrains' representation of notebooks. It warns users when the specified file is not
a Jupyter `.ipynb` file and expects the `ruff` command-line tool to be available.

Functions:
- transform_ruff_to_jetbrains_compatible_output: Converts Ruff output to the expected
  JetBrains format.
- read_cell: Reads the source content from each cell in the Jupyter notebook.
- compute_jetbrains_cell_offsets: Computes line offsets per Jupyter cell into JetBrains
  representation accounting for blank lines and cell markers.
- main: The entry point of the script that ties together all functionalities.

Use the script directly with Python. This is particularly useful within a configured
JetBrains file watcher for `.ipynb` files.
"""

import re
import subprocess
import sys
import warnings
from itertools import accumulate
from pathlib import Path

import nbformat

LINE_BREAK = r"\r\n|\r|\n"


def transform_ruff_to_jetbrains_compatible_output(
    ruff_output: str, jetbrains_cell_line_offsets: list[int]
) -> str:
    """
    Transforms Ruff output to a JetBrains compatible format.

    The line numbers must be mapped so as to be compatible with JetBrain's intermediate notebook representation.
    The file watcher expression must be able to extract the file path, the line number and the expression.

    We transform the ruff format:

        {file_path}:cell {cell_number}:{cell_line_number}:{ruff_column_number}: {error_code} {message}"

    into the following JetBrains compatible format:

        {file_path}:{jetbrains_line_number}:{jetbrains_column_number}: Ruff({error_code}): {message}"

    NB: The JetBrains and Ruff column numbers are shifted by 1 in their indexing

    :param ruff_output: Ruff linting output.
    :param jetbrains_cell_line_offsets: Cell line offsets for each cell in the JetBrains representation.
    :return: JetBrains compatible output
    """
    RUFF_CONCISE_LINE_OUTPUT_PATTERN = r"^(?P<file_path>.+?):cell (?P<cell>\d+):(?P<line>\d+):(?P<column>\d+): (?P<error_code>[A-Z]\d{3}) (?P<message>.*)$"
    """Transform Ruff output from cell X:line:col format to raw_line:col format."""
    ruff_lines = re.split(LINE_BREAK, ruff_output)

    transformed_lines = [
        f"{match['file_path']}:{jetbrains_cell_line_offsets[int(match['cell']) - 1] + int(match['line'])}:{int(match['column']) - 1}: Ruff ({match['error_code']}): {match['message']}"
        for ruff_line in ruff_lines
        if (match := re.match(RUFF_CONCISE_LINE_OUTPUT_PATTERN, ruff_line))
    ]

    return "\n".join(transformed_lines)


def read_cells(notebook_path: str) -> list[str]:
    """
    Reads the cells of the notebook using the official parser.

    :param notebook_path: File path of the Jupyter Notebook to be read.
    :return: Source content of the cells.
    """
    with open(notebook_path, encoding="utf-8") as notebook_file:
        notebook_content = nbformat.read(notebook_file, as_version=4)

    return [cell.source for cell in notebook_content.cells]


def compute_jetbrains_cell_offsets(
    cell_sources: list[str],
) -> list[int]:
    """
    Computes the JetBrains line offsets for each cell in the notebook.

    JetBrains works with an intermediary representation that differs from the raw
    notebook JSON content.
    Each cell is marked up with a comment line that specifies its type and ends with a
    blank line.

    NB: The JetBrains representation can be inspected by looking at the VCS diffs.

    Example Format:

    .. code-block::

        # %%
        a = "some code"

        # %% md
        # Some Markdown

    :param cell_sources: list of notebook cells.
    :return: Computed cell line offsets for each cell in the JetBrains representation.
    """
    jetbrains_full_cell_line_counts = [
        # + 2 accounts for cell marker line and trailing blank line
        len(re.findall(LINE_BREAK, cell_source)) + 2
        for cell_source in cell_sources
    ]

    # initial=1 accounts for the marker line of the first cell
    return list(accumulate(jetbrains_full_cell_line_counts[:-1], initial=1))


def main():
    if len(sys.argv) == 0:
        warnings.warn(
            "\033[93mMake sure you provide the JetBrains $FilePath$ argument in the file watcher run configurations\033[0m",
            stacklevel=2,
        )

    notebook_path = sys.argv[1]

    if Path(notebook_path).suffix != ".ipynb":
        warnings.warn(
            "\033[93mruff-jupyter-jetbrains is designed to be run on \033[4m.ipynb\033[24m files. Make sure the file watcher is configured for Jupyter files exclusively.\033[0m",
            stacklevel=2,
        )

    result = subprocess.run(
        ["ruff", "check", "--output-format=concise", "--quiet", notebook_path],
        capture_output=True,
        text=True,
    )

    cell_sources = read_cells(notebook_path)
    jetbrains_cell_line_offsets = compute_jetbrains_cell_offsets(cell_sources)
    jetbrains_compatible_output = transform_ruff_to_jetbrains_compatible_output(
        result.stdout, jetbrains_cell_line_offsets
    )

    print(jetbrains_compatible_output, end="")

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
