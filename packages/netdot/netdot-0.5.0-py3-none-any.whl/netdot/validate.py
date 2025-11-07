"""Functions to help validate the correctness of arbitrary values.

Note: Raise an Error validation fails.
"""

import logging

from netdot import exceptions

logger = logging.getLogger(__name__)


def VLAN_id(vlan_id: int):
    # ensure: 1 <= vid <= 4094
    if vlan_id < 1 or vlan_id > 4094:
        raise ValueError(f'VLAN ID outside of valid range: {vlan_id}')


def RESTful_XML(content):
    expected_root_token = '<opt'
    xml_message = str(content)
    if expected_root_token not in xml_message:
        raise exceptions.NetdotRESTError(
            f'Expected {expected_root_token} to be root of XML response.',
            response=xml_message,
        )
