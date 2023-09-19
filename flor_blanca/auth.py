import functools,os

from flask import(
    Blueprint, flash , g, redirect, render_template, request, 
    session, url_for,current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
from flor_blanca.postDb import get_db


   
bp = Blueprint('auth', __name__, url_prefix='/auth')

ADMIN_LIST = os.getenv('ADMIN_LIST')

@bp.route('/register', methods=('GET','POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Email is required.'

        if error is None:
            try:
                cursor = db.cursor()
                cursor.execute(
                     "INSERT INTO users (username, password, email) VALUES (%s, %s,%s)",
                    (username, generate_password_hash(password), email),

                )

            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
        
        flash(error)
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        
        if user is None:
            error = 'Incorrect email address or password.'
        elif not check_password_hash(user[2], password):
            error = 'Incorrect password.'

        if error is None:          
            
            session['id'] = user[0]
            session['username'] = user[1]
            session['email'] = user[3]
            session['customer_id'] = user[5]
            session['used_questions'] = int(user[8])
            current_app.logger.info(session['used_questions'])
          
        
            
            if session['email'] in ADMIN_LIST :
                    session['role'] = 'admin'
            else:
                    session['role'] = 'user'
                    
            return redirect(url_for('index',username=user[1]))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('id')

    if user_id is None:
        g.user = None
    else:
        cursor = get_db().cursor()
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        g.user = cursor.fetchone()

        cursor.close() 

@bp.route('/logout')
def logout():
   
    
    
    session.clear()
    

    return redirect(url_for('index'))




def save_question_count():
     email = session.get('email')    
     used_questions = session.get('used_questions')   
     db = get_db()
     cursor = db.cursor()
     cursor.execute('UPDATE users SET used_questions=%s WHERE email = %s',(used_questions,email))
     current_app.logger.info(f" Question count saved correctly\nValues\nUsed Questions: {used_questions}")
    
    

def increment_used_count():
       
        used_questions = session.get('used_questions')
        used_questions += 1
        session['used_questions'] = used_questions
      
      


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


def required_basic(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        email = session.get('email')
        role = session.get('role')  

        if role == 'admin':
            return view(**kwargs)

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT customer_id FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        customer_id = user[0]
    
        if  customer_id is None or customer_id == '' :
            return redirect(url_for('index'))

        return view(**kwargs)

    return wrapped_view



def required_spirit_plan(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        email = session.get('email')
        role = session.get('role')  

        if role == 'admin':
            return view(**kwargs)

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT subscription_plan FROM users WHERE email = %s', (email,))
        subscription_plan = cursor.fetchone()

    
        if  subscription_plan is None or subscription_plan[0]  != "price_1Ng3KKAEZk4zaxmwLuapT9kg" :
            return redirect(url_for('index'))

        return view(**kwargs)

    return wrapped_view


def required_soul_plan(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        email = session.get('email')
        role = session.get('role')  

        if role == 'admin':
            return view(**kwargs)
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT subscription_plan FROM users WHERE email = %s', (email,))
        subscription_plan = cursor.fetchone()
       
        if  subscription_plan is None or  subscription_plan[0]  != 'price_1Ng3KKAEZk4zaxmwLuapT9kg' and subscription_plan[0] != 'price_1Ng3GzAEZk4zaxmwyZRkXBiW' :
            return redirect(url_for('index'))

        return view(**kwargs)

    return wrapped_view

def is_admin(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        role = session.get('role')  

        if role != 'admin':
            
        
    
            return redirect(url_for('index'))

        return view(**kwargs)

    return wrapped_view

@bp.route('/denied')
def denied():

    return render_template('auth/denied.html')

