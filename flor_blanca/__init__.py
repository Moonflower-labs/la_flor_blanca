import os
from flask import Flask, render_template, session
import logging
from dotenv import load_dotenv
from config import Config


load_dotenv()


logging.basicConfig( level=logging.DEBUG)
def create_app(test_config=None):
      # create and configure the app
    app = Flask(__name__, instance_relative_config=True,static_url_path='',
           )
    
    app.config.from_mapping(
        
        DATABASE=os.getenv('DATABASE_URL') ,
        MAIL_SERVER = os.getenv('MAIL_SERVER'),
        MAIL_PORT = int(os.getenv('MAIL_PORT')),
        MAIL_USERNAME = os.getenv('MAIL_USERNAME'),
        MAIL_PASSWORD = os.getenv('MAIL_PASSWORD'),
        MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') == 'True',
        MAIL_USE_SSL = os.getenv('MAIL_USE_SSL') == 'True',
        
    )
    app.config.from_object(Config)
   

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    # @app.after_request
    # def add_security_headers(resp):
    #     resp.headers['Permissions-Policy'] = "geolocation=(),midi=(),camera=()"
    #     return resp

    from flor_blanca.postDb import init_app
    init_app(app)

    from flor_blanca.extensions import mail
    mail.init_app(app)
  
    @app.route('/')
    def index():
       
        username = session.get('username') 
        return render_template('index.html',username=username)

    from flor_blanca import auth
    app.register_blueprint(auth.bp)

    from flor_blanca.questions import bp as questions_bp
    app.register_blueprint(questions_bp)


    from flor_blanca.answers import bp as answers_bp
    app.register_blueprint(answers_bp)

    from flor_blanca.admin import bp as admin_bp
    app.register_blueprint(admin_bp)


    from . import server
    app.register_blueprint(server.bp)


    @app.route('/dashboard')
    def dashboard():
       email = session.get('email')
       username = session.get('username')
       return render_template('user/dashboard.html',email=email,username=username)







    return app
   

