"""Tests for Canvas class."""

import pytest

from visualflow.render import Canvas
from visualflow.models import EdgePath


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


class TestCanvasUnicode:
    """Tests for Canvas unicode handling."""

    def test_place_box_with_emoji(self) -> None:
        """Box containing emoji renders at correct column position."""
        canvas = Canvas(width=20, height=5)
        # Emoji takes 2 columns
        box = "+-----+\n| \U0001F680  |\n+-----+"  # rocket emoji
        canvas.place_box(box, x=0, y=0)
        result = canvas.render()
        lines = result.split("\n")
        assert lines[0] == "+-----+"
        assert "\U0001F680" in lines[1]
        assert lines[2] == "+-----+"

    def test_place_box_with_cjk(self) -> None:
        """Box containing CJK characters renders correctly."""
        canvas = Canvas(width=20, height=5)
        # Each CJK char takes 2 columns
        box = "+------+\n| \u4e2d\u6587 |\n+------+"  # Chinese chars
        canvas.place_box(box, x=0, y=0)
        result = canvas.render()
        lines = result.split("\n")
        assert lines[0] == "+------+"
        assert "\u4e2d" in lines[1]
        assert "\u6587" in lines[1]
        assert lines[2] == "+------+"

    def test_multiple_boxes_with_emoji_alignment(self) -> None:
        """Multiple boxes with emoji align correctly."""
        canvas = Canvas(width=40, height=5)
        box1 = "+-----+\n| \U0001F680  |\n+-----+"  # rocket
        box2 = "+-----+\n| OK  |\n+-----+"
        canvas.place_box(box1, x=0, y=0)
        canvas.place_box(box2, x=10, y=0)
        result = canvas.render()
        # Second box should start at column 10
        assert result.count("+-----+") == 4  # 2 boxes x 2 lines each

    def test_get_char_returns_placeholder_as_empty(self) -> None:
        """get_char returns empty string for wide char placeholder."""
        canvas = Canvas(width=10, height=3)
        canvas.place_box("\U0001F680", x=0, y=0)  # rocket at 0,0
        # The emoji is at column 0, placeholder at column 1
        assert canvas.get_char(0, 0) == "\U0001F680"
        assert canvas.get_char(1, 0) == ""  # placeholder

    def test_wide_char_near_boundary(self) -> None:
        """Wide character near canvas boundary is handled."""
        canvas = Canvas(width=5, height=3)
        # Emoji at column 3 would need column 4 for placeholder
        canvas.place_box("...\U0001F680", x=0, y=0)
        result = canvas.render()
        # Should render without error
        assert "..." in result


class TestCanvasDrawEdge:
    """Tests for Canvas.draw_edge method."""

    def test_draw_vertical_edge(self) -> None:
        """Vertical edge draws with | characters."""
        canvas = Canvas(width=10, height=10)
        path = EdgePath(
            source_id="a",
            target_id="b",
            segments=[(5, 2, 5, 7)],  # Vertical from y=2 to y=7
        )
        canvas.draw_edge(path)

        # Check vertical line
        for y in range(2, 7):
            assert canvas.get_char(5, y) == "|"
        # Arrow at end
        assert canvas.get_char(5, 7) == "v"

    def test_draw_horizontal_edge(self) -> None:
        """Horizontal edge draws with - characters."""
        canvas = Canvas(width=15, height=5)
        path = EdgePath(
            source_id="a",
            target_id="b",
            segments=[(2, 2, 10, 2)],  # Horizontal from x=2 to x=10
        )
        canvas.draw_edge(path)

        for x in range(2, 11):
            assert canvas.get_char(x, 2) == "-"

    def test_draw_z_shape_edge(self) -> None:
        """Z-shaped edge draws correctly with corner."""
        canvas = Canvas(width=20, height=15)
        path = EdgePath(
            source_id="a",
            target_id="b",
            segments=[
                (5, 3, 5, 6),    # Down
                (5, 6, 12, 6),   # Across
                (12, 6, 12, 10), # Down
            ],
        )
        canvas.draw_edge(path)

        # First vertical segment
        for y in range(3, 6):
            assert canvas.get_char(5, y) == "|"
        # Corner at (5, 6): coming from above, going right → └
        assert canvas.get_char(5, 6) == "└"
        # Horizontal segment
        for x in range(6, 12):
            assert canvas.get_char(x, 6) == "-"
        # Corner at (12, 6): coming from left, going down → ┐
        assert canvas.get_char(12, 6) == "┐"
        # Second vertical segment with arrow
        for y in range(7, 10):
            assert canvas.get_char(12, y) == "|"
        assert canvas.get_char(12, 10) == "v"

    def test_edge_does_not_overwrite_box(self) -> None:
        """Edge drawing does not overwrite box characters."""
        canvas = Canvas(width=20, height=10)
        box = "+---+\n| A |\n+---+"
        canvas.place_box(box, x=5, y=3)

        # Try to draw edge through box area
        path = EdgePath(
            source_id="a",
            target_id="b",
            segments=[(7, 0, 7, 8)],  # Vertical through box
        )
        canvas.draw_edge(path)

        # Box content should be preserved
        assert canvas.get_char(5, 3) == "+"
        assert canvas.get_char(7, 4) == "A"  # Box content not overwritten

    def test_empty_path_does_nothing(self) -> None:
        """Empty EdgePath does not modify canvas."""
        canvas = Canvas(width=10, height=10)
        path = EdgePath(source_id="a", target_id="b", segments=[])
        canvas.draw_edge(path)
        # Canvas should be unchanged (all spaces)
        assert canvas.render() == ""

    def test_edge_out_of_bounds_ignored(self) -> None:
        """Edge segments outside canvas bounds are ignored."""
        canvas = Canvas(width=5, height=5)
        path = EdgePath(
            source_id="a",
            target_id="b",
            segments=[(2, 2, 10, 2)],  # Extends beyond canvas
        )
        canvas.draw_edge(path)  # Should not raise
        # Only in-bounds portion drawn
        for x in range(2, 5):
            assert canvas.get_char(x, 2) == "-"
