"""Label service with business logic for label operations."""

from cli.client.labels import LabelsAPIClient
from cli.models.label import Label, LabelCreate, LabelUpdate
from cli.services.base import BaseService


class LabelService(BaseService):
    """Business logic for label operations.

    LabelService encapsulates business rules and workflows for label
    management, including:
    - Listing labels in a workspace
    - Creating, updating, and deleting labels
    - Label validation
    - Label color management

    Example:
        ```python
        service = LabelService.from_config()

        # List labels in workspace
        labels = await service.list_labels(workspace_id=123)

        # Create a new label
        label = await service.create_label(
            workspace_id=123,
            label=LabelCreate(name="bug", color="#FF0000")
        )

        # Update a label
        updated = await service.update_label(
            workspace_id=123,
            label_id=1,
            updates=LabelUpdate(color="#00FF00")
        )
        ```
    """

    labels: LabelsAPIClient

    def _init_clients(self) -> None:
        """Initialize API clients."""
        self.labels = LabelsAPIClient.from_config()

    async def list_labels(self, workspace_id: int) -> list[Label]:
        """List labels in a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            List of Label objects

        Raises:
            APIError: On HTTP errors
        """
        return await self.labels.list_labels(workspace_id)

    async def create_label(self, workspace_id: int, label: LabelCreate) -> Label:
        """Create a new label in a workspace.

        Args:
            workspace_id: Workspace ID
            label: Label creation data

        Returns:
            Created Label object

        Raises:
            ValidationError: If label data is invalid
            ConflictError: If label name already exists
            APIError: On other HTTP errors
        """
        return await self.labels.create_label(workspace_id, label)

    async def get_label(self, workspace_id: int, label_id: int) -> Label:
        """Get a specific label by ID.

        Args:
            workspace_id: Workspace ID
            label_id: Label ID

        Returns:
            Label object

        Raises:
            NotFoundError: If label not found
            APIError: On other HTTP errors
        """
        return await self.labels.get_label(workspace_id, label_id)

    async def update_label(
        self, workspace_id: int, label_id: int, updates: LabelUpdate
    ) -> Label:
        """Update a label.

        Args:
            workspace_id: Workspace ID
            label_id: Label ID
            updates: Label update data

        Returns:
            Updated Label object

        Raises:
            NotFoundError: If label not found
            ValidationError: If update data is invalid
            ConflictError: If name already exists
            APIError: On other HTTP errors
        """
        return await self.labels.update_label(workspace_id, label_id, updates)

    async def delete_label(self, workspace_id: int, label_id: int) -> None:
        """Delete a label.

        Args:
            workspace_id: Workspace ID
            label_id: Label ID

        Raises:
            NotFoundError: If label not found
            APIError: On other HTTP errors
        """
        await self.labels.delete_label(workspace_id, label_id)
