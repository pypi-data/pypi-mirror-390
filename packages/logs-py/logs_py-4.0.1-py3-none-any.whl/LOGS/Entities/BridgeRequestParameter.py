from dataclasses import dataclass
from typing import List, Optional, Self, cast

from LOGS.Entities.BridgeType import BridgeType
from LOGS.Entity.EntityRequestParameter import EntityRequestParameter
from LOGS.Entity.IGenericEntityOrderBy import (
    IEntryRecordSortingOptions,
    IGenericEntitySortingOptions,
    IModificationRecordSortingOptions,
    INamedEntitySortingOptions,
)
from LOGS.Interfaces.IEntryRecord import IEntryRecordRequest
from LOGS.Interfaces.IModificationRecord import IModificationRecordRequest
from LOGS.Interfaces.INamedEntity import INamedEntityRequest
from LOGS.Interfaces.IPermissionedEntity import IPermissionedEntityRequest
from LOGS.Interfaces.IUniqueEntity import IUniqueEntityRequest


class BridgeSortingOptions(
    IGenericEntitySortingOptions,
    INamedEntitySortingOptions,
    IEntryRecordSortingOptions,
    IModificationRecordSortingOptions,
):
    TYPE: Self = cast(Self, "TYPE")


@dataclass
class BridgeRequestParameter(
    EntityRequestParameter[BridgeSortingOptions],
    INamedEntityRequest,
    IUniqueEntityRequest,
    IEntryRecordRequest,
    IModificationRecordRequest,
    IPermissionedEntityRequest,
):
    _orderByType = BridgeSortingOptions

    hostnames: Optional[List[str]] = None
    usernames: Optional[List[str]] = None
    ipAddresses: Optional[List[str]] = None
    dataSourceIds: Optional[List[int]] = None
    types: Optional[List[BridgeType]] = None
    datasetIds: Optional[List[int]] = None
    isConfigured: Optional[bool] = None
