"""Tests for Canvas class."""

import pytest

from visualflow.render import Canvas


class TestCanvasCreation:
    """Tests for Canvas creation."""

    def test_canvas_creation(self) -> None:
        """Canvas can be created with dimensions."""
        canvas = Canvas(width=80, height=24)
        assert canvas.width == 80
        assert canvas.height == 24

    def test_canvas_initialized_with_spaces(self) -> None:
        """Canvas is initialized with space characters."""
        canvas = Canvas(width=5, height=3)
        for y in range(3):
            for x in range(5):
                assert canvas.get_char(x, y) == " "


class TestCanvasPutChar:
    """Tests for put_char method."""

    def test_put_char_valid_position(self) -> None:
        """put_char places character at valid position."""
        canvas = Canvas(width=10, height=10)
        canvas.put_char("X", 5, 3)
        assert canvas.get_char(5, 3) == "X"

    def test_put_char_out_of_bounds_ignored(self) -> None:
        """put_char ignores out of bounds positions."""
        canvas = Canvas(width=10, height=10)
        canvas.put_char("X", -1, 0)  # No error
        canvas.put_char("X", 10, 0)  # No error
        canvas.put_char("X", 0, -1)  # No error
        canvas.put_char("X", 0, 10)  # No error


class TestCanvasPlaceBox:
    """Tests for place_box method."""

    def test_place_box_simple(self) -> None:
        """place_box places a simple box."""
        canvas = Canvas(width=20, height=10)
        box = "+---+\n| A |\n+---+"
        canvas.place_box(box, x=2, y=1)

        # Check first line of box
        assert canvas.get_char(2, 1) == "+"
        assert canvas.get_char(3, 1) == "-"
        assert canvas.get_char(6, 1) == "+"

        # Check middle line
        assert canvas.get_char(2, 2) == "|"
        assert canvas.get_char(4, 2) == "A"
        assert canvas.get_char(6, 2) == "|"

    def test_place_box_at_origin(self) -> None:
        """place_box at (0,0) works correctly."""
        canvas = Canvas(width=10, height=5)
        box = "AB\nCD"
        canvas.place_box(box, x=0, y=0)
        assert canvas.get_char(0, 0) == "A"
        assert canvas.get_char(1, 0) == "B"
        assert canvas.get_char(0, 1) == "C"
        assert canvas.get_char(1, 1) == "D"

    def test_place_box_partial_clip_right(self) -> None:
        """place_box clips content that extends past right edge."""
        canvas = Canvas(width=5, height=5)
        box = "ABCDEFGH"  # 8 chars, only 3 will fit starting at x=2
        canvas.place_box(box, x=2, y=0)
        assert canvas.get_char(2, 0) == "A"
        assert canvas.get_char(4, 0) == "C"
        # D, E, F, G, H are clipped

    def test_place_box_partial_clip_bottom(self) -> None:
        """place_box clips content that extends past bottom."""
        canvas = Canvas(width=10, height=2)
        box = "A\nB\nC\nD"  # 4 lines, only 2 will fit
        canvas.place_box(box, x=0, y=0)
        assert canvas.get_char(0, 0) == "A"
        assert canvas.get_char(0, 1) == "B"
        # C, D are clipped

    def test_place_multiple_boxes(self) -> None:
        """Multiple boxes can be placed on canvas."""
        canvas = Canvas(width=30, height=10)
        box1 = "+--+\n|A |\n+--+"
        box2 = "+--+\n|B |\n+--+"
        canvas.place_box(box1, x=0, y=0)
        canvas.place_box(box2, x=10, y=0)

        # First box
        assert canvas.get_char(1, 1) == "A"
        # Second box
        assert canvas.get_char(11, 1) == "B"


class TestCanvasRender:
    """Tests for render method."""

    def test_render_empty_canvas(self) -> None:
        """Empty canvas renders to empty string."""
        canvas = Canvas(width=5, height=3)
        result = canvas.render()
        # All spaces get stripped, so empty
        assert result == ""

    def test_render_single_char(self) -> None:
        """Canvas with single char renders correctly."""
        canvas = Canvas(width=10, height=5)
        canvas.put_char("X", 3, 2)
        result = canvas.render()
        lines = result.split("\n")
        assert len(lines) == 3  # Rows 0, 1, 2
        assert lines[2] == "   X"  # 3 spaces then X

    def test_render_box(self) -> None:
        """Canvas with box renders correctly."""
        canvas = Canvas(width=20, height=5)
        box = "+---+\n| A |\n+---+"
        canvas.place_box(box, x=0, y=0)
        result = canvas.render()
        lines = result.split("\n")
        assert lines[0] == "+---+"
        assert lines[1] == "| A |"
        assert lines[2] == "+---+"

    def test_render_strips_trailing_spaces(self) -> None:
        """Render strips trailing spaces from lines."""
        canvas = Canvas(width=20, height=5)
        canvas.put_char("X", 0, 0)
        result = canvas.render()
        lines = result.split("\n")
        assert lines[0] == "X"  # No trailing spaces

    def test_render_unicode_box(self) -> None:
        """Canvas handles Unicode box-drawing characters."""
        canvas = Canvas(width=20, height=5)
        box = "\n".join([
            "\u250c\u2500\u2500\u2500\u2510",
            "\u2502 A \u2502",
            "\u2514\u2500\u2500\u2500\u2518",
        ])
        canvas.place_box(box, x=0, y=0)
        result = canvas.render()
        assert "\u250c" in result  # Top-left corner
        assert "\u2518" in result  # Bottom-right corner
