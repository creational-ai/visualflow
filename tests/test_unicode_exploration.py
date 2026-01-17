"""Explore Unicode connector and arrow character options.

This is an exploration test - not part of the main test suite.
Run with: uv run pytest tests/test_unicode_exploration.py -v -s
"""

import pytest


class TestConnectorExploration:
    """Visual exploration of Unicode connector and arrow options."""

    def test_arrow_styles(self) -> None:
        """Show different arrow head options."""
        print("\n" + "=" * 60)
        print("ARROW STYLES")
        print("=" * 60)

        arrows = [
            ("v", "Current (ASCII lowercase v)"),
            ("▼", "Black down-pointing triangle"),
            ("▽", "White down-pointing triangle"),
            ("↓", "Downwards arrow"),
            ("⬇", "Downwards black arrow"),
            ("⇓", "Downwards double arrow"),
            ("⏷", "Black medium down-pointing triangle"),
            ("🔽", "Downwards button"),
            ("⯆", "Downwards triangle-headed arrow"),
            ("˅", "Modifier letter down arrowhead"),
            ("ꜜ", "Modifier letter down arrow"),
        ]

        for arrow, name in arrows:
            print(f"    |          ")
            print(f"    |    {arrow}  ← {name}")
            print(f"    {arrow}          ")
            print()

    def test_vertical_line_styles(self) -> None:
        """Show different vertical line options."""
        print("\n" + "=" * 60)
        print("VERTICAL LINE STYLES")
        print("=" * 60)

        lines = [
            ("|", "Current (ASCII pipe)"),
            ("│", "Box drawings light vertical"),
            ("┃", "Box drawings heavy vertical"),
            ("║", "Box drawings double vertical"),
            ("┆", "Box drawings light triple dash vertical"),
            ("┇", "Box drawings heavy triple dash vertical"),
            ("┊", "Box drawings light quadruple dash vertical"),
            ("╎", "Box drawings light double dash vertical"),
            ("╏", "Box drawings heavy double dash vertical"),
            ("⎸", "Left vertical box line"),
            ("⎹", "Right vertical box line"),
        ]

        for char, name in lines:
            print(f"    {char}{char}{char}{char}{char}  ← {name}")
        print()

    def test_horizontal_line_styles(self) -> None:
        """Show different horizontal line options."""
        print("\n" + "=" * 60)
        print("HORIZONTAL LINE STYLES")
        print("=" * 60)

        lines = [
            ("-", "Current (ASCII hyphen)"),
            ("─", "Box drawings light horizontal"),
            ("━", "Box drawings heavy horizontal"),
            ("═", "Box drawings double horizontal"),
            ("┄", "Box drawings light triple dash horizontal"),
            ("┅", "Box drawings heavy triple dash horizontal"),
            ("┈", "Box drawings light quadruple dash horizontal"),
            ("╌", "Box drawings light double dash horizontal"),
            ("╍", "Box drawings heavy double dash horizontal"),
            ("⎯", "Horizontal line extension"),
            ("―", "Horizontal bar"),
        ]

        for char, name in lines:
            print(f"    {char}{char}{char}{char}{char}{char}{char}{char}{char}{char}  ← {name}")
        print()

    def test_corner_styles(self) -> None:
        """Show different corner options."""
        print("\n" + "=" * 60)
        print("CORNER STYLES (for turns in paths)")
        print("=" * 60)

        corners = [
            ("┌┐└┘", "Light corners (current)"),
            ("┏┓┗┛", "Heavy corners"),
            ("╔╗╚╝", "Double corners"),
            ("╭╮╰╯", "Rounded corners"),
        ]

        for chars, name in corners:
            tl, tr, bl, br = chars
            print(f"    {name}:")
            print(f"      {tl}───{tr}   {bl}   {br}")
            print(f"      │   │   │   │")
            print(f"      {bl}───{br}   {tl}   {tr}")
            print()

    def test_full_comparison(self) -> None:
        """Compare complete connector sets in a realistic pattern."""
        print("\n" + "=" * 60)
        print("FULL COMPARISON: Fan-out pattern")
        print("=" * 60)

        # Current style
        print("\n  CURRENT (ASCII + light corners):")
        print("              ┬")
        print("              |")
        print("              |")
        print("         ┌----┼----┐")
        print("         |    |    |")
        print("         v    v    v")

        # Light Unicode
        print("\n  LIGHT UNICODE:")
        print("              ┬")
        print("              │")
        print("              │")
        print("         ┌────┼────┐")
        print("         │    │    │")
        print("         ▼    ▼    ▼")

        # Light with rounded corners
        print("\n  ROUNDED CORNERS:")
        print("              ┬")
        print("              │")
        print("              │")
        print("         ╭────┼────╮")
        print("         │    │    │")
        print("         ▼    ▼    ▼")

        # Heavy
        print("\n  HEAVY:")
        print("              ┳")
        print("              ┃")
        print("              ┃")
        print("         ┏━━━━╋━━━━┓")
        print("         ┃    ┃    ┃")
        print("         ▼    ▼    ▼")

        # Light with arrow variation
        print("\n  LIGHT + ARROW VARIATION:")
        print("              ┬")
        print("              │")
        print("              │")
        print("         ┌────┼────┐")
        print("         │    │    │")
        print("         ↓    ↓    ↓")

        print()

    def test_merge_comparison(self) -> None:
        """Compare merge patterns."""
        print("\n" + "=" * 60)
        print("MERGE PATTERN COMPARISON")
        print("=" * 60)

        # Current
        print("\n  CURRENT:")
        print("         |    |    |")
        print("         └----┼----┘")
        print("              |")
        print("              v")

        # Light
        print("\n  LIGHT UNICODE:")
        print("         │    │    │")
        print("         └────┼────┘")
        print("              │")
        print("              ▼")

        # Rounded
        print("\n  ROUNDED:")
        print("         │    │    │")
        print("         ╰────┼────╯")
        print("              │")
        print("              ▼")

        print()

    def test_recommended_sets(self) -> None:
        """Show recommended character sets."""
        print("\n" + "=" * 60)
        print("RECOMMENDED CHARACTER SETS")
        print("=" * 60)

        print("""
  OPTION A: Light Unicode (clean, professional)
  ─────────────────────────────────────────────
  Vertical:    │
  Horizontal:  ─
  Corners:     ┌ ┐ └ ┘
  T-junctions: ┬ ┴ ├ ┤
  Cross:       ┼
  Arrow:       ▼

  OPTION B: Light + Rounded corners (softer look)
  ───────────────────────────────────────────────
  Vertical:    │
  Horizontal:  ─
  Corners:     ╭ ╮ ╰ ╯
  T-junctions: ┬ ┴ ├ ┤
  Cross:       ┼
  Arrow:       ▼

  OPTION C: Current + Better arrow only
  ──────────────────────────────────────
  Keep everything, just change v → ▼

  OPTION D: Dashed lines (subtle)
  ────────────────────────────────
  Vertical:    ┆
  Horizontal:  ┄
  Corners:     ┌ ┐ └ ┘
  T-junctions: ┬ ┴ ├ ┤
  Cross:       ┼
  Arrow:       ▼
""")
