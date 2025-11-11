"""Tests for graph building."""

from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

from vcard_graph.graph import VCardGraph
from vcard_graph.parser import VCardParser


def test_build_simple_graph() -> None:
    """Test building a simple graph."""
    vcard_content = """BEGIN:VCARD
VERSION:3.0
UID:john@example.com
FN:John Doe
EMAIL:john@example.com
END:VCARD
BEGIN:VCARD
VERSION:3.0
UID:jane@example.com
FN:Jane Smith
EMAIL:jane@example.com
END:VCARD
"""
    parser = VCardParser()

    with NamedTemporaryFile(mode="w", suffix=".vcf", delete=False) as f:
        f.write(vcard_content)
        temp_path = Path(f.name)

    try:
        parser.parse_file(temp_path)
        graph = VCardGraph()
        graph.build_from_parser(parser)

        stats = graph.get_stats()
        assert stats["people"] == 2
        assert stats["total_nodes"] == 2
        assert stats["relationships"] == 0
    finally:
        temp_path.unlink()


def test_build_graph_with_relationships() -> None:
    """Test building a graph with relationships."""
    vcard_content = """BEGIN:VCARD
VERSION:4.0
UID:alice@example.com
FN:Alice Johnson
EMAIL:alice@example.com
RELATED;TYPE=spouse:bob@example.com
END:VCARD
BEGIN:VCARD
VERSION:4.0
UID:bob@example.com
FN:Bob Johnson
EMAIL:bob@example.com
RELATED;TYPE=spouse:alice@example.com
END:VCARD
"""
    parser = VCardParser()

    with NamedTemporaryFile(mode="w", suffix=".vcf", delete=False) as f:
        f.write(vcard_content)
        temp_path = Path(f.name)

    try:
        parser.parse_file(temp_path)
        graph = VCardGraph()
        graph.build_from_parser(parser)

        stats = graph.get_stats()
        assert stats["people"] == 2
        assert stats["relationships"] >= 1  # At least one relationship edge
    finally:
        temp_path.unlink()


def test_build_graph_with_organization() -> None:
    """Test building a graph with organization nodes."""
    vcard_content = """BEGIN:VCARD
VERSION:3.0
UID:john@example.com
FN:John Doe
EMAIL:john@example.com
ORG:Acme Corp
END:VCARD
BEGIN:VCARD
VERSION:3.0
UID:jane@example.com
FN:Jane Smith
EMAIL:jane@example.com
ORG:Acme Corp
END:VCARD
"""
    parser = VCardParser()

    with NamedTemporaryFile(mode="w", suffix=".vcf", delete=False) as f:
        f.write(vcard_content)
        temp_path = Path(f.name)

    try:
        parser.parse_file(temp_path)
        graph = VCardGraph()
        graph.build_from_parser(parser)

        stats = graph.get_stats()
        assert stats["people"] == 2
        assert stats["organizations"] == 1
        assert stats["relationships"] == 2  # Both connected to org
    finally:
        temp_path.unlink()


def test_visualize_graph() -> None:
    """Test graph visualization."""
    vcard_content = """BEGIN:VCARD
VERSION:3.0
UID:test@example.com
FN:Test User
EMAIL:test@example.com
END:VCARD
"""
    parser = VCardParser()

    with NamedTemporaryFile(mode="w", suffix=".vcf", delete=False) as vcf_file:
        vcf_file.write(vcard_content)
        vcf_path = Path(vcf_file.name)

    with TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_graph.html"

        try:
            parser.parse_file(vcf_path)
            graph = VCardGraph()
            graph.build_from_parser(parser)
            graph.visualize(str(output_path))

            assert output_path.exists()
            assert output_path.stat().st_size > 0
        finally:
            vcf_path.unlink()
