from dataclasses import dataclass
from typing import Union

import netdot
from netdot import validate
from netdot.csv_util import CSVDataclass
from netdot.dataclasses.base import NetdotAPIDataclass


@dataclass
class VLAN(NetdotAPIDataclass, CSVDataclass):
    _NETDOT_TABLE_NAME = "Vlan"
    description: str = None
    info: str = None
    name: str = None
    vid: int = None
    vlangroup: Union[str,'netdot.VLANGroup'] = None
    vlangroup_xlink: int = None

    @property
    def has_valid_vid(self):
        if self.vid is None:
            return False
        try:
            validate.VLAN_id(self.vid)
            return True
        except ValueError:
            return False


@dataclass
class VLANGroup(NetdotAPIDataclass, CSVDataclass):
    _NETDOT_TABLE_NAME = "VlanGroup"

    description: str = None
    end_vid: int = None
    info: str = None
    name: str = None
    start_vid: int = None
