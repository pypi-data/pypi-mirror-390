from dataclasses import dataclass
from typing import Self, cast

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


class LabNotebookSortingOptions(
    IGenericEntitySortingOptions,
    INamedEntitySortingOptions,
    IModificationRecordSortingOptions,
):
    VERSION: Self = cast(Self, "VERSION")


@dataclass
class LabNotebookRequestParameter(
    EntityRequestParameter[LabNotebookSortingOptions],
    IPermissionedEntityRequest,
    IUniqueEntityRequest,
    INamedEntityRequest,
    IProjectBasedRequest,
    IVersionedEntityRequest[int],
    ILockableEntityRequest,
    ISignableEntityRequest,
):
    _orderByType = LabNotebookSortingOptions
