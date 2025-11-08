"""Dependency graph data structure and algorithms for task visualization."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Optional


@dataclass
class TaskNode:
    """Represents a task node in the dependency graph."""

    identifier: str
    title: str
    status: str
    priority: int
    labels: List[str]
    owner_id: Optional[str] = None
    dependencies: List[str] = field(
        default_factory=lambda: []
    )  # Task IDs this depends on
    dependents: List[str] = field(
        default_factory=lambda: []
    )  # Task IDs that depend on this


class DependencyGraph:
    """Dependency graph for tasks."""

    def __init__(self) -> None:
        self.nodes: Dict[str, TaskNode] = {}
        self.edges: List[
            tuple[str, str]
        ] = []  # (from_task, to_task) - from depends on to

    def add_task(self, task: dict[str, Any]) -> None:
        """Add a task node to the graph."""
        identifier = task.get("identifier", str(task.get("id", "")))
        title = task.get("title", "")
        status = task.get("status", "backlog")
        priority = task.get("priority", 0)
        labels = task.get("labels", [])
        owner_id = task.get("owner_id")

        self.nodes[identifier] = TaskNode(
            identifier=identifier,
            title=title,
            status=status,
            priority=priority,
            labels=labels,
            owner_id=owner_id,
            dependencies=[],
            dependents=[],
        )

    def add_dependency(self, task_id: str, depends_on: str) -> None:
        """Add a dependency edge: task_id depends on depends_on."""
        if task_id in self.nodes and depends_on in self.nodes:
            # Add to dependencies list
            if depends_on not in self.nodes[task_id].dependencies:
                self.nodes[task_id].dependencies.append(depends_on)

            # Add to dependents list
            if task_id not in self.nodes[depends_on].dependents:
                self.nodes[depends_on].dependents.append(task_id)

            # Add edge
            edge = (task_id, depends_on)
            if edge not in self.edges:
                self.edges.append(edge)

    def find_cycles(self) -> List[List[str]]:
        """
        Detect circular dependencies using DFS.

        Returns list of cycles, where each cycle is a list of task identifiers.
        """
        cycles: List[List[str]] = []
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []

        def dfs(node_id: str) -> bool:
            """DFS to detect cycles. Returns True if cycle found."""
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)

            # Visit all dependencies
            if node_id in self.nodes:
                for dep_id in self.nodes[node_id].dependencies:
                    if dep_id not in visited:
                        if dfs(dep_id):
                            return True
                    elif dep_id in rec_stack:
                        # Cycle detected - extract the cycle
                        cycle_start = path.index(dep_id)
                        cycle = path[cycle_start:] + [dep_id]
                        cycles.append(cycle)
                        return True

            path.pop()
            rec_stack.remove(node_id)
            return False

        # Run DFS from each unvisited node
        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id)

        return cycles

    def find_orphans(self) -> List[str]:
        """Find tasks with no dependencies or dependents."""
        orphans: list[str] = []
        for node_id, node in self.nodes.items():
            if not node.dependencies and not node.dependents:
                orphans.append(node_id)
        return orphans

    def get_root_nodes(self) -> List[str]:
        """Get tasks with no dependencies (root nodes)."""
        roots: list[str] = []
        for node_id, node in self.nodes.items():
            if not node.dependencies:
                roots.append(node_id)
        return roots

    def topological_sort(self) -> List[str]:
        """
        Return tasks in topological order (dependency order).

        Uses Kahn's algorithm. If cycles exist, returns partial ordering.
        """
        # Calculate in-degree for each node
        in_degree: Dict[str, int] = {node_id: 0 for node_id in self.nodes}

        for node_id, node in self.nodes.items():
            in_degree[node_id] = len(node.dependencies)

        # Queue of nodes with no dependencies
        queue: List[str] = [
            node_id for node_id, degree in in_degree.items() if degree == 0
        ]
        result: List[str] = []

        while queue:
            # Sort queue by priority (highest first) for stable ordering
            queue.sort(
                key=lambda x: self.nodes[x].priority if x in self.nodes else 0,
                reverse=True,
            )
            node_id = queue.pop(0)
            result.append(node_id)

            # Reduce in-degree for dependents
            if node_id in self.nodes:
                for dependent_id in self.nodes[node_id].dependents:
                    in_degree[dependent_id] -= 1
                    if in_degree[dependent_id] == 0:
                        queue.append(dependent_id)

        return result

    def get_task_depth(self, task_id: str, max_depth: Optional[int] = None) -> int:
        """
        Calculate depth of a task in the dependency tree.

        Depth is the length of the longest path from a root node to this task.
        """
        if task_id not in self.nodes:
            return 0

        visited: Set[str] = set()

        def dfs_depth(node_id: str, current_depth: int) -> int:
            if max_depth is not None and current_depth >= max_depth:
                return current_depth

            if node_id in visited:
                return current_depth

            visited.add(node_id)

            if node_id not in self.nodes:
                return current_depth

            # If no dependencies, this is depth 0 (root)
            if not self.nodes[node_id].dependencies:
                return current_depth

            # Find max depth from dependencies
            max_dep_depth = current_depth
            for dep_id in self.nodes[node_id].dependencies:
                dep_depth = dfs_depth(dep_id, current_depth + 1)
                max_dep_depth = max(max_dep_depth, dep_depth)

            return max_dep_depth

        return dfs_depth(task_id, 0)

    def filter_by_depth(self, max_depth: int) -> "DependencyGraph":
        """
        Create a new graph containing only tasks within max_depth from root nodes.
        """
        filtered = DependencyGraph()

        # Add tasks within depth
        for node_id, node in self.nodes.items():
            depth = self.get_task_depth(node_id, max_depth)
            if depth <= max_depth:
                filtered.nodes[node_id] = node

        # Add edges for tasks in filtered graph
        for from_task, to_task in self.edges:
            if from_task in filtered.nodes and to_task in filtered.nodes:
                filtered.edges.append((from_task, to_task))

        return filtered
