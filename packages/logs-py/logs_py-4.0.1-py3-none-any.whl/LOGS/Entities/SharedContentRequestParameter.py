from dataclasses import dataclass
from typing import List, Optional

from LOGS.Entity.EntityRequestParameter import EntityRequestParameter
from LOGS.Entity.IGenericEntityOrderBy import (
    IEntryRecordSortingOptions,
    IGenericEntitySortingOptions,
    IModificationRecordSortingOptions,
    INamedEntitySortingOptions,
)
from LOGS.Interfaces.IEntryRecord import IEntryRecordRequest
from LOGS.Interfaces.IModificationRecord import IModificationRecordRequest
from LOGS.Interfaces.IPermissionedEntity import IPermissionedEntityRequest
from LOGS.Interfaces.ISoftDeletable import ISoftDeletableRequest


class SharedContentSortingOptions(
    IGenericEntitySortingOptions,
    INamedEntitySortingOptions,
    IEntryRecordSortingOptions,
    IModificationRecordSortingOptions,
):
    pass


@dataclass
class SharedContentRequestParameter(
    EntityRequestParameter[SharedContentSortingOptions],
    ISoftDeletableRequest,
    IEntryRecordRequest,
    IModificationRecordRequest,
    IPermissionedEntityRequest,
):
    _orderByType = SharedContentSortingOptions

    datasetIds: Optional[List[int]] = None
