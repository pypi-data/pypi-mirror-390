import json
import logging
from abc import ABC, abstractmethod

from rock.utils import FileUtil

logger = logging.getLogger(__name__)


class EnvBuilder(ABC):
    @abstractmethod
    async def build(self, instance_record: dict[str, str] | None = None, **kwargs):
        """Build environment."""
        pass

    async def build_batch(self, dataset: str, **kwargs):
        """Build environments in batch."""
        record_index = 0
        line_count = await FileUtil.get_line_count(dataset)
        with open(dataset, encoding="utf-8") as file:
            for line in file:
                if not line:
                    logger.info("line is empty, finished")
                    break
                line_content = line.strip()
                instance_record = json.loads(line_content)

                logger.info(f"start to handle line {record_index}/{line_count}")
                logger.debug(f"record: {instance_record}")
                try:
                    await self.build(instance_record=instance_record, **kwargs)
                except Exception as e:
                    logger.error(f"build for {record_index}/{line_count} failed, {str(e)}", exc_info=True)
                record_index += 1

    @abstractmethod
    async def verify(self, **kwargs):
        """Verify environment."""
        pass
