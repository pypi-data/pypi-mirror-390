from dataclasses import dataclass
from typing import List, Optional, Sequence, Union
from uuid import UUID

from LOGS.Entity.EntityRequestParameter import (
    DefaultSortingOptions,
    EntityRequestParameter,
)


@dataclass
class EntitiesRequestParameter(EntityRequestParameter[DefaultSortingOptions]):
    _orderByType = DefaultSortingOptions

    uids: Optional[Sequence[Union[str, UUID]]] = None
    names: Optional[List[str]] = None
