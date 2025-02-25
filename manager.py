#!/usr/bin/env python3
import curses
from parser import PythonCellParser
from cell import CellEditor


class EditorManager:
    """
    This manager ties together the Python cell parser and the cell editor.
    It parses a Python source (provided as a string) into cells,
    builds an editor grid (a single-column grid, one cell per row),
    and marks header cells as non-editable.
    """

    def __init__(self, source_code: str):
        self.source_code = source_code
        self.parser = PythonCellParser()
        # Parse the code into a list of cell strings.
        self.cell_list = self.parser.parse(self.source_code)

        # Build a single-column grid: each cell is placed in its own row.
        self.grid_rows = len(self.cell_list)
        self.grid = [[cell] for cell in self.cell_list]

        # Determine editability. For example, mark header cells as non-editable.
        # Here, any cell that starts with "[" or "in " is considered a header.
        def is_header(cell):
            return cell.startswith('[') or cell.startswith('in ')

        self.editable = [
            [False if is_header(cell) else True for cell in row]
            for row in self.grid
        ]

    def run(self):
        def wrapped(stdscr):
            editor = CellEditor(stdscr, grid=self.grid, editable=self.editable)
            editor.run()
        curses.wrapper(wrapped)


if __name__ == "__main__":
    # Sample Python source code for demonstration.
    sample_code = """\
if A:
    A = false
    while TRUE:
         print("hi")
print("done")
"""
    manager = EditorManager(sample_code)
    manager.run()

    # After running the TUI editor, print the final cell values.
    print("\nFinal cell values:")
    for i, row in enumerate(manager.grid):
        print(f"Cell ({i}, 0): {row[0]}")
