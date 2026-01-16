"""ascii-dag layout engine evaluation tests.

ascii-dag is a Rust library with sophisticated Sugiyama layout and edge routing.
This test suite evaluates its capabilities via subprocess calls to compiled examples.

Key findings to document:
- Custom node dimensions: Yes (in Rust API)
- Coordinate system: Character-based grid
- Edge routing hints: Yes (sophisticated edge routing built-in)
- Integration: Subprocess to compiled binary (no Python bindings)
- Unique value: Already renders ASCII output directly
"""

import subprocess
from pathlib import Path

import pytest


ASCII_DAG_DIR = Path(__file__).parent.parent / "ascii-dag"
ASCII_DAG_BINARY_DIR = ASCII_DAG_DIR / "target" / "release" / "examples"


def is_ascii_dag_built() -> bool:
    """Check if ascii-dag is compiled."""
    return (ASCII_DAG_BINARY_DIR / "basic").exists()


# Skip all tests if ascii-dag not built
pytestmark = pytest.mark.skipif(
    not is_ascii_dag_built(),
    reason="ascii-dag not built (run: cd ascii-dag && cargo build --release --examples)",
)


def run_example(name: str, timeout: float = 5.0) -> str:
    """Run an ascii-dag example and return output."""
    binary = ASCII_DAG_BINARY_DIR / name
    if not binary.exists():
        pytest.skip(f"Example {name} not built")

    result = subprocess.run(
        [str(binary)],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.stdout


class TestAsciiDagBuilt:
    """Verify ascii-dag is properly built."""

    def test_cargo_toml_exists(self) -> None:
        """Verify ascii-dag is cloned."""
        cargo_toml = ASCII_DAG_DIR / "Cargo.toml"
        assert cargo_toml.exists(), "ascii-dag not cloned"

    def test_release_build_exists(self) -> None:
        """Verify release build exists."""
        release_dir = ASCII_DAG_DIR / "target" / "release"
        assert release_dir.exists(), "ascii-dag not built in release mode"

    def test_basic_example_exists(self) -> None:
        """Verify basic example is compiled."""
        basic = ASCII_DAG_BINARY_DIR / "basic"
        assert basic.exists(), "basic example not compiled"


class TestAsciiDagBasicExample:
    """Test ascii-dag's basic example output."""

    def test_basic_produces_output(self) -> None:
        """Verify basic example produces output."""
        output = run_example("basic")
        assert output, "No output from basic example"
        assert len(output) > 10, "Output too short"

    def test_basic_output_contains_box_chars(self) -> None:
        """Verify output contains ASCII box characters."""
        output = run_example("basic")

        # Should contain box drawing characters or brackets
        box_chars = ["[", "]", "\u2500", "\u2502", "\u250c", "\u2510", "\u2514", "\u2518", "+", "-", "|"]
        has_box_char = any(c in output for c in box_chars)
        assert has_box_char, f"Output doesn't look like ASCII diagram: {output[:100]}"

    def test_basic_output_is_multiline(self) -> None:
        """Verify output is multi-line diagram."""
        output = run_example("basic")
        lines = output.strip().split("\n")
        assert len(lines) > 1, "Output should be multi-line"


class TestAsciiDagCapabilities:
    """Document ascii-dag's capabilities based on available examples."""

    def test_list_available_examples(self) -> None:
        """Document which examples are available."""
        if not ASCII_DAG_BINARY_DIR.exists():
            pytest.skip("Binary directory doesn't exist")

        examples = [
            f.name
            for f in ASCII_DAG_BINARY_DIR.iterdir()
            if f.is_file() and not f.name.endswith(".d")
        ]

        # Should have at least the basic example
        assert "basic" in examples

        # Document available examples
        print(f"\nAvailable ascii-dag examples: {sorted(examples)}")

    def test_basic_example_visual_inspection(self) -> None:
        """Visual inspection of basic example output.

        This test prints the output for manual inspection.
        It always passes - the purpose is documentation.
        """
        output = run_example("basic")

        # Print for visual inspection
        print("\n" + "=" * 60)
        print("ascii-dag basic example output:")
        print("=" * 60)
        print(output)
        print("=" * 60)

        # Always pass - this is for inspection only
        assert True

    def test_output_format_analysis(self) -> None:
        """Analyze the output format of ascii-dag."""
        output = run_example("basic")

        # Count unique characters used
        chars = set(output)
        printable_chars = [c for c in chars if c.isprintable() and c != " "]

        # Document character set
        print(f"\nCharacters used: {sorted(printable_chars)}")

        # Check for common diagram elements
        has_arrows = any(c in output for c in ["\u2192", "\u2190", "\u2193", "\u2191", ">", "<", "v", "^"])
        has_boxes = any(c in output for c in ["[", "]", "\u250c", "\u2510", "\u2514", "\u2518"])
        has_lines = any(c in output for c in ["\u2500", "\u2502", "-", "|"])

        print(f"Has arrows: {has_arrows}")
        print(f"Has boxes: {has_boxes}")
        print(f"Has lines: {has_lines}")


class TestAsciiDagIntegrationComplexity:
    """Document integration complexity for ascii-dag."""

    def test_integration_requires_subprocess(self) -> None:
        """Document: ascii-dag requires subprocess for Python integration.

        ascii-dag is a Rust library. For Python integration, options are:
        1. Subprocess to compiled binary (current approach)
        2. Build Python bindings with PyO3
        3. FFI bridge

        Subprocess is simplest but limits flexibility.
        """
        # This is a documentation test - always passes
        assert True

    def test_no_python_api(self) -> None:
        """Document: No native Python API available.

        Unlike Grandalf (pure Python) or Graphviz (Python bindings exist),
        ascii-dag requires compilation and subprocess calls.
        """
        # Try to import - should fail
        try:
            import ascii_dag  # noqa: F401

            pytest.fail("ascii_dag should not be importable")
        except ImportError:
            pass  # Expected

    def test_custom_input_requires_rust_code(self) -> None:
        """Document: Custom graph input requires modifying Rust code.

        The compiled examples have hardcoded graphs. To test our
        scenarios, we would need to either:
        1. Create a Rust CLI that accepts input
        2. Create Python bindings
        3. Use the Rust library directly in a Rust test

        This is significantly more complex than Grandalf or Graphviz.
        """
        # Document the limitation
        assert True


class TestAsciiDagAdditionalExamples:
    """Test additional ascii-dag examples if available."""

    def test_build_additional_examples(self) -> None:
        """Build additional examples for testing.

        This test attempts to build more examples. If it fails,
        subsequent tests will be skipped.
        """
        result = subprocess.run(
            ["cargo", "build", "--release", "--examples"],
            cwd=ASCII_DAG_DIR,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            print(f"Build output: {result.stderr}")
            # Don't fail - just document

    def test_complex_graphs_if_available(self) -> None:
        """Test complex_graphs example if built."""
        binary = ASCII_DAG_BINARY_DIR / "complex_graphs"
        if not binary.exists():
            pytest.skip("complex_graphs example not built")

        output = run_example("complex_graphs")

        print("\n" + "=" * 60)
        print("ascii-dag complex_graphs output:")
        print("=" * 60)
        print(output[:2000])  # Limit output length
        print("=" * 60)

        assert output, "No output from complex_graphs"

    def test_edge_cases_if_available(self) -> None:
        """Test edge_cases example if built."""
        binary = ASCII_DAG_BINARY_DIR / "edge_cases"
        if not binary.exists():
            pytest.skip("edge_cases example not built")

        output = run_example("edge_cases")

        print("\n" + "=" * 60)
        print("ascii-dag edge_cases output:")
        print("=" * 60)
        print(output[:2000])
        print("=" * 60)

        assert output, "No output from edge_cases"

    def test_cross_level_if_available(self) -> None:
        """Test cross_level example if built (similar to our skip-level)."""
        binary = ASCII_DAG_BINARY_DIR / "cross_level"
        if not binary.exists():
            pytest.skip("cross_level example not built")

        output = run_example("cross_level")

        print("\n" + "=" * 60)
        print("ascii-dag cross_level output:")
        print("=" * 60)
        print(output[:2000])
        print("=" * 60)

        assert output, "No output from cross_level"


class TestAsciiDagUniqueValue:
    """Document ascii-dag's unique value proposition."""

    def test_direct_ascii_output(self) -> None:
        """Document: ascii-dag produces ASCII output directly.

        Unlike Grandalf and Graphviz which produce coordinates,
        ascii-dag produces the final ASCII diagram directly.
        This is its main unique value.
        """
        output = run_example("basic")

        # Output is directly usable ASCII art
        assert "\n" in output, "Should be multi-line"
        # No coordinates to parse - it's already visual

    def test_sophisticated_edge_routing(self) -> None:
        """Document: ascii-dag has sophisticated edge routing built-in.

        The edge routing in ascii-dag handles:
        - Cross-level edges
        - Edge bundling
        - Collision avoidance

        This is the main reason to consider using it.
        """
        output = run_example("basic")

        # Look for edge routing characters
        edge_chars = ["\u2502", "|", "\u2500", "-", "\u2514", "\u2518", "\u250c", "\u2510"]
        has_edges = any(c in output for c in edge_chars)
        assert has_edges, "Should have edge routing characters"

    def test_no_coordinate_transformation_needed(self) -> None:
        """Document: No coordinate transformation needed.

        With Grandalf or Graphviz, we need to:
        1. Get coordinates
        2. Scale to character grid
        3. Render boxes
        4. Compute edge routing
        5. Render edges

        With ascii-dag, it's just:
        1. Call binary
        2. Get ASCII output

        Trade-off: Less flexibility, but simpler integration.
        """
        # This is documentation - always passes
        assert True
