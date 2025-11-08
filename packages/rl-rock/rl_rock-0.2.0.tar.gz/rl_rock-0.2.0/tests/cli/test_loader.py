import pytest

from rock.cli.loader import CommandLoader
from rock.logger import init_logger

logger = init_logger(__name__)


@pytest.mark.asyncio
async def test_load():
    subclasses = await CommandLoader.load(["rock/cli/command"])
    logger.info(f"subclasses is {subclasses}")
    assert len(subclasses) > 0
