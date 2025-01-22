from flask import Flask, blueprints, request


class Config:
    """
    config class to define developement environment configuration for the app
    """

    DEBUG = True
    DEVELOPMENT = True
    FLASK_DEBUG = True
    TESTING = True


secret = "2zYghUuf^&FpF$y2L&W5ZNfiHKu77"


def create_app():
    """
    Server configuration. Add Flask rules to config above.
    """

    app = Flask(__name__)

    app.config.from_object(Config())

    app.config["SECRET_KEY"] = secret

    register_blueprints(app)
    
    @app.route("/",methods=["POST"])
    def main():
        if request.method == "POST":
            data = request.form['data']
        return {"data":f"{data}"}

    return app


def register_blueprints(app):
    """
    Add created blueprints here.
    For example:

    from routes.Summarization import Summarization
    app.register_blueprint(Summarization,url_prefix='/Summarization')

    """
    from server.menu import menu

    app.register_blueprint(menu, url_prefix="/menu")

    from server.character import character

    app.register_blueprint(character, url_prefix="/character")

    from server.sentiment import sentiment

    app.register_blueprint(sentiment, url_prefix="/sentiments")

    from server.summarization import summary

    app.register_blueprint(summary, url_prefix="/summary")

    from server.thematics import thematics

    app.register_blueprint(thematics, url_prefix="/thematics")
