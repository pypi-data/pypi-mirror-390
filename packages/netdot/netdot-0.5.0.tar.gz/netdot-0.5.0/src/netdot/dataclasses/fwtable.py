import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Union

import netdot
from netdot import parse
from netdot.csv_util import CSVDataclass
from netdot.dataclasses.base import NetdotAPIDataclass
from netdot.mac_address import MACAddress

logger = logging.getLogger(__name__)


@dataclass
class FWTable(NetdotAPIDataclass, CSVDataclass):
    """Forwarding Table for a device."""

    device: Union[str,'netdot.Device'] = None
    device_xlink: int = None
    id: int = None
    tstamp: parse.DateTime = None


@dataclass
class FWTableEntry(NetdotAPIDataclass, CSVDataclass):
    """Forwarding Table entries."""

    fwtable: Union[str,'netdot.FWTable'] = None
    fwtable_xlink: int = None
    id: int = None
    interface: Union[str,'netdot.Interface'] = None
    interface_xlink: int = None
    physaddr: Union[MACAddress,'netdot.PhysAddr']  = None
    physaddr_xlink: int = None

    def infer_timestamp(self) -> datetime:
        """Infer the timestamp of this FWTableEntry (based on the 'fwtable' string returned to us by Netdot API).

        Returns:
            datetime: The inferred timestamp.

        Raises:
            ValueError: If unable to infer the timestamp.
        """
        try:
            tokens = parse.split_combined_entities_str(self.fwtable)
            if len(tokens) == 2:
                return parse.DateTime(tokens[0])
        except Exception:
            raise ValueError(f'Unsure how to parse timestamp from fwtable string: {self.fwtable}')
 