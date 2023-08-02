import os
from flask import Flask ,redirect, request, url_for, render_template
import stripe

stripe.api_key = 'sk_test_51LIRtEAEZk4zaxmwgkvrQLY710xrEQxpWy6wDfNbGB5dH7fnI8Z86XHp1d2Su0qFVV5D7YCMwao8J3UGSMinxJaM004g6MLmcl'
def create_app(test_config=None):
      # create and configure the app
    app = Flask(__name__, instance_relative_config=True,static_url_path='',
           )
    app.config.from_mapping(
        SECRET_KEY='dev',     # path where the SQLite database file will be saved.
        DATABASE=os.path.join(app.instance_path, 'flor_blanca.sqlite'),
    )

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

    # a simple page that says hello
    @app.route('/')
    def index():
        return render_template('index.html')
    

    from . import db
    db.init_app(app)


    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='blog')

    from . import server
    app.register_blueprint(server.bp)
    # app.add_url_rule('/', endpoint='index')
    @app.route('/checkout')
    def checkout():
       

        
        return render_template('checkout.html')

    
    return app
   
# flask --app flor_blanca run --debug
