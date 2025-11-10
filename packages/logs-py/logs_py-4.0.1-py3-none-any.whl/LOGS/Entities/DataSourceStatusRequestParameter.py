from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Self, cast

from LOGS.Entities.BridgeType import BridgeType
from LOGS.Entities.RunState import RunState
from LOGS.Entity.EntityRequestParameter import EntityRequestParameter
from LOGS.Entity.IGenericEntityOrderBy import IGenericEntitySortingOptions


class DataSourceStatusSortingOptions(IGenericEntitySortingOptions):
    STARTED_ON: Self = cast(Self, "STARTED_ON")


@dataclass
class DataSourceStatusRequestParameter(
    EntityRequestParameter[DataSourceStatusSortingOptions]
):
    _orderByType = DataSourceStatusSortingOptions

    dataSourceIds: Optional[List[int]] = None
    types: Optional[List[BridgeType]] = None
    runStates: Optional[List[RunState]] = None
    durationInSecondsMin: Optional[float] = None
    durationInSecondsMax: Optional[float] = None
    startedOnFrom: Optional[datetime] = None
    startedOnTo: Optional[datetime] = None
