from typing import List

from bioblend.galaxy.objects import wrappers
from django.db import models

from django_to_galaxy.schemas.dataset import SimpleDataset
from .galaxy_element import GalaxyElement


class History(GalaxyElement):
    """Table for Galaxy history."""

    galaxy_state = models.CharField(max_length=100)
    """State on the galaxy side."""
    galaxy_owner = models.ForeignKey(
        "GalaxyUser", null=False, on_delete=models.CASCADE, related_name="histories"
    )
    """Galaxy user that owns the workflow."""
    create_time = models.DateTimeField()
    """Time the invocation was created."""

    @property
    def galaxy_history(self) -> wrappers.History:
        """Galaxy object using bioblend."""
        if getattr(self, "_galaxy_history", None) is None:
            self._galaxy_history = self._get_galaxy_history()
        return self._galaxy_history

    def _get_galaxy_history(self) -> wrappers.History:
        """Get galaxy object using bioblend."""
        return self.galaxy_owner.obj_gi.histories.get(self.galaxy_id)

    @property
    def simplify_datasets(self) -> List[SimpleDataset]:
        """Simplified version of datasets from history."""
        if getattr(self, "_simplify_datasets", None) is None:
            self._simplify_datasets = self._get_simplified_datasets()
        return self._simplify_datasets

    def _get_simplified_datasets(self) -> List[SimpleDataset]:
        """Get simplified version of datasets from history."""
        return [
            SimpleDataset(**dataset.wrapped)
            for dataset in self.galaxy_history.get_datasets()
        ]

    def delete(self, **kwargs):
        """Overloaded method to also delete history on Galaxy side."""
        self.galaxy_owner.obj_gi.histories.delete(id_=self.galaxy_id, purge=True)
        return super().delete(**kwargs)

    def synchronize(self):
        """Synchronize data from Galaxy instance."""
        galaxy_history = self._get_galaxy_history()
        self.name = galaxy_history.name
        self.published = galaxy_history.published
        self.galaxy_state = galaxy_history.state
        if self.galaxy_history.annotation is not None:
            self.annotation = galaxy_history.annotation
        self.save()

    def upload_file(
        self, file_path: str, **kwargs
    ) -> wrappers.HistoryDatasetAssociation:
        """Upload file to history."""
        return self.galaxy_history.upload_file(file_path, **kwargs)

    def __repr__(self):
        return f"History: {super().__str__()}"

    class Meta:
        verbose_name_plural = "Histories"
        unique_together = ("galaxy_id", "galaxy_owner")
