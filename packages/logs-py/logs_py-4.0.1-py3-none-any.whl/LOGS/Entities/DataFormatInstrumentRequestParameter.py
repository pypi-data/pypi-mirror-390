from dataclasses import dataclass

from LOGS.Entity.EntityRequestParameter import (
    DefaultSortingOptions,
    EntityRequestParameter,
)
from LOGS.Interfaces.INamedEntity import INamedEntityRequest


@dataclass
class DataFormatInstrumentRequestParameter(
    EntityRequestParameter[DefaultSortingOptions], INamedEntityRequest
):
    _orderByType = DefaultSortingOptions
