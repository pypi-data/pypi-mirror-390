from dataclasses import dataclass
from typing import Union

import netdot
from netdot.csv_util import CSVDataclass
from netdot.dataclasses.base import NetdotAPIDataclass


@dataclass
class Entity(NetdotAPIDataclass, CSVDataclass):
    acctnumber: str = None
    aliases: str = None
    asname: str = None
    asnumber: int = None
    availability: Union[str,'netdot.Availability'] = None
    availability_xlink: int = None
    contactlist: Union[str,'netdot.ContactList'] = None
    contactlist_xlink: int = None
    info: str = None
    maint_contract: str = None
    name: str = None
    oid: str = None
    short_name: str = None
    config_type: str = None


@dataclass
class EntityType(NetdotAPIDataclass, CSVDataclass):
    info: str = None
    name: str = None


@dataclass
class EntityRole(NetdotAPIDataclass, CSVDataclass):
    _NETDOT_ASSOCIATIVE_TABLE = True
    entity: Union[str,'netdot.Entity'] = None
    entity_xlink: int = None
    type: Union[str,'netdot.EntityType'] = None
    type_xlink: int = None


@dataclass
class EntitySite(NetdotAPIDataclass, CSVDataclass):
    _NETDOT_ASSOCIATIVE_TABLE = True
    entity: Union[str,'netdot.Entity'] = None
    entity_xlink: int = None
    site: Union[str,'netdot.Site'] = None
    site_xlink: int = None
