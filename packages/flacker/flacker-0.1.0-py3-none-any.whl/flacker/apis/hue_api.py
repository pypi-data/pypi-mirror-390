from decimal import Decimal
import logging
from ..models import Capabilities, EngineFixture, FlackerApiInterface
from phue import Bridge
import logging
logger = logging.getLogger(__name__)


class HueApi(FlackerApiInterface):
    def __init__(self, ip: str) -> None:
        super().__init__()
        self.bridge = Bridge(ip)
        self.bridge.connect()
        logger.info("Hue API initialized")

    def update_fixture(self, fixtures: list[EngineFixture], time: Decimal) -> bool:
        for f in fixtures:
            if not f.changed:
                continue

            command = {
                "on": bool(f.on),
                "transitiontime": int(f.transition * 10),
            }

            # Set values based on capabilities
            if f.on:
                if f.fixture.capabilities in [
                    Capabilities.BRIGHTNESS,
                    Capabilities.COLOR,
                    Capabilities.TEMPERATURE,
                ]:
                    command["bri"] = int(f.brightness * 255)
                if f.fixture.capabilities in [Capabilities.COLOR]:
                    command["sat"] = int(f.saturation * 255)
                    command["hue"] = int(f.hue * 65535)
                if f.fixture.capabilities in [Capabilities.TEMPERATURE]:
                    command["ct"] = int(f.temperature / 10)

            # Apply update
            self.bridge.set_light(f.fixture.api_id, command)
        return True
