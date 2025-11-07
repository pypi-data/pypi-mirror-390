import ipaddress
import logging

import netdot
from assertpy import assert_that


def test_parse_data_transfer_object_UserType():
    # Act
    user_type = netdot.UserType.from_DTO(
        {
            'id': '1',
            'name': 'test',
            'info': 'test',
        }
    )

    # Assert
    assert_that(user_type.id).is_type_of(int)
    assert_that(user_type.name).is_type_of(str)
    assert_that(user_type.info).is_type_of(str)


def test_parse_data_transfer_object_Site():
    # Act
    site = netdot.Site.from_DTO(
        {
            'id': '1',
            'name': 'test',
            'aliases': 'test',
            'availability': '0',
            'contactlist': '0',
            'info': 'test',
            'street1': 'test',
            'street2': '',
            'city': 'test',
            'state': 'test',
            'country': 'test',
            'zip': 'test',
            'pobox': 'test',
            'gsf': 'test',
            'number': 'test',
        }
    )

    # Assert
    assert_that(site.id).is_type_of(int)
    assert_that(site.availability).is_none()
    assert_that(site.contactlist).is_none()


def test_parse_data_transfer_object_IPBlock():
    # Act
    ipblock = netdot.IPBlock.from_DTO(
        {
            'id': '1',
            'parent': 'Blah Blah Blah',
            'parent_xlink': 'IPBlock/2',
            'address': '10.0.0.1',
            'description': 'test',
            'first_seen': '2020-01-01 00:00:00',
            'info': 'test',
            'interface': 'test',
            'interface_xlink': 'Interface/1',
            'last_seen': '2020-01-01 00:00:00',
            'owner': 'test',
            'owner_xlink': 'Owner/1',
            'prefix': '24',
            'status': 'test',
            'status_xlink': 'Status/1',
            'used_by': 'test',
            'used_by_xlink': 'IPBlock/1',
            'version': '4',
            'vlan': 'test',
            'vlan_xlink': 'Vlan/1',
            'use_network_broadcast': '0',
            'monitored': '0',
            'rir': 'test',
            'asn': 'test',
            'asn_xlink': 'Asn/1',
        }
    )

    # Assert
    assert_that(ipblock.id).is_type_of(int)
    assert_that(ipblock.parent_xlink).is_type_of(int)
    assert_that(ipblock.address).is_type_of(ipaddress.IPv4Address)


def test_parse_data_transfer_object_bogus_xlink(caplog):
    # ! This test will fail if environment variable NETDOT_CLI_RAISE_FIELD_PARSE_ERRORS is set to 'true'
    # Act
    netdot.IPBlock.from_DTO(
        {
            'parent_xlink': 'IPBlock/2-AND-SOME-OTHER-INVALID-TEXT',
        }
    )

    # Assert
    assert_that(caplog.text).matches("WARNING.*Unable to parse 'parent_xlink'.*IPBlock/2-AND-SOME-OTHER-INVALID-TEXT")


def test_parse_data_transfer_object_bogus_DateTime(caplog):
    # ! This test will fail if environment variable NETDOT_CLI_RAISE_FIELD_PARSE_ERRORS is set to 'true'
    # Act
    netdot.IPBlock.from_DTO(
        {
            'first_seen': 'Goopidy goop goop',
        }
    )

    # Assert
    assert_that(caplog.text).matches("WARNING.*Unable to parse 'first_seen' for 'IPBlock'.*Goopidy goop goop")


def test_parse_data_transfer_object_logs_WARNING_about_unparsed_DTO_data(caplog):
    # Act
    user_type = netdot.UserType.from_DTO(
        {
            'id': '1',
            'name': 'test',
            'info': 'test',
            'testing_fake_field': 'test',
        }
    )

    # Assert
    assert_that(user_type.id).is_type_of(int)
    assert_that(user_type.name).is_type_of(str)
    assert_that(user_type.info).is_type_of(str)
    # Assert
    assert_that(caplog.text).matches("WARNING.*unknown.*testing_fake_field")


def test_parse_data_transfer_object_logs_WARNING_about_missing_DTO_data(caplog):
    with caplog.at_level(logging.DEBUG):
        # Act
        user_type = netdot.UserType.from_DTO(
            {
                'id': '1',
            }
        )

        # Assert
        assert_that(caplog.text).matches("DEBUG.*missing.*name")
        assert_that(caplog.text).matches("DEBUG.*missing.*info")
