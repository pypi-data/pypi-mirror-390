from decimal import Decimal
from ..models import EngineFixture, FlackerApiInterface, KeyframeValue, Parameter
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
logger = logging.getLogger(__name__)


class PlotApi(FlackerApiInterface):
    def __init__(self) -> None:
        super().__init__()
        self.history: dict[str, dict[Parameter |
                                     str, list[KeyframeValue]]] = {}

    def update_fixture(self, fixtures: list[EngineFixture], time: Decimal) -> bool:
        for f in fixtures:
            if f.fixture.id not in self.history.keys():
                self.history[f.fixture.id] = (  # type: ignore # pyright: ignore[reportArgumentType]
                    {
                        "name": f.fixture.name,
                        Parameter.ON: [],
                        Parameter.BRIGHTNESS: [],
                        Parameter.SATURATION: [],
                        Parameter.HUE: [],
                        Parameter.TEMPERATURE: [],
                        Parameter.TOPIC: [],
                        Parameter.TRANSITION: [],
                    }
                )

            self.history[f.fixture.id][Parameter.ON].append(f.on)
            self.history[f.fixture.id][Parameter.BRIGHTNESS].append(f.brightness)
            self.history[f.fixture.id][Parameter.SATURATION].append(f.saturation)
            self.history[f.fixture.id][Parameter.HUE].append(f.hue)
            self.history[f.fixture.id][Parameter.TEMPERATURE].append(f.temperature)
            self.history[f.fixture.id][Parameter.TOPIC].append(f.topic)
            self.history[f.fixture.id][Parameter.TRANSITION].append(f.transition)

        return True

    def save_plot(self, path: str, *, order_ids: list[str] | None = None) -> None:
        """Creates an interactive multi-plot HTML with one subplot per fixture."""
        num_fixtures = len(self.history)
        if num_fixtures == 0:
            logger.warning("No history to plot.")
            return

        if order_ids is None:
            order_ids = sorted(self.history.keys())

        # Prepare subplots
        fig = make_subplots(
            rows=num_fixtures,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=[
                f"Fixture {self.history[f]['name']} [{f}]" for f in order_ids
            ],
        )

        # Plot each fixture
        for row, fixture_id in enumerate(order_ids, start=1):
            params = self.history[fixture_id]
            # brightness as time index
            time = list(range(len(params[Parameter.BRIGHTNESS])))

            def add_trace(y, name, color, dash=None):
                fig.add_trace(
                    go.Scatter(
                        x=time,
                        y=y,
                        mode="lines",
                        name=name,
                        line=dict(color=color, dash=dash,
                                  shape="hv"),  # "steps-post"
                    ),
                    row=row,
                    col=1,
                )

            # Boolean "On" encoded as 1/0
            add_trace([1 if v else 0 for v in params[Parameter.ON]],
                      "On (1/0)", "red", "dash")

            # Numeric parameters
            add_trace(params[Parameter.BRIGHTNESS], "Brightness", "black")
            add_trace(params[Parameter.SATURATION], "Saturation", "orange")
            add_trace(params[Parameter.HUE], "Hue", "green")
            add_trace(params[Parameter.TEMPERATURE], "Temperature", "purple")
            add_trace(params[Parameter.TRANSITION], "Transition", "grey")

        fig.update_layout(
            height=400 * num_fixtures,
            width=1000,
            title_text="Fixture Parameter History",
            showlegend=True,
        )

        fig.write_html(path)
        logger.info(f"Saved interactive plot to: {path}")
