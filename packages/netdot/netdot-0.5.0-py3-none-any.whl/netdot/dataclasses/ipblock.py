import ipaddress
import logging
from dataclasses import dataclass
from typing import List, Union

import netdot
from netdot import parse
from netdot.csv_util import CSVDataclass
from netdot.dataclasses.base import NetdotAPIDataclass

logger = logging.getLogger(__name__)


@dataclass
class IPBlock(NetdotAPIDataclass, CSVDataclass):
    # TODO: consider making aliases for this class: IPContainer IPAddress, IPSubnet
    _NETDOT_TABLE_NAME = 'Ipblock'
    address: ipaddress.ip_address = None
    description: str = None
    first_seen: parse.DateTime = None
    info: str = None
    interface: Union[str, 'netdot.Interface'] = None
    interface_xlink: int = None
    last_seen: parse.DateTime = None
    owner: Union[str, 'netdot.Entity'] = None
    owner_xlink: int = None
    parent: Union[str, 'netdot.IPBlock'] = None
    parent_xlink: int = None
    prefix: int = None
    status: Union[str, 'netdot.IPBlockStatus'] = None
    status_xlink: int = None
    used_by: Union[str, 'netdot.Entity'] = None
    used_by_xlink: int = None
    version: int = None
    vlan: Union[str, 'netdot.VLAN'] = None
    vlan_xlink: int = None
    use_network_broadcast: bool = False
    monitored: bool = False
    rir: str = None
    asn: Union[str, 'netdot.ASN'] = None
    asn_xlink: int = None

    def load_children(self) -> List['IPBlock']:
        """Get the children of this IPBlock.

        Returns:
            List[IPBlock]: The children of this IPBlock.

        Raises:
            ProtocolError: Can occur if your connection with Netdot has any issues.
            HTTPError: If no results found. (error details can be found in Netdot's apache server logs)
        """
        return self.repository.get_ipblock_children(self.id)


@dataclass
class IPBlockAttrName(NetdotAPIDataclass, CSVDataclass):
    _NETDOT_TABLE_NAME = 'IpblockAttrName'
    info: str = None
    name: str = None


@dataclass
class IPBlockStatus(NetdotAPIDataclass, CSVDataclass):
    _NETDOT_TABLE_NAME = 'IpblockStatus'
    name: str = None


@dataclass
class Service(NetdotAPIDataclass, CSVDataclass):
    """Network services, such as: NTP, POP3, RADIUS, SMTP, SSH, TELNET..."""
    info: str = None
    name: str = None


@dataclass
class IPBlockAttr(NetdotAPIDataclass, CSVDataclass):
    _NETDOT_TABLE_NAME = 'IpblockAttr'
    ipblock: Union[str, 'netdot.IPBlock'] = None
    ipblock_xlink: int = None
    name: Union[str, 'netdot.IPBlockAttrName'] = None
    name_xlink: int = None
    value: str = None


@dataclass
class IPService(NetdotAPIDataclass, CSVDataclass):
    _NETDOT_TABLE_NAME = 'IpService'
    contactlist: Union[str, 'netdot.ContactList'] = None
    contactlist_xlink: int = None
    ip: Union[ipaddress.ip_address, 'netdot.IPBlock'] = None
    ip_xlink: int = None
    monitored: bool = False
    monitorstatus: Union[str, 'netdot.MonitorStatus'] = None
    monitorstatus_xlink: int = None
    service: Union[str, 'netdot.Service'] = None
    service_xlink: int = None


@dataclass
class SubnetZone(NetdotAPIDataclass, CSVDataclass):
    subnet: Union[str, 'netdot.IPBlock'] = None
    subnet_xlink: int = None
    zone: Union[str, 'netdot.Zone'] = None
    zone_xlink: int = None
