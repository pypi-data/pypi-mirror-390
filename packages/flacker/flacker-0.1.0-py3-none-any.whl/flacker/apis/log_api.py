from decimal import Decimal
from ..models import EngineFixture, FlackerApiInterface
import logging
logger = logging.getLogger(__name__)


class LogApi(FlackerApiInterface):

    def update_fixture(self, fixtures: list[EngineFixture], time: Decimal) -> bool:
        for f in fixtures:
            logger.info(f)
        return True
