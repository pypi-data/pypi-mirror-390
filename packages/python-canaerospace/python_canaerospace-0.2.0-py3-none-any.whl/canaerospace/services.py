from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .datatypes import pack
from .enums import DataType, ServiceCode
from .frame import CANASMessage


@dataclass
class IDSInfo:
    node_id: int
    hw_rev: int = 0
    sw_rev: int = 0
    identifier_distribution: int = 0
    header_type: int = 0


class NodeServiceHandler:

    def __init__(self,
                 callback: Callable[[CANASMessage], None],
                 node_id: int,
                 channel_base: int = 0x080) -> None:
        self._callback = callback
        self._node_id = node_id
        self._channel_base = channel_base
        self._ids = IDSInfo(node_id=node_id)
        self._handlers: dict[int, Callable[[CANASMessage], CANASMessage | None]] = {
            ServiceCode.IDS.value: self._handle_ids,
            ServiceCode.NSS.value: self._handle_nss,
            ServiceCode.NIS.value: self._handle_nis,
            ServiceCode.CSS.value: self._handle_css,
            ServiceCode.DDS.value: self._handle_dds,
            ServiceCode.DUS.value: self._handle_dus,
            ServiceCode.SCS.value: self._handle_scs,
            ServiceCode.TIS.value: self._handle_tis,
            ServiceCode.FPS.value: self._handle_fps,
            ServiceCode.STS.value: self._handle_sts,
            ServiceCode.FSS.value: self._handle_fss,
            ServiceCode.TCS.value: self._handle_tcs,
            ServiceCode.BSS.value: self._handle_bss,
            ServiceCode.MIS.value: self._handle_mis,
            ServiceCode.MCS.value: self._handle_mcs,
            ServiceCode.DIS.value: self._handle_dss
        }

    def set_ids_info(self, *,
                     hw_rev: int,
                     sw_rev: int,
                     identifier_distribution: int = 0,
                     header_type: int = 0) -> None:
        self._ids.hw_rev = hw_rev & 0xFF
        self._ids.sw_rev = sw_rev & 0xFF
        self._ids.identifier_distribution = identifier_distribution & 0xFF
        self._ids.header_type = header_type & 0xFF

    def on_request(self, request: CANASMessage) -> None:
        fn = self._handlers.get(request.service_code)
        if fn is None:
            return
        resp = fn(request)
        if resp:
            self._callback(resp)

    @staticmethod
    def _reply(
            request: CANASMessage, *,
            data_type: DataType,
            service_code: int,
            message_code: int,
            payload: bytes = None) -> CANASMessage:
        return CANASMessage(
            can_id=request.can_id + 1,
            node_id=request.node_id,
            data_type=data_type,
            service_code=service_code,
            message_code=message_code,
            data=payload
        )

    def _handle_ids(self, request: CANASMessage) -> CANASMessage:
        payload = bytes([self._ids.hw_rev, self._ids.sw_rev,
                        self._ids.identifier_distribution, self._ids.header_type])
        return self._reply(
            request=request,
            data_type=DataType.UCHAR4,
            service_code=ServiceCode.IDS.value,
            message_code=request.message_code,
            payload=payload)

    def _handle_nss(self, request: CANASMessage) -> CANASMessage:
        return self._reply(
            request=request,
            data_type=DataType.NODATA,
            service_code=ServiceCode.NSS.value,
            message_code=request.message_code,
            payload=pack(DataType.NODATA, )
        )

    def _handle_dds(self, request: CANASMessage) -> CANASMessage:
        return self._reply(
            request=request,
            data_type=DataType.LONG,
            service_code=ServiceCode.DDS.value,
            message_code=request.message_code,
            payload=pack(DataType.LONG, 0)
        )

    def _handle_dus(self, request: CANASMessage) -> CANASMessage:
        return self._reply(
            request=request,
            data_type=DataType.LONG,
            service_code=ServiceCode.DUS.value,
            message_code=request.message_code,
            payload=pack(DataType.LONG, 0)
        )

    def _handle_scs(self, request: CANASMessage) -> CANASMessage:
        return self._reply(
            request=request,
            data_type=request.data_type,
            service_code=ServiceCode.SCS.value,
            message_code=request.message_code,
            payload=pack(request.data_type, 0)
        )

    def _handle_css(self, request: CANASMessage) -> CANASMessage:
        return self._reply(
            request=request,
            data_type=DataType.NODATA,
            service_code=ServiceCode.CSS.value,
            message_code=request.message_code,
            payload=pack(DataType.NODATA, )
        )

    def _handle_tis(self, request: CANASMessage) -> CANASMessage:
        return self._reply(
            request=request,
            data_type=DataType.NODATA,
            service_code=ServiceCode.TIS.value,
            message_code=0,
            payload=pack(DataType.NODATA, )
        )

    def _handle_fps(self, request: CANASMessage) -> CANASMessage:
        return self._reply(
            request=request,
            data_type=DataType.NODATA,
            service_code=ServiceCode.FPS.value,
            message_code=0
        )

    def _handle_sts(self, request: CANASMessage) -> CANASMessage:
        return self._reply(
            request=request,
            data_type=DataType.NODATA,
            service_code=ServiceCode.STS.value,
            message_code=0,
            payload=pack(DataType.NODATA, )
        )

    def _handle_fss(self, request: CANASMessage) -> CANASMessage:
        return self._reply(
            request=request,
            data_type=DataType.NODATA,
            service_code=ServiceCode.FSS.value,
            message_code=0,
            payload=pack(DataType.NODATA, )
        )

    def _handle_tcs(self, request: CANASMessage) -> CANASMessage:
        return self._reply(
            request=request,
            data_type=request.data_type,
            service_code=ServiceCode.TCS.value,
            message_code=request.message_code,
            payload=pack(request.data_type, 0)
        )

    def _handle_bss(self, request: CANASMessage) -> CANASMessage:
        return self._reply(
            request=request,
            data_type=DataType.NODATA,
            service_code=ServiceCode.BSS.value,
            message_code=-1,
            payload=pack(DataType.NODATA, )
        )

    def _handle_nis(self, request: CANASMessage) -> CANASMessage:
        return self._reply(
            request=request,
            data_type=DataType.NODATA,
            service_code=ServiceCode.NIS.value,
            message_code=0,
            payload=pack(DataType.NODATA, )
        )

    def _handle_mis(self, request: CANASMessage) -> CANASMessage:
        return self._reply(
            request=request,
            data_type=request.data_type,
            service_code=ServiceCode.MIS.value,
            message_code=request.message_code,
            payload=pack(request.data_type, 0)
        )

    def _handle_mcs(self, request: CANASMessage) -> CANASMessage:
        return self._reply(
            request=request,
            data_type=request.data_type,
            service_code=ServiceCode.MCS.value,
            message_code=request.message_code,
            payload=pack(request.data_type, 0)
        )

    def _handle_dss(self, request: CANASMessage) -> CANASMessage:
        return self._reply(
            request=request,
            data_type=DataType.NODATA,
            service_code=ServiceCode.DIS.value,
            message_code=0,
            payload=pack(DataType.NODATA, )
        )
