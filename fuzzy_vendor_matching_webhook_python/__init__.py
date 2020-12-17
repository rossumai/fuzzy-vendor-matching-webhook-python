import flask
from fuzzy_vendor_matching_webhook_python.webhook import vendor_matching


def create_app():
    app = flask.Flask(__name__)
    app.config.from_object(flask.config)
    # app.config["DEBUG"] = True
    app.route("/vendor_matching", methods=["POST"])(vendor_matching)
    return app
