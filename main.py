import os
from flask import Flask
from flask_restful import Resource, Api
from application import config
from application.config import LocalDevelopmentConfig
#from application.database import db
from flask_login import LoginManager
from application.controllers import register_routes
from application.login import login_bp
from datetime import datetime
from flask_uploads import UploadSet, configure_uploads, IMAGES

# create an UploadSet for images
images = UploadSet('images', IMAGES)

app = None
#api = None
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder="templates")
    if os.getenv('ENV', "development") == "production":
      raise Exception("Currently no production config is setup.")
    else:
      print("Staring Local Development")
      app.config.from_object(LocalDevelopmentConfig)
    
    # initialize the login manager 
    login_manager.init_app(app)

    # Define and register the load_user function
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)
    
    from application.database import db
    
    db.init_app(app)

    # configure Flask-Uploads
    configure_uploads(app, (images,))

    #api = Api(app)
    app.app_context().push()  
    return app    #, api

#app, api = create_app()
app = create_app()

# Import all the controllers so they are loaded
from application.controllers import *

# register the routes with the app
register_routes(app)
app.register_blueprint(login_bp)
# Add all restful controllers
#from application.api import UserAPI
#api.add_resource(UserAPI, "/api/user", "/api/user/<string:username>")

if __name__ == '__main__':
  # Run the Flask app
  app.run(host='0.0.0.0',port=8080)
