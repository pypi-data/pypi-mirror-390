from datetime import datetime
from enum import IntEnum
import logging
from typing import Annotated, Literal, Optional, Union

import pydantic

logger = logging.getLogger("agpsd")

class Mode(IntEnum):
    unknown = 0
    no_fix = 1
    fix2D = 2
    fix3D = 3


class Watch(pydantic.BaseModel):
    class_: Literal["WATCH"] = pydantic.Field("WATCH", alias="class")
    enable: bool = True
    json_: bool = pydantic.Field(True, alias="json")
    split24: bool = False
    raw: int = 0

    model_config = {
        'extra': 'allow'
    }


class Version(pydantic.BaseModel):
    class_: Literal["VERSION"] = pydantic.Field("VERSION", alias="class")
    release: str
    rev: str
    proto_major: int
    proto_minor: int

    @property
    def proto(self) -> tuple[int, int]:
        return self.proto_major, self.proto_minor


class Device(pydantic.BaseModel):
    class_: Literal["DEVICE"] = pydantic.Field("DEVICE", alias="class")
    path: str
    activated: datetime
    native: int
    bps: int
    parity: str
    stopbits: int
    cycle: float
    flags: int = 0
    driver: Optional[str] = None
    subtype: Optional[str] = None
    mincycle: Optional[float] = None


class Devices(pydantic.BaseModel):
    class_: Literal["DEVICES"] = pydantic.Field("DEVICES", alias="class")
    devices: list[Device]


class TPV(pydantic.BaseModel):
    class_: Literal["TPV"] = pydantic.Field("TPV", alias="class")
    device: str
    mode: Mode
    time: Optional[datetime] = None  # only inside POLL messages the time is empty
    leapseconds: int = 0
    # if the GNSS sensor does not have fix, following fields will be missing
    lat: Optional[float] = None
    lon: Optional[float] = None
    altHAE: Optional[float] = None
    altMSL: Optional[float] = None
    alt: Optional[float] = None
    magvar: Optional[float] = None
    speed: Optional[float] = None
    geoidSep: Optional[float] = None
    sep: Optional[float] = None
    ept: Optional[float] = None
    eps: Optional[float] = None
    epc: Optional[float] = None
    eph: Optional[float] = None
    epx: Optional[float] = None
    epy: Optional[float] = None
    epv: Optional[float] = None
    track: Optional[float] = None
    magtrack: Optional[float] = None
    climb: Optional[float] = None


class PRN(pydantic.BaseModel):
    PRN: int
    el: float
    az: float
    ss: float
    used: bool
    gnssid: int
    svid: int
    used: bool


class Sky(pydantic.BaseModel):
    class_: Literal["SKY"] = pydantic.Field("SKY", alias="class")
    device: str
    xdop: Optional[float] = None
    nSat: Optional[int] = None
    uSat: Optional[int] = None
    ydop: Optional[float] = None
    vdop: Optional[float] = None
    tdop: Optional[float] = None
    hdop: Optional[float] = None
    pdop: Optional[float] = None
    gdop: Optional[float] = None
    satellites: list[PRN] = []


class Poll(pydantic.BaseModel):
    class_: Literal["POLL"] = pydantic.Field("POLL", alias="class")
    time: datetime
    active: int
    tpv: list[TPV]
    sky: list[Sky]


AnyGPSDMessage = Union[Sky, TPV, Device, Devices, Version, Watch, Poll]
RuntimeGPSDMessage = Union[Sky, TPV]

Message = pydantic.RootModel[Annotated[AnyGPSDMessage, pydantic.Field(discriminator="class_")]]

def parse(data: str) -> AnyGPSDMessage:
    logger.debug("Message %s", data)
    return Message.model_validate_json(data).root
