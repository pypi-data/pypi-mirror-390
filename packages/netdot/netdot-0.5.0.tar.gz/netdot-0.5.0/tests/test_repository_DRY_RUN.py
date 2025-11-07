import logging
import os

import netdot
import pytest
from assertpy import assert_that
from netdot import Repository, exceptions


@pytest.mark.vcr
def test_show_changes(repository: Repository, capfd):
    # Arrange
    repository.enable_propose_changes(print_changes=False)
    repository.create_new(netdot.Audit())
    repository.create_new(netdot.Availability())
    repository.create_new(netdot.HorizontalCable())
    site = repository.get_site(137)
    site.name = 'AAAA'
    repository.create_new(netdot.Device())
    repository.delete(netdot.BGPPeering())
    repository.create_new(netdot.BGPPeering())
    site.aliases = 'BBBB'  # Later, make some more updates to the site

    # Act
    repository.show_changes(terse=True)

    # Assert
    console_output = capfd.readouterr().out
    assert_that(console_output).contains(
        ' 1. Will CREATE Audit: Audit(id=None, fields=None, label=None, object_id=None...'
    )
    assert_that(console_output).contains('2. Will CREATE Availability')
    assert_that(console_output).contains('3. Will CREATE HorizontalCable')
    assert_that(console_output).contains('4. Will CREATE Device')
    assert_that(console_output).contains('5. Will DELETE BGPPeering')
    assert_that(console_output).contains('6. Will CREATE BGPPeering')
    assert_that(console_output).matches('7. Will UPDATE Site.*AAAA.*BBBB.*')


@pytest.mark.vcr
def test_get_rr_by_address_does_NOT_propose_changes(repository: Repository, capfd):
    # Arrange
    repository.enable_propose_changes(print_changes=False)
    repository.get_rr_by_address('128.223.250.151')

    # Act
    repository.show_changes()

    # Assert
    console_output = capfd.readouterr().out
    assert_that(console_output.strip()).is_equal_to('None, yet...')


@pytest.mark.vcr
def test_show_changes_as_tables(repository: Repository, capfd):
    # Arrange
    repository.enable_propose_changes(print_changes=False)
    repository.create_new(netdot.Audit())
    repository.create_new(netdot.Device(collect_arp=False))
    repository.delete(netdot.BGPPeering())
    site = repository.get_site(137)
    site.name = 'UPDATED'
    site.aliases = 'AAAA'

    # Act
    repository.show_changes_as_tables(terse=True)

    # Assert
    console_output = capfd.readouterr().out
    assert_that(console_output).contains(
        """## BGPPeering Changes

action    id    bgppeeraddr    bgppeerid    device    entity
--------  ----  -------------  -----------  --------  --------
DELETE    None  None           None         None      None
"""
    )
    assert_that(console_output).contains(
        """## Device Changes

action    id    site    asset_id    monitorstatus    name
--------  ----  ------  ----------  ---------------  ------
CREATE    None  None    None        None             None
"""
    )
    assert_that(console_output).contains(
        """## Site Changes

action      id  name              aliases    availability    contactlist
--------  ----  ----------------  ---------  --------------  ----------------
UPDATE     137  [-Computing       +AAAA+     None            Computing Center
                Center                                       Contacts
                (039)-]+UPDATED+"""
    )


@pytest.mark.vcr
def test_show_changes_as_tables_widescreen(repository: Repository, capfd):
    # Arrange
    repository.enable_propose_changes(print_changes=False)
    site = repository.get_site(137)
    site.name = 'AAAA'
    site.aliases = 'BBBB'

    # Act
    repository.show_changes_as_tables(terse=False)

    # Assert
    console_output = capfd.readouterr().out
    assert_that(console_output).contains("""## Site Changes

action      id  name                              aliases    availability    contactlist                  gsf    number  street1          street2    state    city    country      zip  pobox    info
--------  ----  --------------------------------  ---------  --------------  -------------------------  -----  --------  ---------------  ---------  -------  ------  ---------  -----  -------  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
UPDATE     137  [-Computing Center (039)-]+AAAA+  +BBBB+     None            Computing Center Contacts      0       039  1225 KINCAID ST             OR       EUGENE  US         97401           === BEGIN AUTOMATION MSG ===  > WARNING: Any details entered below "=== BEGIN AUTOMATION MSG ===" will be overwritten by automation.  ⚠ NOTICE: Managed by "NetDot Sync with GIS" NTS Jenkins Pipeline.                 https://is-nts-jenkins.uoregon.edu/job/Netdot%20Sync%20with%20GIS/             Fields (Column Names): number, name, street1, street2, city, state, zip, country             Last Created/Updated at 2022-07-08T14:10:34 PDT.
""")


@pytest.mark.vcr
def test_show_changes_as_tables_select_columns(repository: Repository, capfd):
    # Arrange
    repository.enable_propose_changes(print_changes=False)
    site = repository.create_new(netdot.Site(name='Test Site'))
    floor = site.add_floor(netdot.Floor(level='Test Floor'))
    room1 = floor.add_room(netdot.Room(name='Test Room 1'))  # noqa: F841
    room2 = floor.add_room(netdot.Room(name='Test Room 2'))
    room3 = floor.add_room(netdot.Room(name='Test Room 3'))
    closet = room3.add_closet(netdot.Closet(name='Test Closet 1'))
    closet.room = room2

    # Act
    repository.show_changes_as_tables(select_cols=['name', 'level', 'room'])

    # Assert
    console_output = capfd.readouterr().out

    assert_that(console_output).contains(
        """## Closet Changes

action    name           room
--------  -------------  ---------------------------------
CREATE    Test Closet 1  Room(id=None, name='Test Room 2')
"""
    )
    assert_that(console_output).contains(
        """## Site Changes

action    name
--------  ---------
CREATE    Test Site
"""
    )
    assert_that(console_output).contains(
        """## Floor Changes

action    level
--------  ----------
CREATE    Test Floor"""
    )
    assert_that(console_output).contains(
        """## Room Changes

action    name
--------  -----------
CREATE    Test Room 1
CREATE    Test Room 2
CREATE    Test Room 3"""
    )


@pytest.mark.vcr
def test_save_changes(repository: Repository, caplog):
    # Arrange
    repository.enable_propose_changes(print_changes=False)
    site = repository.create_new(netdot.Site(name='Test Site'))
    caplog.set_level(logging.INFO)

    # Act
    repository.save_changes()

    # Assert
    assert_that(caplog.text).contains('Will CREATE Site')

    # Cleanup
    site.delete(confirm=False)


@pytest.mark.vcr
def test_status_report_when_failed_action(repository: Repository):
    # Arrange
    repository.enable_propose_changes(print_changes=False)
    site = repository.create_new(netdot.Site(name='Test Site'))
    # NOTE: Adding a 2nd site with same name will raise 400 error:
    duplicate_site = repository.create_new(netdot.Site(name='Test Site'))
    floor = site.add_floor(netdot.Floor(level='Test Floor'))
    room = floor.add_room(netdot.Room(name='Test Room'))
    netdot.config.ERROR_PICKLE_FILENAME = 'netdot.pickle'
    netdot.config.SAVE_AS_FILE_ON_ERROR = True
    # Try to save bogus changes will raise an exception:
    assert_that(repository.save_changes).raises(
        exceptions.NetdotError
    ).when_called_with()

    # Act
    report = repository.proposed_changes.status_report()

    # Assert
    assert_that(netdot.config.ERROR_PICKLE_FILENAME).exists()
    assert_that(report).contains('1. Finished CREATE Site')
    assert_that(report).contains('1. Will CREATE Floor')
    assert_that(report).contains('2. Will CREATE Room')
    assert_that(report).matches(
        r"""Failed Action\(s\):

1. Will CREATE Site: .*
---> Failed with exception: 400 .*"""
    )

    # Cleanup
    site.delete(confirm=False)
    os.remove(netdot.config.ERROR_PICKLE_FILENAME)


@pytest.mark.vcr
def test_incremental_creation_of_site_with_rooms(repository: Repository, caplog):
    # Arrange
    repository.enable_propose_changes(print_changes=False)
    site = repository.create_new(netdot.Site(name='Test Site 1'))
    floor = site.add_floor(netdot.Floor(level='Test Floor 1'))
    room1 = floor.add_room(netdot.Room(name='Test Room 1'))
    room2 = floor.add_room(netdot.Room(name='Test Room 2'))
    room3 = floor.add_room(netdot.Room(name='Test Room 3'))
    closet = room3.add_closet(netdot.Closet(name='Test Closet 1'))
    caplog.set_level(logging.INFO)

    # Act
    repository.save_changes()

    # Assert
    assert_that(site.id).is_not_none()
    assert_that(floor.id).is_not_none()
    assert_that(room1.id).is_not_none()
    assert_that(room2.id).is_not_none()
    assert_that(room3.id).is_not_none()
    assert_that(closet.id).is_not_none()

    # Cleanup
    site.delete(confirm=False)
