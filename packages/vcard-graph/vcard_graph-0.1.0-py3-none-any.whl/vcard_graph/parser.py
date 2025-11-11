"""Parse vCard files using vobject library."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, Protocol

import vobject  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from typing import Any


class RelatedIdentifierType(Enum):
    """Type of identifier in a RELATED field."""

    UID = "uid"  # Direct UID reference
    URN_UUID = "urn_uuid"  # urn:uuid: reference
    URI = "uri"  # http/https URL reference
    EMAIL = "email"  # Email address
    TEXT = "text"  # Plain text description


class RelatedContact:
    """Represents a related contact reference."""

    def __init__(
        self, relationship_type: str, identifier: str, identifier_type: RelatedIdentifierType
    ) -> None:
        self.relationship_type = relationship_type
        self.identifier = identifier
        self.identifier_type = identifier_type

    def __repr__(self) -> str:
        return (
            f"RelatedContact(type={self.relationship_type!r}, "
            f"id={self.identifier!r}, id_type={self.identifier_type})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RelatedContact):
            return NotImplemented
        return (
            self.relationship_type == other.relationship_type
            and self.identifier == other.identifier
            and self.identifier_type == other.identifier_type
        )


class VCardComponent(Protocol):
    """Protocol for vobject vCard component."""

    name: str
    value: Any

    def getChildren(self) -> list[VCardComponent]: ...  # noqa: N802


class VCardNameValue(Protocol):
    """Protocol for vCard N (name) field value."""

    given: str
    family: str


class Contact:
    """Represents a contact from a vCard."""

    def __init__(
        self,
        uid: str,
        name: str,
        email: str | None = None,
        org: str | None = None,
        related: list[RelatedContact] | None = None,
        categories: list[str] | None = None,
    ) -> None:
        self.uid = uid
        self.name = name
        self.email = email
        self.org = org
        self.related = related or []
        self.categories = categories or []

    def __repr__(self) -> str:
        return f"Contact(uid={self.uid!r}, name={self.name!r}, email={self.email!r})"


class VCardParser:
    """Parser for vCard files."""

    def __init__(self) -> None:
        self.contacts: dict[str, Contact] = {}

    def parse_file(self, file_path: Path) -> None:
        """Parse a single vCard file."""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # vobject can handle multiple vCards in one file
        vcards: Iterator[VCardComponent] = vobject.readComponents(content)  # type: ignore[attr-defined]
        for vcard in vcards:
            if vcard.name != "VCARD":
                continue

            contact = self._extract_contact(vcard)
            if contact:
                self.contacts[contact.uid] = contact

    def parse_directory(self, dir_path: Path) -> None:
        """Parse all vCard files in a directory."""
        for vcf_file in dir_path.glob("**/*.vcf"):
            try:
                self.parse_file(vcf_file)
            except Exception as e:
                print(f"Warning: Failed to parse {vcf_file}: {e}")

        # Also try .vcard extension
        for vcard_file in dir_path.glob("**/*.vcard"):
            try:
                self.parse_file(vcard_file)
            except Exception as e:
                print(f"Warning: Failed to parse {vcard_file}: {e}")

    def parse_files(self, file_paths: list[Path]) -> None:
        """Parse multiple vCard files."""
        for file_path in file_paths:
            try:
                self.parse_file(file_path)
            except Exception as e:
                print(f"Warning: Failed to parse {file_path}: {e}")

    def _extract_contact(self, vcard: VCardComponent) -> Contact | None:
        """Extract contact information from a vCard component."""
        # Get UID (required)
        uid = None
        if hasattr(vcard, "uid"):
            uid = str(vcard.uid.value)
        else:
            # Generate UID from email or name if not present
            if hasattr(vcard, "email"):
                uid = str(vcard.email.value)
            elif hasattr(vcard, "fn"):
                uid = str(vcard.fn.value)
            else:
                return None

        # Get name
        name = ""
        if hasattr(vcard, "fn"):
            name = str(vcard.fn.value)
        elif hasattr(vcard, "n"):
            n = vcard.n.value
            name = f"{n.given} {n.family}".strip()

        if not name:
            name = uid

        # Get email
        email = None
        if hasattr(vcard, "email"):
            email = str(vcard.email.value)

        # Get organization
        org = None
        if hasattr(vcard, "org"):
            org_value = vcard.org.value
            if isinstance(org_value, list):
                org = org_value[0] if org_value else None
            else:
                org = str(org_value)

        # Get categories
        categories: list[str] = []
        # System categories to filter out
        system_categories = {"starred", "mycontacts", "my contacts", "system group: my contacts"}
        if hasattr(vcard, "categories"):
            cat_value = vcard.categories.value
            if isinstance(cat_value, list):
                categories = [
                    str(c).strip()
                    for c in cat_value
                    if c and str(c).strip().lower() not in system_categories
                ]
            else:
                # Single category or comma-separated
                cat_str = str(cat_value)
                categories = [
                    c.strip()
                    for c in cat_str.split(",")
                    if c.strip() and c.strip().lower() not in system_categories
                ]

        # Get related contacts using standard RELATED field (RFC 6350)
        # and Apple X-ABRELATEDNAMES
        related: list[RelatedContact] = []

        # Extract standard RELATED fields
        for child in vcard.getChildren():
            if child.name == "RELATED":
                identifier = str(child.value)
                # Extract TYPE parameter (e.g., spouse, child, parent, friend, colleague)
                rel_type = "related"  # default
                if hasattr(child, "params") and "TYPE" in child.params:
                    type_value = child.params["TYPE"]
                    if isinstance(type_value, list):
                        rel_type = type_value[0].lower()
                    else:
                        rel_type = type_value.lower()

                # Classify the identifier type
                id_type = self._classify_identifier(identifier)
                related.append(RelatedContact(rel_type, identifier, id_type))

        # Extract Apple X-ABRELATEDNAMES fields
        # These use item grouping: item1.X-ABRELATEDNAMES paired with item1.X-ABLabel
        apple_relations = self._extract_apple_relations(vcard)
        related.extend(apple_relations)

        return Contact(
            uid=uid, name=name, email=email, org=org, related=related, categories=categories
        )

    def _classify_identifier(self, identifier: str) -> RelatedIdentifierType:
        """Classify the type of identifier in a RELATED field.

        According to RFC 6350, RELATED can contain:
        - URIs (including urn:uuid:)
        - Text (when VALUE=text parameter is used)
        """
        # Check for urn:uuid: format
        if identifier.startswith("urn:uuid:"):
            return RelatedIdentifierType.URN_UUID

        # Check for http/https URIs
        if identifier.startswith(("http://", "https://")):
            return RelatedIdentifierType.URI

        # Check if it looks like an email (simple heuristic)
        if "@" in identifier and "." in identifier.split("@")[-1]:
            return RelatedIdentifierType.EMAIL

        # Check if it might be a UID (UUID format without urn:uuid: prefix)
        # UUIDs are 36 characters with hyphens in specific positions
        if (
            len(identifier) == 36
            and identifier[8] == "-"
            and identifier[13] == "-"
            and identifier[18] == "-"
            and identifier[23] == "-"
        ):
            return RelatedIdentifierType.UID

        # Default to text (name or description)
        return RelatedIdentifierType.TEXT

    def _extract_apple_relations(self, vcard: VCardComponent) -> list[RelatedContact]:
        """Extract Apple X-ABRELATEDNAMES relationships.

        Apple uses item grouping to pair X-ABRELATEDNAMES with X-ABLabel:
        item1.X-ABRELATEDNAMES:John Doe
        item1.X-ABLabel:_$!<Friend>!$_

        vobject parses these with a 'group' attribute on the component.
        """
        relations: list[RelatedContact] = []

        # Build a map of item groups to their X-ABRELATEDNAMES and X-ABLabel values
        item_groups: dict[str, dict[str, str]] = {}

        for child in vcard.getChildren():
            # Check if this child has a group (vobject's way of handling item grouping)
            group = getattr(child, "group", None)

            if group and child.name in ("X-ABRELATEDNAMES", "X-ABLABEL"):
                if group not in item_groups:
                    item_groups[group] = {}

                if child.name == "X-ABRELATEDNAMES":
                    item_groups[group]["name"] = str(child.value)
                elif child.name == "X-ABLABEL":
                    item_groups[group]["label"] = str(child.value)

        # Process the grouped items
        for group_data in item_groups.values():
            if "name" in group_data:
                identifier = group_data["name"]
                label = group_data.get("label", "related")

                # Normalize Apple's special label format: _$!<Type>!$_
                rel_type = self._normalize_apple_label(label)

                # Apple X-ABRELATEDNAMES typically contains text names
                id_type = self._classify_identifier(identifier)
                relations.append(RelatedContact(rel_type, identifier, id_type))

        return relations

    def _normalize_apple_label(self, label: str) -> str:
        """Normalize Apple's relationship label format.

        Apple uses _$!<Type>!$_ for standard types (e.g., _$!<Friend>!$_)
        and plain text for custom types.
        """
        # Check if it's Apple's special format
        if label.startswith("_$!<") and label.endswith(">!$_"):
            # Extract the type from _$!<Type>!$_
            rel_type = label[4:-4].lower()
        else:
            # Custom label, use as-is
            rel_type = label.lower()

        return rel_type

    def get_all_contacts(self) -> list[Contact]:
        """Get all parsed contacts."""
        return list(self.contacts.values())
