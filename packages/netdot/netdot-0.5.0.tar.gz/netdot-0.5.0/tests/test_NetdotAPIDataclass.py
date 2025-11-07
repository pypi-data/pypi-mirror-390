import dataclasses
import datetime
import pytest

from assertpy import assert_that

import netdot
import netdot.dataclasses as dataclasses
from netdot import Repository


def test_Device_initialization():
    # Act
    dataclasses.initialize()

    # Assert
    assert_that(dataclasses.Device._initialized).is_true()
    assert_that(vars(dataclasses.Device).keys()).contains('load_site')


def test_Closet_initialization():
    # Act
    dataclasses.initialize()

    # Assert
    assert_that(dataclasses.Closet._initialized).is_true()
    assert_that(vars(dataclasses.Closet).keys()).contains('add_horizontalcable')
    assert_that(vars(dataclasses.Closet).keys()).contains('add_backbonecable_as_end_closet')
    assert_that(vars(dataclasses.Closet).keys()).contains('add_backbonecable_as_start_closet')


def test_Site_initialization():
    # Act
    dataclasses.initialize()

    # Assert
    assert_that(dataclasses.Site._initialized).is_true()
    assert_that(vars(dataclasses.Site).keys()).contains('load_devices')
    assert_that(vars(dataclasses.Site).keys()).contains('add_device')
    assert_that(vars(dataclasses.Site).keys()).contains('add_floor')


def test_Product_initialization():
    # Act
    dataclasses.initialize()

    # Assert
    assert_that(dataclasses.Site._initialized).is_true()
    assert_that(vars(dataclasses.Site).keys()).contains('load_devices')
    assert_that(vars(dataclasses.Site).keys()).contains('load_devices')


def test_asset_setter():
    # Arrange
    device = dataclasses.Device()
    my_asset = dataclasses.Asset(info='Testing', id=123)

    # Asset
    device.asset_id = my_asset

    # Assert
    assert_that(device.asset_id_xlink).is_equal_to(my_asset.id)


def test_post_init_handles_xlink_population():
    # Arrange
    site = netdot.Site(name='Test Site', id=123)

    # Act
    floor = netdot.Floor(level='Test Floor', site=site)

    # Assert
    assert_that(floor.site_xlink).is_equal_to(site.id)
    assert_that(floor.site).is_equal_to(site)

def test_add_methods_exist():
    # Arrange
    netdot.Device._prepare_class()
    netdot.ContactList._prepare_class()
    netdot.DeviceContacts._prepare_class()

    # Assert
    attribute_names = vars(netdot.Device).keys()
    assert_that(attribute_names).contains('add_contactlist')


def test_load_methods_exist():
    # Arrange
    netdot.Site._prepare_class()
    netdot.SiteSubnet._prepare_class()

    # Assert
    attribute_names = vars(netdot.Site).keys()
    assert_that(attribute_names).contains('load_availability')
    assert_that(attribute_names).contains('load_contactlist')
    assert_that(attribute_names).contains('load_devices')
    assert_that(attribute_names).contains('load_farend_sitelinks')
    assert_that(attribute_names).contains('load_nearend_sitelinks')
    assert_that(attribute_names).contains('load_subnets')
    assert_that(attribute_names).contains('load_entities')


@pytest.mark.vcr
def test_create(repository):
    # Arrange
    repository.disable_propose_changes()
    site = netdot.Site(
        name='Test Site',
        aliases='test-site',
        info='A site created by automated testing (netdot-sites-manager).',
    ).with_repository(repository)

    # Act
    site.create()

    # Assert
    assert_that(site.id).is_not_none()

    # Cleanup
    site.delete(confirm=False)


@pytest.mark.vcr
def test_cannot_create_with_ID(repository):
    site = repository.get_site(137)

    # Act
    assert_that(
        site.create
    ).raises(
        ValueError
    ).when_called_with()


@pytest.mark.vcr
def test_update(repository):
    # Arrange
    repository.disable_propose_changes()
    site = repository.create_new(netdot.Site(
        name='Test Site',
        aliases='test-site',
    ))

    # Act
    site.name = 'UPDATED'
    site.aliases = 'UPDATED'
    site.update()

    # Assert
    # TODO These assertions are pretty lame -- better to do a get_site(site.id) for sure.
    assert_that(site.name).is_equal_to('UPDATED')
    assert_that(site.aliases).is_equal_to('UPDATED')

    # Cleanup
    site.delete(confirm=False)


@pytest.mark.vcr
def test_my_xlink_load_method(repository):
    # Arrange
    contact = repository.get_contact(1716)

    # Act
    email_availability = contact.load_notify_email()

    # Assert
    assert_that(email_availability).is_not_none()


@pytest.mark.vcr
def test_my_xlink_load_method_when_none_related(repository):
    # Arrange
    contact = repository.get_contact(1716)

    # Act
    pager_availability = contact.load_notify_pager()

    # Assert
    assert_that(pager_availability).is_none()


@pytest.mark.vcr
def test_require_ID_to_update(repository):
    site = netdot.Site(id=None, name='Test Site').with_repository(repository)

    # Act
    assert_that(
        site.update
    ).raises(
        ValueError
    ).when_called_with()


@pytest.mark.vcr
def test_create_RR_with_datetime(repository: Repository):
    # Arrange
    repository.disable_propose_changes()
    zone = repository.get_zone(1)
    rr = repository.create_new(
        netdot.RR(
            expiration=datetime.datetime(2020, 1, 1, 0, 0, 0),
            zone=zone,
            info='test-info',
            name='test-name',
        )
    )

    assert_that(rr.id).is_not_none()
    assert_that(rr.expiration).is_equal_to(datetime.datetime(2020, 1, 1, 0, 0, 0))

    # Cleanup
    rr.delete(confirm=False)


@pytest.mark.vcr
def test_sites_equal(repository):
    # Arrange
    repository.disable_propose_changes()
    site1 = repository.get_site(137)
    site2 = repository.get_site(137)

    # Act & Assert
    assert_that(site1).is_equal_to(site2)


@pytest.mark.vcr
def test_sites_unequal_after_modification(repository):
    # Arrange
    site1 = repository.get_site(137)
    site2 = repository.get_site(137)

    # Act
    site2.name = 'UPDATED'

    # Assert
    assert_that(site1).is_not_equal_to(site2)


@pytest.mark.vcr
def test_sites_unequal(repository):
    # Arrange
    site1 = repository.get_site(137)
    site2 = repository.get_site(136)

    # Act & Assert
    assert_that(site1).is_not_equal_to(site2)


def test_replace():
    # Arrange
    dataclasses.initialize()
    site = dataclasses.Site(
        name='Test netdot-sites-manager package', 
        info="""Created to test the netdot-sites-manager Python package. 
            See more in the project's user guide: 
            https://git.uoregon.edu/projects/ISN/repos/netdot-sites-manager/browse/docs/user-guide.md"""
    )

    # Act
    updated_site = site.replace(name=f'UPDATED: {site.name}')

    # Assert
    assert_that(updated_site.name).starts_with('UPDATED: ')
