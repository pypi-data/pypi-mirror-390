from dataclasses import dataclass
from typing import Optional

from LOGS.Entity.EntityRequestParameter import (
    DefaultSortingOptions,
    EntityRequestParameter,
)


@dataclass
class MethodRequestParameter(EntityRequestParameter[DefaultSortingOptions]):
    _orderByType = DefaultSortingOptions

    name: Optional[str] = None
