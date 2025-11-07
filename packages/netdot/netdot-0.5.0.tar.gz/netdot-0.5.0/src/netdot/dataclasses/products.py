from dataclasses import dataclass
from typing import Union

import netdot
from netdot.csv_util import CSVDataclass
from netdot.dataclasses.base import NetdotAPIDataclass


@dataclass
class ProductType(NetdotAPIDataclass, CSVDataclass):

    info: str = None
    name: str = None


@dataclass
class Product(NetdotAPIDataclass, CSVDataclass):
    _xlink_map = {
        "type": "ProductType",
        "manufacturer": "Entity",
    }

    description: str = None
    info: str = None
    manufacturer: Union[str,'netdot.Entity'] = None
    manufacturer_xlink: int = None
    name: str = None
    sysobjectid: str = None
    type: Union[str,'netdot.ProductType'] = None
    type_xlink: int = None
    latest_os: str = None
    part_number: str = None
    config_type: str = None
