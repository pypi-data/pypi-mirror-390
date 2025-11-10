from enum import StrEnum

from pydantic import BaseModel, Field


class DescriptorData(BaseModel):
    lines: int = 0
    buffer_size: int = Field(0, alias="bufferSize")
    tick_resolution: int = Field(0, alias="tickResolution")
    max_yn_frame_size: int = Field(0, alias="maxYnFrameSize")
    implemented_macros: list[int] = Field([], alias="implementedMacros")
    device_list_specifier: int = Field(0, alias="deviceListSpecifier")
    protocol_version_major: int = Field(1, alias="protocolVersionMajor")
    protocol_version_minor: int = Field(0, alias="protocolVersionMinor")
    power_supply_implemented: bool = Field(False, alias="powerSupplyImplemented")


class DeviceInfoData(BaseModel):
    serial: int
    gtin: int
    pcb: str
    article_number: int = Field(alias="articleNumber")
    article_info: str = Field("", alias="articleInfo")
    production_year: int = Field(alias="productionYear")
    production_week: int = Field(alias="productionWeek")


class LineStatus(StrEnum):
    OK = "ok"
    LOW_POWER = "lowPower"
    NO_POWER = "noPower"


class DALIBusData(BaseModel):
    send_blocked_initialize: bool = Field(False, alias="sendBlockedInitialize")
    send_blocked_quiescent: bool = Field(False, alias="sendBlockedQuiescent")
    send_blocked_macro_running: bool = Field(False, alias="sendBlockedMacroRunning")
    send_buffer_full: bool = Field(False, alias="sendBufferFull")
    line_status: LineStatus = Field(LineStatus.OK, alias="lineStatus")
    device: DeviceInfoData


class InfoData(BaseModel):
    name: str
    version: str
    tier: str = "basic"
    emergency_light: bool = Field(False, alias="emergencyLight")
    node_red: bool = Field(False, alias="nodeRed")
    errors: dict[str, str] = {}
    descriptor: DescriptorData = DescriptorData()
    device: DeviceInfoData
    lines: dict[str, DALIBusData] = {}
