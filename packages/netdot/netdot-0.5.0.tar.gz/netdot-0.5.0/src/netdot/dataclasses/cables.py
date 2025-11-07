from dataclasses import dataclass
from typing import Union

import netdot
from netdot import parse
from netdot.csv_util import CSVDataclass
from netdot.dataclasses.base import NetdotAPIDataclass


@dataclass
class HorizontalCable(NetdotAPIDataclass, CSVDataclass):
    account: str = None
    closet: Union[str,'netdot.Closet'] = None
    closet_xlink: int = None
    contactlist: Union[str,'netdot.ContactList'] = None
    contactlist_xlink: int = None
    datetested: parse.DateTime = None
    faceplateid: str = None
    info: str = None
    installdate: parse.DateTime = None
    jackid: str = None
    length: str = None
    room: Union[str,'netdot.Room'] = None
    room_xlink: int = None
    testpassed: bool = False
    type: Union[str,'netdot.CableType'] = None
    type_xlink: int = None


@dataclass
class BackboneCable(NetdotAPIDataclass, CSVDataclass):
    end_closet: Union[str,'netdot.Closet'] = None
    end_closet_xlink: int = None
    info: str = None
    installdate: parse.DateTime = None
    length: str = None
    name: str = None
    owner: Union[str,'netdot.Entity'] = None
    owner_xlink: int = None
    start_closet: Union[str,'netdot.Closet'] = None
    start_closet_xlink: int = None
    type: Union[str,'netdot.CableType'] = None
    type_xlink: int = None


@dataclass
class Circuit(NetdotAPIDataclass, CSVDataclass):
    cid: str = None
    info: str = None
    installdate: parse.DateTime = None
    linkid: Union[str,'netdot.SiteLink'] = None
    linkid_xlink: int = None
    speed: str = None
    status: Union[str,'netdot.CircuitStatus'] = None
    status_xlink: int = None
    type: Union[str,'netdot.CircuitType'] = None
    type_xlink: int = None
    vendor: Union[str,'netdot.Entity'] = None
    vendor_xlink: int = None
    datetested: parse.DateTime = None
    loss: str = None


@dataclass
class StrandStatus(NetdotAPIDataclass, CSVDataclass):
    info: str = None
    name: str = None


@dataclass
class CableStrand(NetdotAPIDataclass, CSVDataclass):
    cable: Union[str,'netdot.BackboneCable'] = None
    cable_xlink: int = None
    circuit_id: Union[str,'netdot.Circuit'] = None
    circuit_id_xlink: int = None
    description: str = None
    fiber_type: Union[str,'netdot.FiberType'] = None
    fiber_type_xlink: int = None
    info: str = None
    name: str = None
    number: int = None
    status: Union[str,'netdot.StrandStatus'] = None
    status_xlink: int = None


@dataclass
class Splice(NetdotAPIDataclass, CSVDataclass):

    info: str = None
    strand1: Union[str,'netdot.CableStrand'] = None
    strand1_xlink: int = None
    strand2: Union[str,'netdot.CableStrand'] = None
    strand2_xlink: int = None


@dataclass
class CableType(NetdotAPIDataclass, CSVDataclass):

    info: str = None
    name: str = None


@dataclass
class CircuitStatus(NetdotAPIDataclass, CSVDataclass):

    info: str = None
    name: str = None


@dataclass
class CircuitType(NetdotAPIDataclass, CSVDataclass):

    info: str = None
    name: str = None


@dataclass
class FiberType(NetdotAPIDataclass, CSVDataclass):

    info: str = None
    name: str = None
