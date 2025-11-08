"""Dependency graph building utilities."""

from typing import Optional

from cli.services.task_service import TaskService
from cli.models.task import TaskFilters
from cli.models.common import Status
from cli.graph import DependencyGraph


async def build_workspace_dependency_graph(
    task_service: TaskService,
    workspace_id: int,
    status_filter: Optional[list[Status]] = None,
    priority_min: Optional[int] = None,
    labels_filter: Optional[list[str]] = None,
    phase_filter: Optional[str] = None,
    owner_filter: Optional[str] = None,
    max_depth: Optional[int] = None,
) -> DependencyGraph:
    """
    Build complete dependency graph for workspace.

    Fetches all tasks matching filters and their dependencies.
    """
    graph = DependencyGraph()

    # Fetch all tasks matching filters
    filters = TaskFilters(
        workspace_id=workspace_id,
        status=status_filter,
        priority_gte=priority_min,
        labels=labels_filter,
        phase=phase_filter,
        owner=owner_filter,
        limit=100,  # API max
        sort_by="priority",
        order="desc",
    )
    task_list = await task_service.list_tasks(filters)

    tasks = [task.model_dump() for task in task_list]

    if not tasks:
        return graph

    # Add all tasks as nodes
    for task in tasks:
        graph.add_task(task)

    # Fetch dependencies for each task
    for task in tasks:
        identifier = task.get("identifier", str(task.get("id")))
        try:
            # Fetch dependencies (tasks this depends on)
            dependencies = await task_service.get_task_dependencies(identifier)
            for dep in dependencies:
                # Convert Task model to dict
                dep_dict = dep.model_dump()
                dep_id = dep_dict.get("identifier", str(dep_dict.get("id")))
                # Add dependency edge
                graph.add_dependency(identifier, dep_id)

                # If dependency is not in graph yet, add it
                if dep_id not in graph.nodes:
                    graph.add_task(dep_dict)

        except Exception:
            # Skip if dependencies can't be fetched
            pass

    # Apply depth filter if specified
    if max_depth is not None:
        graph = graph.filter_by_depth(max_depth)

    return graph
