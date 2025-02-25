#!/usr/bin/env python3
import curses

# Define control-key constants.
CTRL_H = ord("h") & 0x1F  # move left
CTRL_J = ord("j") & 0x1F  # move down
CTRL_K = ord("k") & 0x1F  # move up
CTRL_L = ord("l") & 0x1F  # move right
CTRL_P = ord("p") & 0x1F  # print cell: coordinates & content
CTRL_Q = ord("q") & 0x1F  # quit the editor


class CellEditor:
    def __init__(self, stdscr, grid=None, editable=None, rows=5, cols=5):
        """
        Initialize the CellEditor.

        If a `grid` (list of lists of strings) and an `editable`
        (list of lists of booleans) grid are provided, those will be used.
        Otherwise, a default grid of dimensions rows×cols is created.
        """
        self.stdscr = stdscr

        if grid is not None and editable is not None:
            self.grid = grid
            self.editable = editable
            self.grid_rows = len(grid)
            self.grid_cols = len(grid[0]) if self.grid_rows > 0 else 0
        else:
            self.grid_rows = rows
            self.grid_cols = cols
            self.grid = [["" for _ in range(self.grid_cols)]
                         for _ in range(self.grid_rows)]
            self.editable = [[True for _ in range(self.grid_cols)]
                             for _ in range(self.grid_rows)]

        # Start at the upper-left cell.
        self.cur_row = 0
        self.cur_col = 0

    def run(self):
        # Attempt to set the cursor to visible.
        try:
            curses.curs_set(1)
        except curses.error:
            pass

        while True:
            self.stdscr.clear()

            # Compose and display a header with the current cell info.
            header = f"Editing Cell ({self.cur_row}, {self.cur_col})"
            if not self.editable[self.cur_row][self.cur_col]:
                header += " [NON-EDITABLE]"
            self.stdscr.addstr(0, 0, header)
            self.stdscr.addstr(
                1,
                0,
                "Ctrl+h: left, Ctrl+l: right, Ctrl+j: down, Ctrl+k: up, Ctrl+p: print, Ctrl+q: quit"
            )

            note = ("Type to edit this cell."
                    if self.editable[self.cur_row][self.cur_col]
                    else "This cell is not editable.")
            self.stdscr.addstr(2, 0, note)

            # Display the current cell's content.
            cur_content = self.grid[self.cur_row][self.cur_col]
            self.stdscr.addstr(4, 0, cur_content)
            self.stdscr.move(4, len(cur_content))
            self.stdscr.refresh()

            ch = self.stdscr.getch()

            # Quit.
            if ch == CTRL_Q:
                break

            # Navigation between cells.
            elif ch == CTRL_H and self.cur_col > 0:
                self.cur_col -= 1
            elif ch == CTRL_L and self.cur_col < self.grid_cols - 1:
                self.cur_col += 1
            elif ch == CTRL_J and self.cur_row < self.grid_rows - 1:
                self.cur_row += 1
            elif ch == CTRL_K and self.cur_row > 0:
                self.cur_row -= 1

            # Print the contents of the current cell.
            elif ch == CTRL_P:
                message = (f"Cell ({self.cur_row}, {self.cur_col}): "
                           f"{self.grid[self.cur_row][self.cur_col]}")
                self.stdscr.addstr(6, 0, message)
                self.stdscr.addstr(8, 0, "Press any key to continue...")
                self.stdscr.refresh()
                self.stdscr.getch()

            # Editing: allow modifications only if current cell is editable.
            elif self.editable[self.cur_row][self.cur_col]:
                if ch in (curses.KEY_BACKSPACE, 127, 8):
                    if cur_content:
                        self.grid[self.cur_row][self.cur_col] = cur_content[:-1]
                elif 32 <= ch <= 126:
                    self.grid[self.cur_row][self.cur_col] = cur_content + chr(ch)
            else:
                # Visual feedback for attempts to edit a non-editable cell.
                curses.flash()


if __name__ == "__main__":
    curses.wrapper(lambda stdscr: CellEditor(stdscr).run())
