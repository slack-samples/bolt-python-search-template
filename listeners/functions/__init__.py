from slack_bolt import App

from .filters import filters_step_callback
from .search import search_step_callback


def register(app: App):
    app.function("search", auto_acknowledge=False, ack_timeout=10)(search_step_callback)
    app.function("filters", auto_acknowledge=False, ack_timeout=10)(filters_step_callback)
