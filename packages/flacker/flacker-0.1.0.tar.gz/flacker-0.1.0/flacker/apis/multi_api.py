from decimal import Decimal
from ..models import EngineFixture, FlackerApiInterface


class MultiApi(FlackerApiInterface):
    def __init__(self, apis: list[FlackerApiInterface]) -> None:
        super().__init__()
        self.apis = apis

    def update_fixture(self, fixtures: list[EngineFixture], time: Decimal) -> bool:
        success = True
        for api in self.apis:
            if not api.update_fixture(fixtures, time):
                success = False

        return success
