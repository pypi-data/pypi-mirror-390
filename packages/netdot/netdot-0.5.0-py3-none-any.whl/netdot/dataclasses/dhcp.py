import logging
from dataclasses import dataclass
from typing import Union

import netdot
from netdot.csv_util import CSVDataclass
from netdot.dataclasses.base import NetdotAPIDataclass

logger = logging.getLogger(__name__)


@dataclass
class DHCPScope(NetdotAPIDataclass, CSVDataclass):
    _NETDOT_TABLE_NAME = "DhcpScope"
    ipblock: Union[str,'netdot.IPBlock'] = None
    ipblock_xlink: int = None
    text: str = None
    name: str = None
    container: Union[str,'netdot.DHCPScope'] = None
    container_xlink: int = None
    physaddr: Union[str,'netdot.PhysAddr'] = None
    physaddr_xlink: int = None
    type: Union[str,'netdot.DHCPScopeType'] = None
    type_xlink: int = None
    export_file: str = None
    enable_failover: bool = False
    failover_peer: str = None
    active: bool = False
    duid: str = None
    version: int = None


@dataclass
class DHCPAttr(NetdotAPIDataclass, CSVDataclass):
    _NETDOT_TABLE_NAME = "DhcpAttr"

    name: Union[str,'netdot.DHCPAttrName'] = None
    name_xlink: int = None
    scope: Union[str,'netdot.DHCPScope'] = None
    scope_xlink: int = None
    value: str = None


@dataclass
class DHCPScopeUse(NetdotAPIDataclass, CSVDataclass):
    _NETDOT_TABLE_NAME = "DhcpScopeUse"
    scope: Union[str,'netdot.DHCPScope'] = None
    scope_xlink: int = None
    template: Union[str,'netdot.DHCPScope'] = None
    template_xlink: int = None


@dataclass
class DHCPAttrName(NetdotAPIDataclass, CSVDataclass):
    _NETDOT_TABLE_NAME = "DhcpAttrName"
    code: int = None
    format: str = None
    info: str = None
    name: str = None


@dataclass
class DHCPScopeType(NetdotAPIDataclass, CSVDataclass):
    _NETDOT_TABLE_NAME = "DhcpScopeType"
    info: str = None
    name: str = None
