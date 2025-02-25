#!/usr/bin/env python3

class PythonCellParser:
    """
    A simple parser that converts Python code into a list of cells by using
    indentation to determine nesting. This version preserves the original
    content of each line (including quotes, parentheses, colons, etc.).

    For example, given the code:

        if A:
            A = false
            while TRUE:
                 print("hi")
        print("done")

    the parser produces cells like:

        [if A:]
        in if A:, A = false
        in if A:, while TRUE:
        in in while TRUE:, print("hi")
        print("done")
    """

    def __init__(self, indent_unit=4):
        self.indent_unit = indent_unit

    def parse(self, code: str):
        lines = code.splitlines()
        cells = []
        # Stack holds tuples: (indentation level, header line content)
        stack = []

        for line in lines:
            if not line.strip():
                continue  # Skip blank lines

            # Determine the current indentation level.
            indent = len(line) - len(line.lstrip())
            content = line.lstrip()  # Preserve the original line content

            # Check if this is a header line (ends with ":")
            is_header = content.endswith(":")

            # Pop headers from the stack if their indent is greater than or equal
            # to the current line. This determines the current nesting structure.
            while stack and stack[-1][0] >= indent:
                stack.pop()

            if is_header:
                # Format the cell for a header.
                if not stack:
                    cell = f"[{content}]"
                else:
                    parent_chain = ", ".join(item[1] for item in stack)
                    cell = f"in {parent_chain}, {content}"
                # Push this header into the stack.
                stack.append((indent, content))
                cells.append(cell)
            else:
                # Format a non-header cell.
                if stack:
                    chain = ", ".join("in " + item[1] for item in stack)
                    cell = f"{chain}, {content}"
                else:
                    cell = content
                cells.append(cell)

        return cells


if __name__ == "__main__":
    sample_code = """\
if A:
    A = false
    while TRUE:
         print("hi")
print("done")
"""
    parser = PythonCellParser()
    for cell in parser.parse(sample_code):
        print(cell)
