"""Canvas for ASCII rendering.

The Canvas class manages a 2D character grid where boxes are placed.
Boxes come pre-made with borders - the canvas just positions them.
"""

from pydantic import BaseModel, PrivateAttr, model_validator


class Canvas(BaseModel):
    """2D character grid for ASCII rendering.

    Coordinates: x = column (0 = left), y = row (0 = top)
    """

    width: int
    height: int
    _grid: list[list[str]] = PrivateAttr(default_factory=list)

    @model_validator(mode="after")
    def _init_grid(self) -> "Canvas":
        """Initialize the character grid with spaces."""
        self._grid = [[" " for _ in range(self.width)] for _ in range(self.height)]
        return self

    def place_box(self, content: str, x: int, y: int) -> None:
        """Place a pre-made box at the given position.

        Args:
            content: The complete box content (with borders)
            x: Left edge column
            y: Top edge row
        """
        lines = content.split("\n")
        for row_offset, line in enumerate(lines):
            canvas_y = y + row_offset
            if canvas_y < 0 or canvas_y >= self.height:
                continue
            for col_offset, char in enumerate(line):
                canvas_x = x + col_offset
                if canvas_x < 0 or canvas_x >= self.width:
                    continue
                self._grid[canvas_y][canvas_x] = char

    def put_char(self, char: str, x: int, y: int) -> None:
        """Place a single character at the given position.

        Args:
            char: Single character to place
            x: Column
            y: Row
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self._grid[y][x] = char

    def get_char(self, x: int, y: int) -> str:
        """Get the character at the given position.

        Args:
            x: Column
            y: Row

        Returns:
            Character at position, or space if out of bounds
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self._grid[y][x]
        return " "

    def render(self) -> str:
        """Render the canvas to a string.

        Returns:
            Multi-line string representation of the canvas
        """
        # Join rows, stripping trailing spaces from each line
        lines = ["".join(row).rstrip() for row in self._grid]
        # Remove trailing empty lines
        while lines and not lines[-1]:
            lines.pop()
        return "\n".join(lines)
