import functools,os
import secrets
from flask_mail import Message
from flor_blanca.extensions import mail

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
            error = 'Nombre de usuario es obligatorio.'
        elif not password:
            error = 'Contraseña es obligatoria.'
        elif not email:
            error = 'Email es obligatorio.'

        if error is None:
            try:
                cursor = db.cursor()
                cursor.execute(
                     "INSERT INTO users (username, password, email) VALUES (%s, %s,%s)",
                    (username, generate_password_hash(password), email),

                )

            except db.IntegrityError:
                error = f"Nombre de usuario o email ya está registrado."
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
            error = 'Email o Contraseña incorrecto.'
        elif not check_password_hash(user[2], password):
            error = 'Contraseña incorrecta.'

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




def save_question_count(count):
     email = session.get('email')  
     db = get_db()  
     cursor = db.cursor()
   
     cursor.execute('UPDATE users SET used_questions=%s WHERE email = %s',(count,email))
     current_app.logger.info(f" Question count saved correctly\nValues\nUsed Questions: {count}")
    
      
      


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
    
        if  customer_id is None:
                        message = 'No puedes acceder a los servicios de Tienda,  Preguntas, planes de Personalidad,  Alma o Espíritu, Tarot y Sesión en Directo. Para tener acceso a estos servicios debes comprar un plan de suscripción. Si tienes más dudas consulta nuestra sección de Ayuda.'
                        flash(message)
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
        
        else:

            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT subscription_plan FROM users WHERE email = %s', (email,))
            subscription_plan = cursor.fetchone()
         
    
            if  subscription_plan is None or subscription_plan[0]  != "price_1Ng3KKAEZk4zaxmwLuapT9kg" :
                 message = 'No puedes acceder a los servicios de Tienda,  Preguntas, planes de Personalidad,  Alma o Espíritu, Tarot y Sesión en Directo. Para tener acceso a estos servicios debes comprar un plan de suscripción. Si tienes más dudas consulta nuestra sección de Ayuda.'
                 flash(message)
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
            message = 'No puedes acceder a los servicios de Tienda,  Preguntas, planes de Personalidad,  Alma o Espíritu, Tarot y Sesión en Directo. Para tener acceso a estos servicios debes comprar un plan de suscripción. Si tienes más dudas consulta nuestra sección de Ayuda.'
            flash(message)
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




@bp.route('/reset_password',methods=['POST','GET'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # generate cookie
        secret_token = secrets.token_hex(16)
        # save cookie to users details
        db = get_db()
        cursor = db.cursor()
        cursor.execute('UPDATE users set password_recovery=%s WHERE email=%s',(secret_token,email))


        try:     
             
                 msg = Message('Resetea tu contraseña con La Flor Blanca', sender='admin@thechicnoir.com',
                                  recipients=[email])
           
           
               
                 msg.body = f"Has recibido este email porque te has olvidado tu contraseña. Utiliza el siguiente código para proceder:\n{secret_token}"
           
                 mail.send(msg)
                 current_app.logger.info(' Email sent to user')

                 return redirect(url_for('auth.validate_password_reset',email=email))

        except Exception as e:
                 
                 return current_app.logger.warning(str(e))

    return render_template('auth/resetPassword.html')




@bp.route('/validate_password_reset',methods=['POST','GET'])
def validate_password_reset():
     if request.method== 'POST':
       cookie = request.form.get('cookie')
       email = request.args.get('email')
       if validate_cookie(cookie,email):
            
            return redirect(url_for('auth.newPassword',email=email))
       
       else:
            error='El código no coincide con nuestros records'
            flash(error)
            return redirect(url_for('auth.login'))
     
     return render_template('auth/cookie_validate.html')
       



@bp.route('/newPassword',methods=['POST','GET'])
def newPassword():
      email = request.args.get('email')
      if request.method== 'POST':
           password = request.form.get('password')
           db= get_db()
           cursor = db.cursor()
           cursor.execute( "UPDATE users set password=%s,password_recovery=%s WHERE email=%s",
                    ( generate_password_hash(password),None, email),) 
           return redirect(url_for('auth.login'))

      return render_template('auth/newPassword.html')





def validate_cookie(cookie,email):
     
     db = get_db()
     cursor = db.cursor()
     cursor.execute('SELECT password_recovery FROM users WHERE email=%s',(email,))
     stored_cookie = cursor.fetchone()
     if stored_cookie[0]!=cookie:
          return False
     else:
          return True
     
     

@bp.route('/delete_account',methods=['POST','GET'])
@login_required
def delete_account():
      email = session.get('email')
      if request.method== 'POST':
           db= get_db()
           cursor = db.cursor()
           cursor.execute( "SELECT customer_id,subscription_status,subscription_plan FROM users WHERE email=%s",
                    (email,)) 
           user = cursor.fetchone()
           if user[0] is None and user[1] is None and user[2] is None:
                cursor.execute( "DELETE FROM users WHERE email=%s",( email,)) 
                current_app.logger.info(f'User with email: {email} succesfully deleted from Database')
                session.clear()
                message = 'Tu cuenta ha sido eliminada'
                flash(message)
                
                return redirect(url_for('index'))
           
           else:
                message = 'Tu cuenta no se ha podido borrar porque todavía tiene una suscripción activa'
                flash(message)
                return redirect(url_for('index'))

      return render_template('auth/deleteAccount.html')

