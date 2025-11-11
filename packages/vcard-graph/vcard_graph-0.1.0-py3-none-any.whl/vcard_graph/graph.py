"""Build and visualize graph from vCard relationships."""

import logging
from typing import List, Optional

import networkx as nx
import plotly.graph_objects as go

from vcard_graph.parser import RelatedIdentifierType, VCardParser

logger = logging.getLogger(__name__)


class VCardGraph:
    """Build and visualize a graph from vCard contacts."""

    def __init__(self, warn_unmatched: bool = True) -> None:
        self.graph: nx.Graph = nx.Graph()
        self.parser = VCardParser()
        self.warn_unmatched = warn_unmatched
        self.unmatched_relations: list[tuple[str, str, str]] = []  # (contact, rel_type, identifier)

    def build_from_parser(self, parser: VCardParser) -> None:
        """Build graph from an existing parser."""
        self.parser = parser
        self._build_graph()

    def _build_graph(self) -> None:
        """Build the graph from parsed contacts."""
        contacts = self.parser.get_all_contacts()
        self.unmatched_relations = []  # Reset unmatched relations

        # Add all contacts as nodes
        for contact in contacts:
            self.graph.add_node(
                contact.uid,
                name=contact.name,
                email=contact.email,
                org=contact.org,
                node_type="person",
                categories=contact.categories,
            )

        # Add edges for relationships
        for contact in contacts:
            for related in contact.related:
                # Try to find the related contact by identifier
                target_node = self._find_contact_node(related.identifier, related.identifier_type)
                if target_node:
                    self.graph.add_edge(
                        contact.uid, target_node, relationship=related.relationship_type
                    )
                else:
                    # Track unmatched relation
                    self.unmatched_relations.append(
                        (contact.name, related.relationship_type, related.identifier)
                    )

                    # Warn if enabled and not a URI (URIs are expected to be external)
                    if self.warn_unmatched and related.identifier_type != RelatedIdentifierType.URI:
                        logger.warning(
                            "Could not find contact for %s relationship '%s' (type: %s) of %s",
                            related.relationship_type,
                            related.identifier,
                            related.identifier_type.value,
                            contact.name,
                        )

        # Add organization nodes and edges
        org_contacts: dict[str, List[str]] = {}
        for contact in contacts:
            if contact.org:
                if contact.org not in org_contacts:
                    org_contacts[contact.org] = []
                org_contacts[contact.org].append(contact.uid)

        # Add organization nodes
        for org_name, members in org_contacts.items():
            if len(members) > 1:  # Only add org node if multiple people share it
                org_node_id = f"org:{org_name}"
                self.graph.add_node(org_node_id, name=org_name, node_type="organization")
                for member_uid in members:
                    self.graph.add_edge(member_uid, org_node_id, relationship="member")

    def _find_contact_node(
        self, identifier: str, identifier_type: RelatedIdentifierType
    ) -> Optional[str]:
        """Find a contact node by identifier.

        Args:
            identifier: The identifier value (UID, email, name, URI, etc.)
            identifier_type: The type of identifier

        Returns:
            The node ID if found, None otherwise
        """
        # Handle different identifier types
        if identifier_type == RelatedIdentifierType.UID:
            # Direct UID match
            if identifier in self.graph.nodes:
                return str(identifier)

        elif identifier_type == RelatedIdentifierType.URN_UUID:
            # Extract UUID from urn:uuid: format
            uuid = identifier[9:] if identifier.startswith("urn:uuid:") else identifier
            if uuid in self.graph.nodes:
                return str(uuid)

        elif identifier_type == RelatedIdentifierType.EMAIL:
            # Match by email
            for node_id, node_data in self.graph.nodes(data=True):
                if node_data.get("node_type") != "person":
                    continue
                if node_data.get("email") == identifier:
                    return str(node_id)

        elif identifier_type == RelatedIdentifierType.TEXT:
            # Try to match by name or UID
            if identifier in self.graph.nodes:
                return str(identifier)

            for node_id, node_data in self.graph.nodes(data=True):
                if node_data.get("node_type") != "person":
                    continue
                if node_data.get("name") == identifier:
                    return str(node_id)

        elif identifier_type == RelatedIdentifierType.URI:
            # URIs typically can't be matched to contacts
            # They might point to external resources
            pass

        return None

    def visualize(self, output_file: str = "vcard_graph.html") -> None:
        """Create an interactive visualization of the graph."""
        if len(self.graph.nodes) == 0:
            raise ValueError("Graph is empty. Parse some vCard files first.")

        # Group nodes by category for better layout
        category_groups: dict[str, list[str]] = {}
        for node_id, node_data in self.graph.nodes(data=True):
            if node_data.get("node_type") == "person":
                categories = node_data.get("categories", [])
                # Use first category or "uncategorized"
                category = categories[0] if categories else "uncategorized"
                if category not in category_groups:
                    category_groups[category] = []
                category_groups[category].append(node_id)

        # Log category distribution for debugging
        if category_groups:
            logger.info("Category distribution:")
            for category, nodes in sorted(category_groups.items()):
                logger.info("  %s: %d contacts", category, len(nodes))

        # Use spring layout with category-based initial positions
        # This helps group nodes by category
        initial_pos = {}
        for i, (category, nodes) in enumerate(category_groups.items()):
            # Position each category in separate areas
            center_x = 10 * float(i - len(category_groups) / 2)
            center_y = 0
            for j, node_id in enumerate(nodes):
                # Spread nodes within the category
                initial_pos[node_id] = (
                    center_x + 2 * (j % 5 - 2),
                    center_y + 2 * (j // 5),
                )

        # Add organization and other non-person nodes
        for node_id in self.graph.nodes():
            if node_id not in initial_pos:
                initial_pos[node_id] = (0, 0)

        # Use spring layout for positioning with initial positions
        pos = nx.spring_layout(self.graph, pos=initial_pos, k=2, iterations=50)

        # Create edge traces
        edge_traces = []

        # Group edges by relationship type for different colors
        relationship_types: dict[str, List[tuple[str, str]]] = {}
        for edge in self.graph.edges(data=True):
            rel_type = edge[2].get("relationship", "related")
            if rel_type not in relationship_types:
                relationship_types[rel_type] = []
            relationship_types[rel_type].append((edge[0], edge[1]))

        # Color map for different relationship types
        rel_colors = {
            "spouse": "#FF1493",
            "partner": "#FF1493",
            "child": "#FFA500",
            "parent": "#4169E1",
            "mother": "#4169E1",
            "father": "#4169E1",
            "sibling": "#32CD32",
            "brother": "#32CD32",
            "sister": "#32CD32",
            "friend": "#FFD700",
            "colleague": "#9370DB",
            "assistant": "#9370DB",
            "manager": "#9370DB",
            "member": "#A9A9A9",
            "related": "#808080",
        }

        for rel_type, edges in relationship_types.items():
            edge_x = []
            edge_y = []
            for edge_tuple in edges:
                x0, y0 = pos[edge_tuple[0]]
                x1, y1 = pos[edge_tuple[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

            edge_trace = go.Scatter(
                x=edge_x,
                y=edge_y,
                mode="lines",
                line=dict(width=2, color=rel_colors.get(rel_type, "#808080")),
                hoverinfo="none",
                name=rel_type.capitalize(),
                showlegend=True,
            )
            edge_traces.append(edge_trace)

        # Create node traces grouped by category
        category_traces = []

        # Generate colors dynamically for all categories
        # Use a diverse color palette
        color_palette = [
            "#FF1493",  # deep pink
            "#FFD700",  # gold
            "#9370DB",  # medium purple
            "#FF6347",  # tomato red
            "#20B2AA",  # light sea green
            "#87CEEB",  # sky blue
            "#FF8C00",  # dark orange
            "#32CD32",  # lime green
            "#FF69B4",  # hot pink
            "#4169E1",  # royal blue
            "#DC143C",  # crimson
            "#00CED1",  # dark turquoise
            "#FF4500",  # orange red
            "#9932CC",  # dark orchid
            "#00FA9A",  # medium spring green
            "#FF1493",  # deep pink
            "#DAA520",  # goldenrod
            "#8B008B",  # dark magenta
            "#00BFFF",  # deep sky blue
            "#FF6347",  # tomato
        ]

        # Group people by category
        category_nodes: dict[str, dict[str, list]] = {}

        for node_id, node_data in self.graph.nodes(data=True):
            x, y = pos[node_id]
            name = node_data.get("name", node_id)
            node_type = node_data.get("node_type", "person")

            hover_text = f"<b>{name}</b>"
            if node_data.get("email"):
                hover_text += f"<br>Email: {node_data['email']}"
            if node_data.get("org") and node_type == "person":
                hover_text += f"<br>Org: {node_data['org']}"

            if node_type == "person":
                categories = node_data.get("categories", [])
                category = categories[0] if categories else "uncategorized"

                if categories:
                    hover_text += f"<br>Categories: {', '.join(categories)}"

                if category not in category_nodes:
                    category_nodes[category] = {
                        "x": [],
                        "y": [],
                        "text": [],
                        "hover": [],
                    }

                category_nodes[category]["x"].append(x)
                category_nodes[category]["y"].append(y)
                category_nodes[category]["text"].append(name)
                category_nodes[category]["hover"].append(hover_text)

        # Create traces for each category with dynamic colors
        # Assign colors from palette, cycling if needed
        categories_sorted = sorted(category_nodes.keys())
        for i, category in enumerate(categories_sorted):
            data = category_nodes[category]
            # Use uncategorized color for uncategorized, otherwise cycle through palette
            if category.lower() == "uncategorized":
                color = "#808080"  # gray
            else:
                color = color_palette[i % len(color_palette)]

            trace = go.Scatter(
                x=data["x"],
                y=data["y"],
                mode="markers+text",
                text=data["text"],
                textposition="top center",
                hovertext=data["hover"],
                hoverinfo="text",
                marker=dict(
                    size=20,
                    color=color,
                    line=dict(width=2, color="white"),
                ),
                name=category.capitalize(),
                showlegend=True,
            )
            category_traces.append(trace)

        # Create node trace for organizations
        org_node_x = []
        org_node_y = []
        org_node_text = []
        org_node_hover = []

        for node_id, node_data in self.graph.nodes(data=True):
            if node_data.get("node_type") == "organization":
                x, y = pos[node_id]
                name = node_data.get("name", node_id)
                hover_text = f"<b>{name}</b>"

                org_node_x.append(x)
                org_node_y.append(y)
                org_node_text.append(name)
                org_node_hover.append(hover_text)

        org_trace = go.Scatter(
            x=org_node_x,
            y=org_node_y,
            mode="markers+text",
            text=org_node_text,
            textposition="top center",
            hovertext=org_node_hover,
            hoverinfo="text",
            marker=dict(
                size=25,
                color="#FF6B6B",
                symbol="square",
                line=dict(width=2, color="white"),
            ),
            name="Organizations",
            showlegend=True,
        )

        # Create figure
        fig = go.Figure(
            data=edge_traces + category_traces + [org_trace],
            layout=go.Layout(
                title="vCard Contact Graph",
                showlegend=True,
                hovermode="closest",
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor="white",
            ),
        )

        fig.write_html(output_file)
        print(f"Graph visualization saved to {output_file}")

    def get_stats(self) -> dict[str, int]:
        """Get statistics about the graph."""
        person_count = sum(
            1 for _, data in self.graph.nodes(data=True) if data.get("node_type") == "person"
        )
        org_count = sum(
            1 for _, data in self.graph.nodes(data=True) if data.get("node_type") == "organization"
        )

        return {
            "total_nodes": self.graph.number_of_nodes(),
            "people": person_count,
            "organizations": org_count,
            "relationships": self.graph.number_of_edges(),
            "unmatched_relations": len(self.unmatched_relations),
        }

    def get_unmatched_relations(self) -> list[tuple[str, str, str]]:
        """Get list of unmatched relations.

        Returns:
            List of (contact_name, relationship_type, identifier) tuples
        """
        return self.unmatched_relations.copy()
