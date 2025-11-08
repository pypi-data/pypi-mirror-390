from decimal import Decimal
import logging
from ..models import Capabilities, EngineFixture, FlackerApiInterface
from hue_entertainment_pykit import create_bridge, Entertainment, Streaming
import logging
logger = logging.getLogger(__name__)


class HueEntertainmentApi(FlackerApiInterface):
    def __init__(
        self, ip: str, entertainment_zone_name: str, color_mode: str = "xyz"
    ) -> None:
        """Color mode can be rgb or xyb."""
        super().__init__()
        self.color_mode = color_mode

        # Set up the Bridge instance with the all needed configuration
        self._bridge = create_bridge(
            identification="4abb74df-5b6b-410e-819b-bf4448355dff",
            rid="d476df48-83ad-4430-a104-53c30b46b4d0",
            ip_address=ip,
            swversion=1962097030,
            username="8nuTIcK2nOf5oi88-5zPvV1YCt0wTHZIGG8MwXpu",
            hue_app_id="94530efc-933a-4f7c-97e5-ccf1a9fc79af",
            clientkey="B42753E1E1605A1AB90E1B6A0ECF9C51",
            name="Hue Bridge for Entertainment",
        )

        # Set up the Entertainment API service
        entertainment_service = Entertainment(self._bridge)

        # Fetch all Entertainment Configurations on the Hue bridge
        entertainment_configs = entertainment_service.get_entertainment_configs()

        if entertainment_zone_name not in entertainment_configs:
            logger.error(
                f"Hue Entertainment Zone [{entertainment_zone_name}] not found. Options: {' | '.join(entertainment_configs.keys())}"
            )

        self.entertainment_config = entertainment_configs[entertainment_zone_name]

        # Set up the Streaming service
        self._streaming = Streaming(
            self._bridge,
            self.entertainment_config,
            entertainment_service.get_ent_conf_repo(),
        )

        # Start streaming messages to the bridge
        self._streaming.start_stream()
        self._streaming.set_color_space(self.color_mode)
        logger.info("Hue Entertainment API successfully initialized")

    def update_fixture(self, fixtures: list[EngineFixture], time: Decimal) -> bool:
        for f in fixtures:
            if not f.changed:
                continue

            color = self._hsv_to_rgb(f.hue, f.saturation, f.brightness)
            if self.color_mode == "xyb":
                color = self._rgb_to_xyz(*color)

            # Apply update
            self._streaming.set_input((*color, int(f.fixture.api_id)))
        return True

    def _hsv_to_rgb(self, h, s, v) -> tuple[float, float, float]:
        """
        Convert HSV values to RGB.s
        h: 0-1, s: 0-1, v: 0-1
        Returns: r, g, b in 0-1 range
        """
        if s == 0:
            r = g = b = v
        else:
            i = int(h * 6.0)
            f = (h * 6.0) - i
            p = v * (1.0 - s)
            q = v * (1.0 - s * f)
            t = v * (1.0 - s * (1.0 - f))
            if i == 0:
                r, g, b = v, t, p
            elif i == 1:
                r, g, b = q, v, p
            elif i == 2:
                r, g, b = p, v, t
            elif i == 3:
                r, g, b = p, q, v
            elif i == 4:
                r, g, b = t, p, v
            elif i == 5:
                r, g, b = v, p, q
            else:
                r = g = b = 0
        return r, g, b

    def _rgb_to_xyz(self, r, g, b) -> tuple[float, float, float]:
        """
        Convert RGB values to XYZ.
        r, g, b: 0-1 range
        Returns: x, y, z
        """
        # Convert RGB to linear RGB
        r = r if r <= 0.04045 else ((r + 0.055) / 1.055) ** 2.4
        g = g if g <= 0.04045 else ((g + 0.055) / 1.055) ** 2.4
        b = b if b <= 0.04045 else ((b + 0.055) / 1.055) ** 2.4

        r *= 100.0
        g *= 100.0
        b *= 100.0

        # Observer = 2°, Illuminant = D65
        x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
        y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
        z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041

        return x, y, z
