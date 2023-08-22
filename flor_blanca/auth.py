import functools,os

from flask import(
    Blueprint, flash , g, redirect, render_template, request, 
    session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flor_blanca.postDb import get_db
# from flor_blanca.db import get_db

   
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
                # db.commit()
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
            session.clear()
            session['id'] = user[0]
            session['username'] = user[1]
            session['email'] = user[3]

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


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

@bp.route('/denied')
def denied():

    return render_template('auth/denied.html')

"""This decorator returns a new view function that wraps 
the original view it's applied to. The new function checks 
if a user is loaded and redirects to the login page otherwise. 
If a user is loaded the original view is called and continues normally. 
You'll use this decorator when writing the blog views.

"""