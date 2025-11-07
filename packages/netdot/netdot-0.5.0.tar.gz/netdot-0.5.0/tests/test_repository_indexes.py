import pytest
from assertpy import assert_that

from netdot import Repository


@pytest.mark.vcr()
def test_infer_product(repository: Repository):
    # Arrange
    device = repository.get_device(10091)

    # Act
    product = device.infer_product()

    # Assert
    assert_that(product.type).is_equal_to('Switch')
    assert_that(product.name).is_equal_to('EX3400-48P')