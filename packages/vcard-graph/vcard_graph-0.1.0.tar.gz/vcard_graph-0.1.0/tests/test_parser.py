"""Tests for vCard parser."""

from pathlib import Path
from tempfile import NamedTemporaryFile

from vcard_graph.parser import RelatedContact, RelatedIdentifierType, VCardParser


def test_parse_simple_vcard() -> None:
    """Test parsing a simple vCard."""
    vcard_content = """BEGIN:VCARD
VERSION:3.0
UID:john@example.com
FN:John Doe
EMAIL:john@example.com
END:VCARD
"""
    parser = VCardParser()

    with NamedTemporaryFile(mode="w", suffix=".vcf", delete=False) as f:
        f.write(vcard_content)
        temp_path = Path(f.name)

    try:
        parser.parse_file(temp_path)
        contacts = parser.get_all_contacts()

        assert len(contacts) == 1
        contact = contacts[0]
        assert contact.uid == "john@example.com"
        assert contact.name == "John Doe"
        assert contact.email == "john@example.com"
    finally:
        temp_path.unlink()


def test_parse_vcard_with_org() -> None:
    """Test parsing a vCard with organization."""
    vcard_content = """BEGIN:VCARD
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
        contacts = parser.get_all_contacts()

        assert len(contacts) == 1
        contact = contacts[0]
        assert contact.org == "Acme Corp"
    finally:
        temp_path.unlink()


def test_parse_vcard_with_relationships() -> None:
    """Test parsing a vCard with relationships."""
    vcard_content = """BEGIN:VCARD
VERSION:4.0
UID:alice@example.com
FN:Alice Johnson
EMAIL:alice@example.com
RELATED;TYPE=spouse:bob@example.com
RELATED;TYPE=child:charlie@example.com
END:VCARD
"""
    parser = VCardParser()

    with NamedTemporaryFile(mode="w", suffix=".vcf", delete=False) as f:
        f.write(vcard_content)
        temp_path = Path(f.name)

    try:
        parser.parse_file(temp_path)
        contacts = parser.get_all_contacts()

        assert len(contacts) == 1
        contact = contacts[0]
        assert len(contact.related) == 2
        assert (
            RelatedContact("spouse", "bob@example.com", RelatedIdentifierType.EMAIL)
            in contact.related
        )
        assert (
            RelatedContact("child", "charlie@example.com", RelatedIdentifierType.EMAIL)
            in contact.related
        )
    finally:
        temp_path.unlink()


def test_parse_multiple_vcards() -> None:
    """Test parsing multiple vCards from one file."""
    vcard_content = """BEGIN:VCARD
VERSION:3.0
UID:person1@example.com
FN:Person One
END:VCARD
BEGIN:VCARD
VERSION:3.0
UID:person2@example.com
FN:Person Two
END:VCARD
"""
    parser = VCardParser()

    with NamedTemporaryFile(mode="w", suffix=".vcf", delete=False) as f:
        f.write(vcard_content)
        temp_path = Path(f.name)

    try:
        parser.parse_file(temp_path)
        contacts = parser.get_all_contacts()

        assert len(contacts) == 2
        uids = {c.uid for c in contacts}
        assert "person1@example.com" in uids
        assert "person2@example.com" in uids
    finally:
        temp_path.unlink()


def test_parse_apple_relations() -> None:
    """Test parsing Apple X-ABRELATEDNAMES fields."""
    vcard_content = """BEGIN:VCARD
VERSION:3.0
UID:alice@example.com
FN:Alice Johnson
EMAIL:alice@example.com
item1.X-ABRELATEDNAMES:Bob Smith
item1.X-ABLabel:_$!<Friend>!$_
item2.X-ABRELATEDNAMES:Carol Johnson
item2.X-ABLabel:_$!<Mother>!$_
END:VCARD
"""
    parser = VCardParser()

    with NamedTemporaryFile(mode="w", suffix=".vcf", delete=False) as f:
        f.write(vcard_content)
        temp_path = Path(f.name)

    try:
        parser.parse_file(temp_path)
        contacts = parser.get_all_contacts()

        assert len(contacts) == 1
        contact = contacts[0]
        assert len(contact.related) == 2
        assert RelatedContact("friend", "Bob Smith", RelatedIdentifierType.TEXT) in contact.related
        assert (
            RelatedContact("mother", "Carol Johnson", RelatedIdentifierType.TEXT) in contact.related
        )
    finally:
        temp_path.unlink()


def test_parse_apple_custom_label() -> None:
    """Test parsing Apple X-ABRELATEDNAMES with custom label."""
    vcard_content = """BEGIN:VCARD
VERSION:3.0
UID:test@example.com
FN:Test User
item1.X-ABRELATEDNAMES:Custom Person
item1.X-ABLabel:Mentor
END:VCARD
"""
    parser = VCardParser()

    with NamedTemporaryFile(mode="w", suffix=".vcf", delete=False) as f:
        f.write(vcard_content)
        temp_path = Path(f.name)

    try:
        parser.parse_file(temp_path)
        contacts = parser.get_all_contacts()

        assert len(contacts) == 1
        contact = contacts[0]
        assert len(contact.related) == 1
        assert (
            RelatedContact("mentor", "Custom Person", RelatedIdentifierType.TEXT) in contact.related
        )
    finally:
        temp_path.unlink()


def test_parse_mixed_relations() -> None:
    """Test parsing both standard RELATED and Apple X-ABRELATEDNAMES."""
    vcard_content = """BEGIN:VCARD
VERSION:4.0
UID:mixed@example.com
FN:Mixed User
RELATED;TYPE=spouse:Standard Spouse
item1.X-ABRELATEDNAMES:Apple Friend
item1.X-ABLabel:_$!<Friend>!$_
END:VCARD
"""
    parser = VCardParser()

    with NamedTemporaryFile(mode="w", suffix=".vcf", delete=False) as f:
        f.write(vcard_content)
        temp_path = Path(f.name)

    try:
        parser.parse_file(temp_path)
        contacts = parser.get_all_contacts()

        assert len(contacts) == 1
        contact = contacts[0]
        assert len(contact.related) == 2
        assert (
            RelatedContact("spouse", "Standard Spouse", RelatedIdentifierType.TEXT)
            in contact.related
        )
        assert (
            RelatedContact("friend", "Apple Friend", RelatedIdentifierType.TEXT) in contact.related
        )
    finally:
        temp_path.unlink()


def test_parse_urn_uuid_relation() -> None:
    """Test parsing RELATED with urn:uuid: identifier."""
    vcard_content = """BEGIN:VCARD
VERSION:4.0
UID:alice@example.com
FN:Alice Johnson
RELATED;TYPE=friend:urn:uuid:f81d4fae-7dec-11d0-a765-00a0c91e6bf6
END:VCARD
"""
    parser = VCardParser()

    with NamedTemporaryFile(mode="w", suffix=".vcf", delete=False) as f:
        f.write(vcard_content)
        temp_path = Path(f.name)

    try:
        parser.parse_file(temp_path)
        contacts = parser.get_all_contacts()

        assert len(contacts) == 1
        contact = contacts[0]
        assert len(contact.related) == 1
        assert (
            RelatedContact(
                "friend",
                "urn:uuid:f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
                RelatedIdentifierType.URN_UUID,
            )
            in contact.related
        )
    finally:
        temp_path.unlink()


def test_parse_uri_relation() -> None:
    """Test parsing RELATED with URI identifier."""
    vcard_content = """BEGIN:VCARD
VERSION:4.0
UID:alice@example.com
FN:Alice Johnson
RELATED;TYPE=contact:http://example.com/directory/jdoe.vcf
END:VCARD
"""
    parser = VCardParser()

    with NamedTemporaryFile(mode="w", suffix=".vcf", delete=False) as f:
        f.write(vcard_content)
        temp_path = Path(f.name)

    try:
        parser.parse_file(temp_path)
        contacts = parser.get_all_contacts()

        assert len(contacts) == 1
        contact = contacts[0]
        assert len(contact.related) == 1
        assert (
            RelatedContact(
                "contact",
                "http://example.com/directory/jdoe.vcf",
                RelatedIdentifierType.URI,
            )
            in contact.related
        )
    finally:
        temp_path.unlink()


def test_parse_text_value_relation() -> None:
    """Test parsing RELATED with VALUE=text."""
    vcard_content = """BEGIN:VCARD
VERSION:4.0
UID:alice@example.com
FN:Alice Johnson
RELATED;TYPE=co-worker;VALUE=text:Please contact my assistant Jane Doe for any inquiries.
END:VCARD
"""
    parser = VCardParser()

    with NamedTemporaryFile(mode="w", suffix=".vcf", delete=False) as f:
        f.write(vcard_content)
        temp_path = Path(f.name)

    try:
        parser.parse_file(temp_path)
        contacts = parser.get_all_contacts()

        assert len(contacts) == 1
        contact = contacts[0]
        assert len(contact.related) == 1
        related = contact.related[0]
        assert related.relationship_type == "co-worker"
        assert "Jane Doe" in related.identifier
        assert related.identifier_type == RelatedIdentifierType.TEXT
    finally:
        temp_path.unlink()


def test_parse_categories() -> None:
    """Test parsing CATEGORIES field."""
    vcard_content = """BEGIN:VCARD
VERSION:3.0
UID:alice@example.com
FN:Alice Johnson
CATEGORIES:Family,VIP
END:VCARD
"""
    parser = VCardParser()

    with NamedTemporaryFile(mode="w", suffix=".vcf", delete=False) as f:
        f.write(vcard_content)
        temp_path = Path(f.name)

    try:
        parser.parse_file(temp_path)
        contacts = parser.get_all_contacts()

        assert len(contacts) == 1
        contact = contacts[0]
        assert len(contact.categories) == 2
        assert "Family" in contact.categories
        assert "VIP" in contact.categories
    finally:
        temp_path.unlink()


def test_filter_system_categories() -> None:
    """Test that system categories are filtered out."""
    vcard_content = """BEGIN:VCARD
VERSION:3.0
UID:bob@example.com
FN:Bob Smith
CATEGORIES:Starred,Family,myContacts
END:VCARD
"""
    parser = VCardParser()

    with NamedTemporaryFile(mode="w", suffix=".vcf", delete=False) as f:
        f.write(vcard_content)
        temp_path = Path(f.name)

    try:
        parser.parse_file(temp_path)
        contacts = parser.get_all_contacts()

        assert len(contacts) == 1
        contact = contacts[0]
        # Only "Family" should remain after filtering system categories
        assert len(contact.categories) == 1
        assert "Family" in contact.categories
        assert "Starred" not in contact.categories
        assert "myContacts" not in contact.categories
    finally:
        temp_path.unlink()
