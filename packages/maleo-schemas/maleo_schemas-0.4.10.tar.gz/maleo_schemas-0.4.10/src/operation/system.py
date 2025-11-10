from typing import Generic, Literal
from maleo.types.boolean import BoolT
from ..connection import OptConnectionContext
from ..error import (
    OptAnyErrorT,
    AnyErrorT,
)
from ..response import OptResponseT, ErrorResponseT, OptSuccessResponseT
from .action.system import SystemOperationAction
from .base import BaseOperation
from .enums import OperationType


class SystemOperation(
    BaseOperation[
        SystemOperationAction,
        None,
        BoolT,
        OptAnyErrorT,
        OptConnectionContext,
        OptResponseT,
        None,
    ],
    Generic[
        BoolT,
        OptAnyErrorT,
        OptResponseT,
    ],
):
    type: OperationType = OperationType.SYSTEM
    resource: None = None
    response_context: None = None


class FailedSystemOperation(
    SystemOperation[
        Literal[False],
        AnyErrorT,
        ErrorResponseT,
    ],
    Generic[AnyErrorT, ErrorResponseT],
):
    success: Literal[False] = False


class SuccessfulSystemOperation(
    SystemOperation[
        Literal[True],
        None,
        OptSuccessResponseT,
    ],
    Generic[OptSuccessResponseT],
):
    success: Literal[True] = True
    error: None = None
