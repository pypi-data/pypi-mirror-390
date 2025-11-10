from dataclasses import dataclass
from typing import List, Optional

from LOGS.Entities.DatasetRequestParameter import ParsingStates
from LOGS.Entity.EntityRequestParameter import EntityRequestParameter
from LOGS.Entity.IGenericEntityOrderBy import (
    IEntryRecordSortingOptions,
    IGenericEntitySortingOptions,
    IModificationRecordSortingOptions,
)
from LOGS.Interfaces.IEntryRecord import IEntryRecordRequest
from LOGS.Interfaces.IModificationRecord import IModificationRecordRequest
from LOGS.Interfaces.INamedEntity import INamedEntityRequest
from LOGS.Interfaces.IUniqueEntity import IUniqueEntityRequest


class AttachmentSortingOptions(
    IGenericEntitySortingOptions,
    IEntryRecordSortingOptions,
    IModificationRecordSortingOptions,
):
    pass


@dataclass
class AttachmentRequestParameter(
    EntityRequestParameter[AttachmentSortingOptions],
    IUniqueEntityRequest,
    INamedEntityRequest,
    IEntryRecordRequest,
    IModificationRecordRequest,
):
    _orderByType = AttachmentSortingOptions

    parsingState: Optional[List[ParsingStates]] = None
    pathContains: Optional[str] = None

    # Additional fetch options
    includeInfo: Optional[bool] = None
    includeZipSize: Optional[bool] = None
