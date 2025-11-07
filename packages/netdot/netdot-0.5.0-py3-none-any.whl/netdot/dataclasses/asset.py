from dataclasses import dataclass
from typing import Union

import netdot
from netdot import parse
from netdot.csv_util import CSVDataclass
from netdot.dataclasses.base import NetdotAPIDataclass
from netdot.mac_address import MACAddress


@dataclass
class Asset(NetdotAPIDataclass, CSVDataclass):
    #
    #
    # Relational fields
    #
    #
    product_id: Union[str,'netdot.Product'] = None
    product_id_xlink: int = None
    physaddr: Union[MACAddress, 'netdot.PhysAddr'] = None
    physaddr_xlink: int = None
    maint_contract: Union[str,'netdot.MaintContract'] = None
    maint_contract_xlink: int = None
    #
    #
    # Basic fields
    #
    #
    custom_serial: str = None
    description: str = None
    info: str = None
    inventory_number: str = None
    maint_from: parse.DateTime = None
    maint_until: parse.DateTime = None
    date_purchased: parse.DateTime = None
    po_number: str = None
    reserved_for: str = None
    serial_number: str = None
