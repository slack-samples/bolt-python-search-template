from slack_bolt import App

from .entity_details_requested import entity_details_requested_callback


def register(app: App):
    app.event("entity_details_requested")(entity_details_requested_callback)
