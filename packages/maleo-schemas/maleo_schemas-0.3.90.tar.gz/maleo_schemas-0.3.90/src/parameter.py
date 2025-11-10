from pydantic import Field
from typing import Annotated, Generic
from maleo.enums.status import (
    ListOfDataStatuses,
    SimpleDataStatusesMixin,
    FULL_DATA_STATUSES,
)
from .mixins.filter import DateFilters
from .mixins.identity import IdentifierMixin, IdentifierT
from .mixins.parameter import (
    Search,
    UseCache,
)
from .mixins.sort import SortColumns
from .operation.action.status import StatusUpdateOperationAction
from .pagination import BaseFlexiblePagination, BaseStrictPagination


class ReadSingleParameter(
    SimpleDataStatusesMixin[ListOfDataStatuses],
    UseCache,
    IdentifierMixin[IdentifierT],
    Generic[IdentifierT],
):
    statuses: Annotated[
        ListOfDataStatuses,
        Field(FULL_DATA_STATUSES, description="Data statuses", min_length=1),
    ] = FULL_DATA_STATUSES


class BaseReadMultipleParameter(
    SortColumns,
    Search,
    SimpleDataStatusesMixin[ListOfDataStatuses],
    DateFilters,
    UseCache,
):
    statuses: Annotated[
        ListOfDataStatuses,
        Field(FULL_DATA_STATUSES, description="Data statuses", min_length=1),
    ] = FULL_DATA_STATUSES


class ReadUnpaginatedMultipleParameter(
    BaseFlexiblePagination,
    BaseReadMultipleParameter,
):
    pass


class ReadPaginatedMultipleParameter(
    BaseStrictPagination,
    BaseReadMultipleParameter,
):
    pass


class StatusUpdateParameter(
    StatusUpdateOperationAction,
    IdentifierMixin[IdentifierT],
    Generic[IdentifierT],
):
    pass


class DeleteSingleParameter(
    IdentifierMixin[IdentifierT],
    Generic[IdentifierT],
):
    pass
