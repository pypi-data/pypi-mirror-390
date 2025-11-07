import os

import pytest
from assertpy import assert_that
import netdot

from netdot.client import Client
from netdot.exceptions import HTTPError


@pytest.fixture
def client(netdot_url, username, password) -> Client:
    return Client(netdot_url, username, password)


@pytest.mark.vcr()
def test_get_object_by_id(client: Client):
    # Act
    device = client.get_object_by_id('Device', 12973)

    # Assert
    assert_that(device).is_type_of(dict)
    assert_that(device).contains_key('name')
    assert_that(device).contains_key('site')
    assert_that(device).contains_key('bgplocalas')
    assert_that(device).contains_key('last_arp')


@pytest.mark.vcr()
def test_get_all(client):
    # Act
    sites = client.get_all('Site')

    # Assert
    assert_that(sites).is_type_of(list).is_not_empty()
    site = sites[0]
    assert_that(site).is_type_of(dict)
    assert_that(site).contains_key('street1')
    assert_that(site).contains_key('street2')
    assert_that(site).contains_key('state')
    assert_that(site).contains_key('city')
    assert_that(site).contains_key('country')


@pytest.mark.vcr()
def test_create_object_site(client: Client):
    # Act
    site = client.create_object(
        "site",
        {
            'name': 'Test site 123',
            'info': 'A site created by automated testing (netdot-sites-manager).',
        },
    )

    # Assert
    assert_that(site['name']).is_equal_to('Test site 123')


@pytest.mark.vcr()
def test_get_object_by_id_0_raises_error(client: Client):
    assert_that(
        client.get_object_by_id
    ).raises(
        HTTPError
    ).when_called_with(
        'Site', 1234
    )


@pytest.mark.vcr()
def test_get_object_by_id_FooBar_raises_error(client: Client):
    assert_that(
        client.get_object_by_id
    ).raises(
        HTTPError
    ).when_called_with(
        'FooBar', 1234
    )


@pytest.mark.vcr()
def test_delete_object_site(client: Client):
    # Act
    client.delete_object_by_id("site", 754)

    # Assert
    assert_that(client.get_object_by_id).raises(HTTPError).when_called_with('site', 754)


@pytest.mark.vcr()
def test_verify_ssl_enabled_by_default(netdot_url, username, password):
    # ! This test will fail if environment variable NETDOT_CLI_SKIP_SSL is set to 'true'
    # Act
    client = Client(netdot_url, username, password)

    # Assert
    assert_that(client.http.verify).is_true()


@pytest.mark.vcr()
def test_logout(netdot_url, username, password):
    # Arrange
    client = Client(netdot_url, username, password)
    assert_that(client.http.cookies).is_not_empty()

    # Act
    client.logout()

    # Assert
    assert_that(client.http.cookies).is_empty()


@pytest.mark.vcr()
def test_login_fails_with_nice_message(netdot_url, username, password):
    # Arrange
    client = Client(netdot_url, username, password)
    assert_that(client.http.cookies).is_not_empty()

    # Act
    client.logout()

    # Assert
    assert_that(client.http.cookies).is_empty()


@pytest.mark.vcr()
@pytest.mark.skip("We're struggling to remember how to solicit a 'Carp::croak' from netdot REST API. It was happening last week, but it doesn't show up in NSDB Logs... Prime suspect is the: 'search_like' Netdot function -- iirc, the error messages looked like they were produced from there.")
def test_warn_if_CarpCroak_returned_in_HTTP_response(client: Client, capsys):
    assert_that(
        client.post
    ).raises(
        netdot.exceptions.HTTPError
    ).when_called_with('/floor', data={
        'id': 1234,
        'name': 'test',  # Should actually be 'level'! (not 'name')
        'site': 137,
    })

    assert_that(capsys.readouterr().out).contains('WARN')
