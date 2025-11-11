#  Copyright (c) 2024 Russell Smiley
#
#  This file is part of click_logging_config.
#
#  You should have received a copy of the MIT License along with click_logging_config.
#  If not, see <https://opensource.org/licenses/MIT>.

import logging

import pytest
from click.testing import CliRunner


@pytest.fixture(autouse=True)
def cleanup_logging_handlers():
    """Clean up logging handlers between tests to prevent handler accumulation."""
    # Setup: store original handlers and level
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers[:]
    original_level = root_logger.level

    yield

    # Teardown: remove handlers that were added during the test
    current_handlers = root_logger.handlers[:]
    for handler in current_handlers:
        if (handler not in original_handlers) and (not handler.stream.closed):
            # This is a handler added during the test
            handler.flush()
            handler.close()
            root_logger.removeHandler(handler)

    # Restore original level
    root_logger.setLevel(original_level)


@pytest.fixture()
def click_runner() -> CliRunner:
    return CliRunner()
