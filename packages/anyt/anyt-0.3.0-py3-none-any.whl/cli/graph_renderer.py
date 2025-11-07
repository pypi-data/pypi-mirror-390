"""Graph rendering utilities for ASCII and DOT format visualization."""

from typing import Any, List, Set
from cli.graph import DependencyGraph


def truncate_text(text: str, max_length: int) -> str:
    """Truncate text to max_length, adding ellipsis if needed."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 1] + "…"


def get_status_symbol(status: str) -> str:
    """Get symbol for task status."""
    symbols = {
        "done": "✓",
        "inprogress": "•",
        "active": "•",
        "backlog": "○",
        "todo": "○",
        "blocked": "⚠",
    }
    return symbols.get(status, "○")


def render_ascii_graph(graph: DependencyGraph, compact: bool = False) -> str:
    """
    Render dependency graph as ASCII art.

    Uses tree structure starting from root nodes (tasks with no dependencies).
    Handles multiple root nodes and orphaned tasks.
    """
    if not graph.nodes:
        return "No tasks in workspace"

    lines: List[str] = []
    visited: Set[str] = set()

    def render_tree(
        node_id: str, prefix: str = "", is_last: bool = True, depth: int = 0
    ) -> None:
        """Recursively render tree structure."""
        if node_id in visited:
            # Already rendered - show reference
            lines.append(
                f"{prefix}{'└─' if is_last else '├─'} ({node_id}) [shown above]"
            )
            return

        visited.add(node_id)

        if node_id not in graph.nodes:
            return

        node = graph.nodes[node_id]

        # Build node label
        status_sym = get_status_symbol(node.status)
        if compact:
            label = f"{node.identifier} {truncate_text(node.title, 30)} {status_sym}"
        else:
            label = f"{node.identifier} {truncate_text(node.title, 50)} {status_sym}"

        # Add to output
        connector = "└─" if is_last else "├─"
        lines.append(f"{prefix}{connector} {label}")

        # Render dependents (tasks that depend on this one)
        dependents = node.dependents
        if dependents:
            # Extend prefix for children
            extension = "   " if is_last else "│  "
            new_prefix = prefix + extension

            for i, dep_id in enumerate(dependents):
                is_last_child = i == len(dependents) - 1
                render_tree(dep_id, new_prefix, is_last_child, depth + 1)

    # Get root nodes (tasks with no dependencies)
    root_nodes = graph.get_root_nodes()

    if not root_nodes:
        # No clear roots - might have cycles or all tasks have dependencies
        # Start from any unvisited node
        lines.append(
            "[yellow]Warning: No root tasks found (possible circular dependencies)[/yellow]"
        )
        lines.append("")
        root_nodes = list(graph.nodes.keys())[:5]  # Show first 5

    # Render each root tree
    for i, root_id in enumerate(root_nodes):
        if root_id not in visited:
            is_last_root = i == len(root_nodes) - 1
            render_tree(root_id, "", is_last_root)

    # Find orphans (tasks not connected to anything)
    orphans = graph.find_orphans()
    if orphans:
        lines.append("")
        lines.append("Orphaned tasks (no dependencies):")
        for orphan_id in orphans:
            if orphan_id in graph.nodes:
                node = graph.nodes[orphan_id]
                status_sym = get_status_symbol(node.status)
                label = (
                    f"{node.identifier} {truncate_text(node.title, 50)} {status_sym}"
                )
                lines.append(f"  • {label}")

    # Add legend
    lines.append("")
    lines.append("Legend: ✓ done  • active  ○ backlog  ⚠ blocked")

    return "\n".join(lines)


def render_dot_graph(graph: DependencyGraph) -> str:
    """
    Generate Graphviz DOT format for dependency graph.

    Output can be piped to `dot` command:
        anyt graph --format dot | dot -Tpng > graph.png
    """
    if not graph.nodes:
        return "digraph dependencies { }"

    lines: List[str] = []
    lines.append("digraph dependencies {")
    lines.append("    rankdir=LR;")
    lines.append("    node [shape=box, style=rounded];")
    lines.append("")

    # Define status colors
    status_colors = {
        "done": "lightgreen",
        "inprogress": "lightyellow",
        "active": "lightyellow",
        "backlog": "lightblue",
        "todo": "lightblue",
        "blocked": "lightcoral",
    }

    # Add nodes
    for node_id, node in graph.nodes.items():
        color = status_colors.get(node.status, "lightgray")
        title_short = truncate_text(node.title, 30).replace('"', '\\"')
        label = f"{node.identifier}\\n{title_short}"

        # Add priority badge if high priority
        if node.priority >= 1:
            label += f"\\n[P{node.priority}]"

        lines.append(
            f'    "{node_id}" [label="{label}", fillcolor={color}, style="filled,rounded"];'
        )

    lines.append("")

    # Add edges (dependencies)
    for from_task, to_task in graph.edges:
        # Edge goes from dependent task to dependency (from depends on to)
        lines.append(f'    "{from_task}" -> "{to_task}";')

    lines.append("}")

    return "\n".join(lines)


def render_json_graph(graph: DependencyGraph) -> dict[str, Any]:
    """
    Render graph as JSON-serializable dictionary.

    Returns structured data suitable for JSON output.
    """
    # Build nodes list
    nodes: list[dict[str, Any]] = []
    for node_id, node in graph.nodes.items():
        nodes.append(
            {
                "identifier": node.identifier,
                "title": node.title,
                "status": node.status,
                "priority": node.priority,
                "labels": node.labels,
                "owner_id": node.owner_id,
                "dependencies": node.dependencies,
                "dependents": node.dependents,
            }
        )

    # Build edges list
    edges = [{"from": from_task, "to": to_task} for from_task, to_task in graph.edges]

    # Find cycles
    cycles = graph.find_cycles()

    # Find orphans
    orphans = graph.find_orphans()

    # Calculate some metadata
    total_tasks = len(graph.nodes)
    total_edges = len(graph.edges)
    root_nodes = graph.get_root_nodes()

    return {
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "total_tasks": total_tasks,
            "total_edges": total_edges,
            "root_nodes": root_nodes,
            "orphaned_tasks": orphans,
            "circular_dependencies": cycles,
        },
    }
