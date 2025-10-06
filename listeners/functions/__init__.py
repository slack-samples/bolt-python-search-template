from slack_bolt import App

from .filters import filters_step_callback
from .search import search_step_callback


def register(app: App):
    app.function("search", auto_acknowledge=False)(search_step_callback)
    app.function("filters", auto_acknowledge=False)(filters_step_callback)
