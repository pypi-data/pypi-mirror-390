from __future__ import annotations

from typing import Protocol

from canaerospace.types import HookArgs, ParamCallbackArgs, ServicePollArgs, ServiceRequestArgs, ServiceResponseArgs


class HookCallback(Protocol):
    def __call__(self, args: HookArgs) -> None: ...


class ParamCallback(Protocol):
    def __call__(self, args: ParamCallbackArgs) -> None: ...


class ServicePollCallback(Protocol):
    def __call__(self, args: ServicePollArgs) -> None: ...


class ServiceRequestCallback(Protocol):
    def __call__(self, args: ServiceRequestArgs) -> None: ...


class ServiceResponseCallback(Protocol):
    def __call__(self, args: ServiceResponseArgs) -> None: ...
