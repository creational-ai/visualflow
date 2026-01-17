"""Pre-made box content for test fixtures.

These represent the kind of content that comes from Mission Control
task `diagram` fields - complete boxes with borders.
"""


def make_simple_box(label: str, width: int = 15) -> str:
    """Create a simple box with label.

    Args:
        label: Text to display in box
        width: Total width including borders

    Returns:
        Multi-line string box
    """
    inner_width = width - 2  # Account for borders
    top = "+" + "-" * inner_width + "+"
    middle = "|" + label.center(inner_width) + "|"
    bottom = "+" + "-" * inner_width + "+"
    return "\n".join([top, middle, bottom])


def make_detailed_box(title: str, subtitle: str, status: str, width: int = 25) -> str:
    """Create a detailed box like Mission Control tasks.

    Args:
        title: Main title
        subtitle: Subtitle line
        status: Status indicator
        width: Total width including borders

    Returns:
        Multi-line string box
    """
    inner = width - 2
    lines = [
        "+" + "-" * inner + "+",
        "|" + title.center(inner) + "|",
        "|" + subtitle.center(inner) + "|",
        "|" + status.center(inner) + "|",
        "+" + "-" * inner + "+",
    ]
    return "\n".join(lines)


# Pre-made boxes for fixtures (realistic Mission Control style)
BOX_POC1 = """\
+-------------------------+
|         PoC 1           |
|        SCHEMA           |
|      Complete           |
+-------------------------+"""

BOX_POC2 = """\
+-------------------------+
|         PoC 2           |
|        SERVER           |
|      Complete           |
+-------------------------+"""

BOX_POC3 = """\
+-------------------------+
|         PoC 3           |
|          CRUD           |
|      Complete           |
+-------------------------+"""

BOX_POC4 = """\
+-------------------------+
|         PoC 4           |
|        HISTORY          |
|      Complete           |
+-------------------------+"""

BOX_POC5 = """\
+-------------------------+
|         PoC 5           |
|       WORKFLOW          |
|      Complete           |
+-------------------------+"""

BOX_POC6 = """\
+-------------------------+
|         PoC 6           |
|       ANALYSIS          |
|      Complete           |
+-------------------------+"""

BOX_POC7 = """\
+-------------------------+
|         PoC 7           |
|          E2E            |
|      Complete           |
+-------------------------+"""

BOX_POC8 = """\
+-------------------------+
|         PoC 8           |
|       ABSTRACT          |
|      Complete           |
+-------------------------+"""

BOX_STANDALONE_A = """\
+-------------------------+
|    STRUCTURED TEXT      |
|      Complete           |
+-------------------------+"""

BOX_STANDALONE_B = """\
+-------------------------+
|     DELETE TOOLS        |
|      Complete           |
+-------------------------+"""
