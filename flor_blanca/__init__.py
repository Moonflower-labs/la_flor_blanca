import os
from flask import Flask, render_template, session
import logging
from dotenv import load_dotenv
from config import ProductionConfig
from apscheduler.schedulers.background import BackgroundScheduler



load_dotenv()



logging.basicConfig(level=logging.INFO)
def create_app(test_config=None):
     
    app = Flask(__name__, instance_relative_config=True,static_url_path='',)
   

    
    app.config.from_object(ProductionConfig)
   

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
    
   

    from flor_blanca.postDb import init_app,get_db
    init_app(app)

    from flor_blanca.extensions import mail
    mail.init_app(app)

    scheduler = BackgroundScheduler()
    def reset_question_count():
       with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('UPDATE users SET used_questions=%s,tarot_used_questions=%s,live_used_questions=%s',(0,0,0))
        print("reset_question_count executed")

    # Schedule job to run at the start of each month
    scheduler.add_job(reset_question_count, 'cron', month='*', day=1, hour=0, minute=0)
    scheduler.start()
  
    @app.route('/')
    def index():
       
        username = session.get('username') 
        email = session.get('email') 
        return render_template('index.html',username=username,email=email)

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


    @app.route('/help')
    def help_page():
       email = session.get('email')
       username = session.get('username')
       return render_template('user/help.html',email=email,username=username)




    return app
   

