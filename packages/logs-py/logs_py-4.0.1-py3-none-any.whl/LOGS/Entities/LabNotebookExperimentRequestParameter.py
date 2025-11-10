from dataclasses import dataclass
from typing import List, Optional, Self, cast

from LOGS.Entities.LabNotebookModels import LabNotebookExperimentStatus
from LOGS.Entity.EntityRequestParameter import EntityRequestParameter
from LOGS.Entity.IGenericEntityOrderBy import (
    IGenericEntitySortingOptions,
    IModificationRecordSortingOptions,
    INamedEntitySortingOptions,
)
from LOGS.Interfaces.ILockableEntity import ILockableEntityRequest
from LOGS.Interfaces.INamedEntity import INamedEntityRequest
from LOGS.Interfaces.IPermissionedEntity import IPermissionedEntityRequest
from LOGS.Interfaces.IProjectBased import IProjectBasedRequest
from LOGS.Interfaces.ISignableEntity import ISignableEntityRequest
from LOGS.Interfaces.IUniqueEntity import IUniqueEntityRequest
from LOGS.Interfaces.IVersionedEntity import IVersionedEntityRequest


class LabNotebookExperimentSortingOptions(
    IGenericEntitySortingOptions,
    INamedEntitySortingOptions,
    IModificationRecordSortingOptions,
):
    STATUS: Self = cast(Self, "STATUS")
    VERSION: Self = cast(Self, "VERSION")
    LAB_NOTEBOOK_ID: Self = cast(Self, "LAB_NOTEBOOK_ID")
    LAB_NOTEBOOK_NAME: Self = cast(Self, "LAB_NOTEBOOK_NAME")
    LAB_NOTEBOOK_EXPERIMENT_ID: Self = cast(Self, "LAB_NOTEBOOK_EXPERIMENT_ID")
    LAB_NOTEBOOK_EXPERIMENT_NAME: Self = cast(Self, "LAB_NOTEBOOK_EXPERIMENT_NAME")


@dataclass
class LabNotebookExperimentRequestParameter(
    EntityRequestParameter[LabNotebookExperimentSortingOptions],
    IPermissionedEntityRequest,
    IUniqueEntityRequest,
    INamedEntityRequest,
    IProjectBasedRequest,
    ILockableEntityRequest,
    ISignableEntityRequest,
    IVersionedEntityRequest[int],
):
    _orderByType = LabNotebookExperimentSortingOptions

    status: Optional[List[LabNotebookExperimentStatus]] = None
    labNotebookIds: Optional[List[int]] = None
    labNotebookProjectIds: Optional[List[int]] = None
