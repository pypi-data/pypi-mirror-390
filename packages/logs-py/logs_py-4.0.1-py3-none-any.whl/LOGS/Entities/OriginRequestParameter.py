from dataclasses import dataclass
from typing import List, Optional, Sequence, Union
from uuid import UUID

from LOGS.Entity.EntityRequestParameter import (
    DefaultSortingOptions,
    EntityRequestParameter,
)
from LOGS.Interfaces.IEntryRecord import IEntryRecordRequest
from LOGS.Interfaces.IModificationRecord import IModificationRecordRequest
from LOGS.Interfaces.INamedEntity import INamedEntityRequest
from LOGS.Interfaces.IPermissionedEntity import IPermissionedEntityRequest


@dataclass
class OriginRequestParameter(
    EntityRequestParameter[DefaultSortingOptions],
    INamedEntityRequest,
    IModificationRecordRequest,
    IEntryRecordRequest,
    IPermissionedEntityRequest,
):
    _orderByType = DefaultSortingOptions

    urls: Optional[List[str]] = None
    uids: Optional[Sequence[Union[UUID, str]]] = None
