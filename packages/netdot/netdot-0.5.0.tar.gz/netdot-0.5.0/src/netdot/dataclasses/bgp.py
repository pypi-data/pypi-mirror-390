import logging
from dataclasses import dataclass
from typing import Union

import netdot
from netdot import parse
from netdot.csv_util import CSVDataclass
from netdot.dataclasses.base import NetdotAPIDataclass

logger = logging.getLogger(__name__)


@dataclass
class BGPPeering(NetdotAPIDataclass, CSVDataclass):

    bgppeeraddr: str = None
    bgppeerid: str = None
    device: Union[str,'netdot.Device'] = None
    device_xlink: int = None
    entity: Union[str,'netdot.Entity'] = None
    entity_xlink: int = None
    monitored: bool = False
    authkey: str = None
    info: str = None
    max_v4_prefixes: int = None
    max_v6_prefixes: int = None
    contactlist: Union[str,'netdot.ContactList'] = None
    contactlist_xlink: int = None
    last_changed: parse.DateTime = None
    peer_group: str = None
    state: str = None


@dataclass
class ASN(NetdotAPIDataclass, CSVDataclass):

    description: str = None
    info: str = None
    number: int = None
    rir: str = None
