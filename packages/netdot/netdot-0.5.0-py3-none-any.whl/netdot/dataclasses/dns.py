from dataclasses import dataclass
from typing import Union

import netdot
from netdot import parse
from netdot.csv_util import CSVDataclass
from netdot.dataclasses.base import NetdotAPIDataclass


@dataclass
class Zone(NetdotAPIDataclass, CSVDataclass):

    active: bool = False
    contactlist: Union[str,'netdot.ContactList'] = None
    contactlist_xlink: int = None
    expire: int = None
    info: str = None
    minimum: int = None
    name: str = None
    refresh: int = None
    retry: int = None
    rname: str = None
    serial: int = None
    default_ttl: int = None
    export_file: str = None
    mname: str = None
    include: str = None


@dataclass
class ZoneAlias(NetdotAPIDataclass, CSVDataclass):

    info: str = None
    name: str = None
    zone: Union[str,'netdot.Zone'] = None
    zone_xlink: int = None


@dataclass
class RR(NetdotAPIDataclass, CSVDataclass):

    active: bool = False
    auto_update: bool = False
    expiration: parse.DateTime = None
    info: str = None
    name: str = None
    zone: Union[str,'netdot.Zone'] = None
    zone_xlink: int = None
    created: parse.DateTime = None
    modified: parse.DateTime = None

    def infer_FQDN(self) -> str:
        """Infer the Fully Qualified Domain Name (FQDN) for this Resource Record (RR).

        Raises:
            ValueError: If either `name` or `zone` are not set for this RR.

        Returns:
            str: The FQDN for this RR.
        """
        if self.name and self.zone:
            return f"{self.name}.{self.zone}"
        else:
            raise ValueError("RR.name and RR.zone must be set to get FQDN")


@dataclass
class RRADDR(NetdotAPIDataclass, CSVDataclass):

    ipblock: Union[str,'netdot.IPBlock'] = None
    ipblock_xlink: int = None
    rr: Union[str,'netdot.RR'] = None
    rr_xlink: int = None
    ttl: str = None


@dataclass
class RRCNAME(NetdotAPIDataclass, CSVDataclass):

    cname: str = None
    rr: Union[str,'netdot.RR'] = None
    rr_xlink: int = None
    ttl: str = None


@dataclass
class RRDS(NetdotAPIDataclass, CSVDataclass):

    algorithm: int = None
    digest: str = None
    digest_type: int = None
    key_tag: int = None
    rr: Union[str,'netdot.RR'] = None
    rr_xlink: int = None
    ttl: str = None


@dataclass
class RRHINFO(NetdotAPIDataclass, CSVDataclass):

    cpu: str = None
    os: str = None
    rr: Union[str,'netdot.RR'] = None
    rr_xlink: int = None
    ttl: str = None


@dataclass
class RRLOC(NetdotAPIDataclass, CSVDataclass):
    _DISPLAY_ATTRIBUTES = ['latitude', 'longitude']

    altitude: int = None
    horiz_pre: str = None
    latitude: str = None
    longitude: str = None
    rr: Union[str,'netdot.RR'] = None
    rr_xlink: int = None
    size: str = None
    ttl: str = None
    vert_pre: str = None


@dataclass
class RRMX(NetdotAPIDataclass, CSVDataclass):

    exchange: str = None
    preference: int = None
    rr: Union[str,'netdot.RR'] = None
    rr_xlink: int = None
    ttl: str = None


@dataclass
class RRNAPTR(NetdotAPIDataclass, CSVDataclass):

    flags: str = None
    order_field: int = None
    preference: int = None
    regexpr: str = None
    replacement: str = None
    rr: Union[str,'netdot.RR'] = None
    rr_xlink: int = None
    services: str = None
    ttl: str = None


@dataclass
class RRNS(NetdotAPIDataclass, CSVDataclass):

    nsdname: str = None
    rr: Union[str,'netdot.RR'] = None
    rr_xlink: int = None
    ttl: str = None


@dataclass
class RRPTR(NetdotAPIDataclass, CSVDataclass):

    ipblock: Union[str,'netdot.IPBlock'] = None
    ipblock_xlink: int = None
    ptrdname: str = None
    rr: Union[str,'netdot.RR'] = None
    rr_xlink: int = None
    ttl: str = None


@dataclass
class RRSRV(NetdotAPIDataclass, CSVDataclass):

    port: int = None
    priority: int = None
    rr: Union[str,'netdot.RR'] = None
    rr_xlink: int = None
    target: str = None
    ttl: str = None
    weight: int = None


@dataclass
class RRTXT(NetdotAPIDataclass, CSVDataclass):

    rr: Union[str,'netdot.RR'] = None
    rr_xlink: int = None
    ttl: str = None
    txtdata: str = None
