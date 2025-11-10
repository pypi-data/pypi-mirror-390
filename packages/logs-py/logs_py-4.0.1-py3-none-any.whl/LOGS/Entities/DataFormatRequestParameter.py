from dataclasses import dataclass
from typing import List, Optional

from LOGS.Entity.EntityRequestParameter import (
    DefaultSortingOptions,
    EntityRequestParameter,
)


@dataclass
class DataFormatRequestParameter(EntityRequestParameter[DefaultSortingOptions]):
    _orderByType = DefaultSortingOptions

    name: Optional[str] = None
    vendors: Optional[List[str]] = None
    vendors: Optional[List[str]] = None
    methods: Optional[List[str]] = None
    formats: Optional[List[str]] = None
    instruments: Optional[List[str]] = None
