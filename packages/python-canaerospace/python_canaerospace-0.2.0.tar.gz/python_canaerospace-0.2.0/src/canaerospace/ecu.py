from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .directory import IdentifierDirectory, ParameterDef
from .frame import CANASMessage, build


@dataclass
class Parameter:
    name: str
    param_def: ParameterDef
    message_code: int = 0
    service_code: int = 0


class ECU:
    def __init__(self, node_id: int, directory: IdentifierDirectory, transmitter: Callable[[CANASMessage], None]):
        self._node_id = node_id
        self._directory = directory
        self._transmitter = transmitter
        self._params: dict[str, Parameter] = {}

    def _has_param(self, name: str) -> bool:
        return name in self._params

    def register(self, name: str):
        self._params[name] = Parameter(
            name=name, param_def=self._directory.by_name(name))

    def unregister(self, name: str) -> Parameter | None:
        if not self._has_param(name):
            return
        return self._params.pop(name)

    def set(self, name: str, *values: int | float) -> CANASMessage:
        param = self._params[name]
        param.message_code = (param.message_code + 1) & 0xFF

        msg = build(
            can_id=param.param_def.can_id,
            node_id=self._node_id,
            data_type=param.param_def.data_type,
            service_code=param.service_code,
            message_code=param.message_code,
            values=values
        )
        self._transmitter(msg)
        return msg

    def handle_receive(self, msg: CANASMessage) -> Parameter | None:
        """ @TODO Send a message system wide that a new message was received for event driven support"""
        try:
            definition = self._directory.by_id(msg.can_id)
        except KeyError:
            return None  # No available definition for the can_id in the frame

        if not self._has_param(definition.name):
            param = Parameter(name=definition.name, param_def=definition)
            self._params[definition.name] = param
        else:
            param = self._params.get(definition.name)

        param.message_code = msg.message_code
        param.service_code = msg.service_code
        return param
