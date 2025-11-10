from typing import Generic, Literal
from maleo.types.boolean import BoolT
from ..connection import OptConnectionContext
from ..error import (
    OptAnyErrorT,
    AnyErrorT,
)
from ..response import OptResponseT, ErrorResponseT, OptSuccessResponseT
from .action.websocket import WebSocketOperationAction
from .base import BaseOperation
from .enums import OperationType


class WebSocketOperation(
    BaseOperation[
        WebSocketOperationAction,
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
    type: OperationType = OperationType.WEBSOCKET
    resource: None = None
    response_context: None = None


class FailedWebSocketOperation(
    WebSocketOperation[
        Literal[False],
        AnyErrorT,
        ErrorResponseT,
    ],
    Generic[AnyErrorT, ErrorResponseT],
):
    success: Literal[False] = False


class SuccessfulWebSocketOperation(
    WebSocketOperation[
        Literal[True],
        None,
        OptSuccessResponseT,
    ],
    Generic[OptSuccessResponseT],
):
    success: Literal[True] = True
    error: None = None
