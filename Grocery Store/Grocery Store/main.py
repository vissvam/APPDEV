import os
from flask import Flask
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db


app = None

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.secret_key = "vishnuvamseechenga"
    if os.getenv('ENV', "development") == "production":
        raise Exception("Currently no production config is setup.")
    else:
        print("Starting Local Development")
        app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    return app

app = create_app()
app.app_context().push() 

from application.controllers import *


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)