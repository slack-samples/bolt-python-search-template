from slack_bolt import App

from .functions import handle_search_event, handle_filters_event


def register_listeners(app: App):
    app.function("search", auto_acknowledge=False, ack_timeout=10)(handle_search_event)
    app.function("filters", auto_acknowledge=False)(handle_filters_event)
