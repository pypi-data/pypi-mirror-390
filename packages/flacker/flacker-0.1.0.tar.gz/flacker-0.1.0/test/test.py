import logging
from decimal import Decimal
from time import sleep

from engine import Engine
from hue_api import HueApi
from models import Flickr, FlickrApiInterface
from multi_api import MultiApi
from plot_api import PlotApi

ip = "192.168.178.85"
id = 4


f = Flickr.load("test_flickr.json")


logging.getLogger().setLevel(logging.DEBUG)


plot = PlotApi()
apis: dict[str, FlickrApiInterface] = {"hue": MultiApi([HueApi(ip), plot])}

engine = Engine(f, apis)

engine.load_sequence("test")

step = 0.1
while engine.is_running:
    engine.step(Decimal.from_float(step))
    engine.propagate()
    sleep(step)

plot.save_plot("plot.png")
print("Done.")
