'''Create, Read, Update, Delete tests for some key Netdot objects.
'''
import netdot
import pytest
from assertpy import assert_that
from netdot import exceptions
from netdot.repository import Repository


@pytest.mark.vcr
def test_create_update_delete_ProductType(repository: Repository):
    #
    #
    # Create
    #
    #
    # Arrange
    repository.disable_propose_changes()
    example_product_type = netdot.ProductType(name="EXAMPLE")

    # Act
    created_product_type: netdot.ProductType = repository.create_new(
        example_product_type
    )

    # Assert
    assert_that(created_product_type).is_not_none()
    assert_that(created_product_type.id).is_not_zero()

    #
    #
    # Read
    #
    #
    # Arrange
    product_type_id: int = created_product_type.id

    # Act
    retrieved_product_type: netdot.ProductType = repository.get_producttype(
        product_type_id
    )

    # Assert
    assert_that(retrieved_product_type.name).is_equal_to(example_product_type.name)

    #
    #
    # Update
    #
    #
    # Arrange
    created_product_type.name = "Updated"

    # Act
    updated_product_type = repository.update(created_product_type)

    # Assert
    assert_that(updated_product_type).is_not_none()
    assert_that(updated_product_type.name).is_equal_to("Updated")
    retrieved_product_type = repository.get_producttype(product_type_id)
    assert_that(retrieved_product_type.name).is_equal_to("Updated")

    #
    #
    # Delete
    #
    #
    # Act
    repository.delete(updated_product_type, confirm=False)

    # Assert
    assert_that(repository.get_producttype).raises(
        exceptions.HTTPError
    ).when_called_with(product_type_id).described_as('Deleted obj should not be found')

    #
    #
    # Delete #2 raises NO error (if ignore_404=True, Default)
    #
    #
    # Act
    repository.delete(updated_product_type, confirm=False)

    #
    #
    # Delete #2 raises error (if ignore_404=False)
    #
    #
    # Act
    assert_that(repository.delete).raises(
        exceptions.NetdotDeleteError
    ).when_called_with(
        updated_product_type, confirm=False, ignore_404=False
    ).described_as(
        'Deleting non-existent obj should raise error'
    )


@pytest.mark.vcr
def test_create_update_delete_HorizontalCable(repository: Repository):
    #
    #
    # Create (all the stuff required for a HorizontalCable)
    #
    #
    # Arrange
    repository.disable_propose_changes()
    site = repository.create_new(netdot.Site(name='Test Site'))
    floor = repository.create_new(netdot.Floor(level='Test Floor', site=site))
    user_room = repository.create_new(netdot.Room(name='Test Room', floor=floor))
    closet_room = repository.create_new(
        netdot.Room(name='Test Closet Room', floor=floor)
    )
    closet = repository.create_new(netdot.Closet(name='Test Closet', room=closet_room))
    contact_list = repository.create_new(netdot.ContactList(name='Test Contact List'))
    cable_type = repository.create_new(netdot.CableType(name='Test Cable Type'))

    # Act
    horizontal_cable = repository.create_new(
        netdot.HorizontalCable(
            account='Test Account',
            faceplateid="TEST123",
            jackid="TEST123456",
            length="100",
            testpassed=True,
            contactlist=contact_list,
            closet=closet,
            room=user_room,
            type=cable_type,
        )
    )

    # Assert
    assert_that(horizontal_cable).is_not_none()
    assert_that(horizontal_cable.id).is_not_none()

    #
    #
    # Read
    #
    #
    # Act
    retrieved_horizontal_cable = repository.get_horizontalcable(horizontal_cable.id)

    # Assert
    assert_that(retrieved_horizontal_cable.account).is_equal_to('Test Account')

    #
    #
    # Update
    #
    #
    # Arrange
    horizontal_cable.account = "Updated"

    # Act
    updated_horizontal_cable = repository.update(horizontal_cable)

    # Assert
    assert_that(updated_horizontal_cable.account).is_equal_to("Updated")
    retrieved_horizontal_cable = repository.get_horizontalcable(horizontal_cable.id)
    assert_that(retrieved_horizontal_cable.account).is_equal_to(
        updated_horizontal_cable.account
    )

    #
    #
    # Delete
    #
    #
    # Act
    for obj in [
        horizontal_cable,
        cable_type,
        contact_list,
        closet,
        user_room,
        closet_room,
        floor,
        site,
    ]:
        obj.delete(confirm=False)


@pytest.mark.vcr
def test_create_update_delete_BackboneCable(repository: Repository):
    #
    #
    # Create (all the stuff required for a BackboneCable)
    #
    #
    # Arrange
    repository.disable_propose_changes()
    site = repository.create_new(netdot.Site(name='Test Site'))
    floor = site.add_floor(netdot.Floor(level='Test Floor'))
    start_room1 = floor.add_room(netdot.Room(name='Room 1'))
    start_room2 = floor.add_room(netdot.Room(name='Room 2'))
    end_room = floor.add_room(netdot.Room(name='End Room'))
    # Add closets to site
    start_closet1 = start_room1.add_closet(
        netdot.Closet(name='Closet 1')
    )
    start_closet2 = start_room2.add_closet(
        netdot.Closet(name='Closet 2')
    )
    end_closet = end_room.add_closet(
        netdot.Closet(name='End Closet')
    )
    cable_type = repository.create_new(netdot.CableType(name='Test Cable Type'))

    # Act - Create
    bb_cable: netdot.BackboneCable = cable_type.add_backbonecable(
        netdot.BackboneCable(
            name='Test Backbone Cable',
            start_closet=start_closet1,
            end_closet=end_closet,
        )
    )

    # Assert
    assert_that(bb_cable.id).is_not_none()

    # Act - Update
    bb_cable.name = 'Updated Test Backbone Cable'
    bb_cable.start_closet = start_closet2
    bb_cable.create_or_update()

    # Assert
    retrieved_bb_cable = repository.get_backbonecable(bb_cable.id)
    assert_that(retrieved_bb_cable.name).is_equal_to(bb_cable.name)
    assert_that(retrieved_bb_cable.start_closet).starts_with(start_closet2.name)
    assert_that(retrieved_bb_cable.start_closet_xlink).is_equal_to(start_closet2.id)

    # Cleanup
    for obj in [
        bb_cable,
        cable_type,
        start_closet1,
        end_closet,
        start_room1,
        end_room,
        floor,
        site,
    ]:
        obj.delete(confirm=False)


@pytest.mark.vcr
def test_add_backbone_cable_to_closet(repository: Repository):
    #
    #
    # Create (all the stuff required for a BackboneCable)
    #
    #
    # Arrange
    repository.disable_propose_changes()
    site = repository.create_new(netdot.Site(name='Test Site'))
    floor = site.add_floor(netdot.Floor(level='Test Floor'))
    start_room = floor.add_room(netdot.Room(name='Room 1'))
    end_room = floor.add_room(netdot.Room(name='End Room'))
    # Add closets to site
    start_closet = start_room.add_closet(
        netdot.Closet(name='Closet 1')
    )
    end_closet = end_room.add_closet(
        netdot.Closet(name='End Closet')
    )
    cable_type = repository.create_new(netdot.CableType(name='Test Cable Type'))

    # Act - Create
    bb_cable = start_closet.add_backbonecable_as_start_closet(netdot.BackboneCable(
        name='Test Backbone Cable',
        end_closet=end_closet,
        type=cable_type,
    ))

    # Assert
    assert_that(bb_cable.id).is_not_none()
    assert_that(bb_cable.start_closet.id).is_equal_to(start_closet.id)
    assert_that(bb_cable.end_closet.id).is_equal_to(end_closet.id)

    # Cleanup
    for obj in [
        bb_cable,
        cable_type,
        start_closet,
        end_closet,
        start_room,
        end_room,
        floor,
        site,
    ]:
        obj.delete(confirm=False)
