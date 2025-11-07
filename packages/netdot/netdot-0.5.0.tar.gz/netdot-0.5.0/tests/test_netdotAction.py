from assertpy import assert_that

from netdot import ProductType
from netdot.actions import NetdotAction, ActionTypes

def test_repr():
    # Arrange
    obj = NetdotAction(ActionTypes.CREATE, 123, ProductType(name="EXAMPLE2", info='TEST'), None)

    # Act
    result = obj.__repr__()

    # Assert
    assert_that(result).is_equal_to("NetdotAction(action_type=ActionTypes.CREATE, id=123, new_data=ProductType(id=None, info='TEST', name='EXAMPLE2'), old_data=None)")
    reconstructed = eval(result)
    assert_that(reconstructed).is_type_of(NetdotAction)
    assert_that(reconstructed.new_data).is_type_of(ProductType)
    assert_that(reconstructed.new_data.name).is_equal_to("EXAMPLE2")
