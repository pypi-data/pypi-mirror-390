import ipaddress
import logging
from dataclasses import dataclass
from typing import Union

import netdot
from netdot import parse
from netdot.csv_util import CSVDataclass
from netdot.dataclasses.base import NetdotAPIDataclass
from netdot.mac_address import MACAddress

logger = logging.getLogger(__name__)


@dataclass
class Device(NetdotAPIDataclass, CSVDataclass):
    #
    #
    # Relational fields
    #
    #
    site_xlink: int = None
    site: Union[str,'netdot.Site'] = None
    asset_id: Union[str,'netdot.Asset'] = None
    asset_id_xlink: int = None
    monitorstatus:  Union[str,'netdot.MonitorStatus']  = None
    monitorstatus_xlink: int = None
    name: Union[str,'netdot.RR'] = None
    name_xlink: int = None
    host_device: Union[str,'netdot.Device'] = None
    host_device_xlink: int = None
    bgplocalas:  Union[str,'netdot.ASN']  = None
    bgplocalas_xlink: int = None
    snmp_target: Union[ipaddress.ip_address, 'netdot.IPBlock'] = None
    snmp_target_xlink: int = None
    room: Union[str,'netdot.Room'] = None
    room_xlink: int = None
    owner: Union[str,'netdot.Entity'] = None
    owner_xlink: int = None
    used_by: Union[str,'netdot.Entity'] = None
    used_by_xlink: int = None
    #
    #
    # Basic fields
    #
    #
    id: int = None
    aliases: str = None
    bgpid: str = None
    canautoupdate: bool = None
    collect_arp: bool = None
    collect_fwt: bool = None
    collect_stp: bool = None
    community: str = None
    customer_managed: bool = None
    date_installed: parse.DateTime = None
    down_from: parse.DateTime = None
    down_until: parse.DateTime = None
    info: str = None
    ipforwarding: bool = None
    last_arp: parse.DateTime = None
    last_fwt: parse.DateTime = None
    last_updated: parse.DateTime = None
    layers: str = None
    monitor_config: bool = None
    monitor_config_group: str = None
    monitored: bool = None
    monitoring_path_cost: int = None
    oobname: str = None
    oobnumber: str = None
    os: str = None
    rack: str = None
    snmp_authkey: str = None
    snmp_authprotocol: str = None
    snmp_bulk: bool = None
    snmp_managed: bool = None
    snmp_polling: bool = None
    snmp_privkey: str = None
    snmp_privprotocol: str = None
    snmp_securitylevel: str = None
    snmp_securityname: str = None
    snmp_version: int = None
    stp_enabled: bool = None
    stp_mst_digest: str = None
    stp_mst_region: str = None
    stp_mst_rev: str = None
    stp_type: str = None
    sysdescription: str = None
    syslocation: str = None
    sysname: str = None
    auto_dns: bool = None
    extension: str = None
    snmp_conn_attempts: int = None
    snmp_down: bool = None
    oobname_2: str = None
    oobnumber_2: str = None
    power_outlet: str = None
    power_outlet_2: str = None
    monitoring_template: str = None

    def infer_base_MAC(self) -> MACAddress:
        """Infer the base_MAC address of this device from the asset_id (str, or Asset object).

        Returns:
            MACAddress: The 'base MAC' of the device.

        Raises:
            ValueError: If the asset_id does not contain a parsable MACAddress.
        """
        if isinstance(self.asset_id, NetdotAPIDataclass):
            return self.asset_id.physaddr
        return parse.MACAddress_from_asset(self.asset_id)

    def infer_product(self) -> 'netdot.Product':
        """Infer the Product of this device (based on its `asset_id` string returned from Netdot REST API).

        > NOTE: One HTTP Request is made to retrieve all Products from Netdot.
        > All subsequent calls to this method will use the cached results (see :func:`Repository.load_product_index`).

        Returns:
            netdot.Product: The Product associated to this Device, or None (if there is no Product yet associated to this device).
        """
        if self.asset_id:
            if isinstance(self.asset_id, NetdotAPIDataclass):
                if isinstance(self.asset_id.product_id, NetdotAPIDataclass):
                    return self.asset_id.product_id
                else:
                    return self.repository.infer_product(self.asset_id.product_id)
            else:
                return self.repository.infer_product(self.asset_id)

@dataclass
class DeviceAttr(NetdotAPIDataclass, CSVDataclass):
    device: Union[str,'netdot.Device'] = None
    device_xlink: int = None
    name: Union[str,'netdot.DeviceAttrName'] = None
    name_xlink: int = None
    value: str = None


@dataclass
class DeviceAttrName(NetdotAPIDataclass, CSVDataclass):
    info: str = None
    name: str = None


@dataclass
class DeviceContacts(NetdotAPIDataclass, CSVDataclass):
    _NETDOT_ASSOCIATIVE_TABLE = True
    contactlist: Union[str,'netdot.ContactList'] = None
    contactlist_xlink: int = None
    device: Union[str,'netdot.Device'] = None
    device_xlink: int = None


@dataclass
class DeviceModule(NetdotAPIDataclass, CSVDataclass):
    class__KEYWORD_ESC: str = None  # "class" is a reserved keyword in Python
    contained_in: int = None
    date_installed: parse.DateTime = None
    description: str = None
    device: Union[str,'netdot.Device'] = None
    device_xlink: int = None
    fru: bool = False
    fw_rev: str = None
    hw_rev: str = None
    last_updated: parse.DateTime = None
    model: str = None
    name: str = None
    number: int = None
    pos: int = None
    sw_rev: str = None
    type: str = None
    asset_id: Union[str,'netdot.Asset'] = None
    asset_id_xlink: int = None


@dataclass
class OUI(NetdotAPIDataclass, CSVDataclass):
    """Organizational Unique Identifier (OUI) is a 24-bit number that uniquely identifies a vendor or manufacturer."""
    oui: str = None
    vendor: str = None


@dataclass
class STPInstance(NetdotAPIDataclass, CSVDataclass):
    """Spanning Tree Protocol instance."""
    bridge_priority: int = None
    device: Union[str,'netdot.Device'] = None
    device_xlink: int = None
    number: int = None
    root_bridge: str = None
    root_port: int = None
