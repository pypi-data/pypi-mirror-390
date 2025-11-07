import pytest


@pytest.mark.vcr
def test_load_rooms(repository):
    # Arrange
    site = repository.get_site(137)

    # Act
    site.load_rooms()

    # Assert
    pass


@pytest.mark.vcr
def test_load_closets(repository):
    # Arrange
    site = repository.get_site(137)

    # Act
    site.load_closets()

    # Assert
    pass