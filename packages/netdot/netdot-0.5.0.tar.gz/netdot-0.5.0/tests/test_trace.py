import logging

import pytest
from assertpy import assert_that

from netdot import Repository


@pytest.mark.vcr
def test_trace_every_byte(repository: Repository, caplog):
    # Arrange
    repository.enable_trace_downloads(1)
    caplog.set_level(logging.INFO)

    # Act
    site = repository.get_site(213)
    closets = site.load_closets()

    # Assert
    assert_that(caplog.text).matches('Total downloaded from Netdot')
    assert_that(len(caplog.text.split('Total downloaded from Netdot'))).is_greater_than(len(closets) + 1)

    # Cleanup
    repository.disable_trace_downloads()