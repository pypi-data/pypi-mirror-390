import os

import pytest
from assertpy import assert_that

import netdot
from netdot import UnitOfWork, actions, exceptions


def test_with_data_type():
    # Arrange
    unit_of_work = UnitOfWork()
    unit_of_work.create(netdot.RR(name='TEST'))
    unit_of_work.create(netdot.ProductType(name='TEST1'))
    unit_of_work.create(netdot.ProductType(name='TEST2'))
    unit_of_work.create(netdot.Site(name='Site1'))
    unit_of_work.create(netdot.Site(name='Site2'))
    unit_of_work.delete(netdot.Site(name='Site3', id=123))
    unit_of_work.update(netdot.Site(name='REPLACE_ME'), netdot.Site(name='Site4'))

    # Act
    unit_of_work = unit_of_work.with_data_type(netdot.Site)

    # Assert
    assert_that(unit_of_work).is_length(4)
    for action in unit_of_work.as_list():
        site = action.new_data if action.new_data else action.old_data
        assert_that(site).is_instance_of(netdot.Site)


def test_dry_run_indents():
    proposed_changes = UnitOfWork()
    for i in range(10000):
        proposed_changes.create(netdot.ProductType())

    # Act
    dry_run = proposed_changes.dry_run()

    # Assert
    assert_that(dry_run).starts_with(
        "    1. Will CREATE ProductType: ProductType(id=None, info=None, name=None)"
    )
    assert_that(dry_run).ends_with(
        "10000. Will CREATE ProductType: ProductType(id=None, info=None, name=None)"
    )


def test_dry_run():
    # Arrange
    proposed_changes = UnitOfWork()
    proposed_changes.create(netdot.ProductType(name="EXAMPLE"))
    proposed_changes.delete(netdot.Site(name="ToDelete", id=123))
    proposed_changes.update(
        netdot.Site(name="Original", id=123), netdot.Site(name="Updated", id=123)
    )

    # Act
    dry_run = proposed_changes.dry_run(terse=False)

    # Assert
    assert_that(dry_run).contains(
        "1. Will CREATE ProductType: ProductType(id=None, info=None, name='EXAMPLE')"
    )
    assert_that(dry_run).matches(
        r"2. Will DELETE Site: Site\(id=123, name='ToDelete', .*\)"
    )
    assert_that(dry_run).matches(
        r"3. Will UPDATE Site: Site\(id=123, name='Updated', .*\) \(replacing: Site\(id=123, name='Original', .*\)\)"
    )


def test_save_as_pickle_and_load():
    proposed_changes = UnitOfWork()

    proposed_changes.create(netdot.ProductType(name="EXAMPLE"))
    proposed_changes.delete(netdot.Site(name="ToDelete", id=123))
    proposed_changes.update(
        netdot.Site(name="Original", id=123), netdot.Site(name="Updated", id=123)
    )

    # Act 
    proposed_changes.save_as_pickle("test.pickle")
    loaded = UnitOfWork.load("test.pickle")
    dry_run = loaded.dry_run(terse=False)

    # Assert
    assert_that(dry_run).contains(
        "1. Will CREATE ProductType: ProductType(id=None, info=None, name='EXAMPLE')"
    )
    assert_that(dry_run).matches(
        r"2. Will DELETE Site: Site\(id=123, name='ToDelete', .*\)"
    )
    assert_that(dry_run).matches(
        r"3. Will UPDATE Site: Site\(id=123, name='Updated', .*\) \(replacing: Site\(id=123, name='Original', .*\)\)"
    )

    # Cleanup
    os.remove("test.pickle")


def test_dry_run_tabulated():
    proposed_changes = UnitOfWork()

    proposed_changes.create(netdot.ProductType(name="EXAMPLE1"))
    proposed_changes.create(netdot.ProductType(name="EXAMPLE2", info='TEST'))
    proposed_changes.delete(netdot.Site(name="ToDelete", id=123))
    proposed_changes.update(
        netdot.Site(name="Original", id=123), netdot.Site(name="Updated", id=123)
    )

    # Act
    dry_run = proposed_changes.changes_as_tables(terse=False)

    # Assert
    assert_that(dry_run).contains(
        """## ProductType Changes

action    id    info    name
--------  ----  ------  --------
CREATE    None  None    EXAMPLE1
CREATE    None  TEST    EXAMPLE2
"""
    )
    assert_that(dry_run).contains("## Site Changes")
    assert_that(dry_run).contains("DELETE")
    assert_that(dry_run).contains("[-Original-]+Updated+")


def test_dry_run_tabulated_terse():
    proposed_changes = UnitOfWork()

    proposed_changes.create(netdot.ProductType(name="EXAMPLE1"))
    proposed_changes.create(netdot.ProductType(name="EXAMPLE2", info='TEST'))
    proposed_changes.delete(netdot.Site(name="ToDelete", id=123))
    proposed_changes.create(netdot.Site(name="Test Site"))
    proposed_changes.update(
        netdot.Site(name="Before", id=123), netdot.Site(name="After", id=123)
    )

    # Act
    dry_run = proposed_changes.changes_as_tables(terse=True)

    # Assert
    assert_that(dry_run).contains(
        """## Site Changes

action    id    name              aliases    availability    contactlist
--------  ----  ----------------  ---------  --------------  -------------
DELETE    123   ToDelete          None       None            None
CREATE    None  Test Site         None       None            None
UPDATE    123   [-Before-]+After  None       None            None
                +"""
    )
    # ?         ^-- Wondering "what's this '+' doing here?"
    # ? There is a newline inserted before the "+" due to `defaults.TABULATE_TERSE_COL_WIDTH` being 16.

    assert_that(dry_run).contains("DELETE")


def test_with_action_type_UPDATE_DELETE():
    # Arrange
    unit_of_work = UnitOfWork()
    unit_of_work.delete(netdot.Site())
    unit_of_work.update(netdot.Site(), netdot.Site())
    unit_of_work.create(netdot.Site())
    unit_of_work.create(netdot.Site())
    unit_of_work.create(netdot.Site())

    # Act
    unit_of_work = unit_of_work.with_action_types(
        [actions.ActionTypes.UPDATE, actions.ActionTypes.DELETE]
    )

    # Assert
    assert_that(unit_of_work).is_length(2)
    for action in unit_of_work.as_list():
        assert_that(action.action_type).is_not_same_as(actions.ActionTypes.CREATE)


def test_without_action_type_DELETE():
    # Arrange
    unit_of_work = UnitOfWork()
    unit_of_work.update(netdot.Site(), netdot.Site())
    unit_of_work.create(netdot.Site())
    unit_of_work.delete(netdot.Site())
    unit_of_work.delete(netdot.Site())
    unit_of_work.delete(netdot.Site())

    # Act
    unit_of_work = unit_of_work.without_action_types([actions.ActionTypes.DELETE])

    # Assert
    assert_that(unit_of_work).is_length(2)
    for action in unit_of_work.as_list():
        assert_that(action.action_type).is_not_same_as(actions.ActionTypes.DELETE)


@pytest.mark.vcr
def test_failed_change(repository):
    # Arrange
    repository.disable_propose_changes()
    unit_of_work = UnitOfWork()
    unit_of_work.create(netdot.Site(name='Test Site', aliases='A'))
    unit_of_work.create(netdot.Site(name='Test Site', aliases='B'))
    assert_that(unit_of_work.failed_action()).is_none()
    assert_that(unit_of_work.save_changes).raises(
        exceptions.HTTPError
    ).when_called_with(repository)

    # Act
    failed_action = unit_of_work.failed_action()
    failed_action_msg = unit_of_work.failed_action_msg()

    # Assert
    assert_that(failed_action).is_not_none()
    assert_that(failed_action_msg).contains("aliases='B'")
    assert_that(failed_action_msg).does_not_contain("aliases='A'")
