from flor_blanca.questions import bp
from flor_blanca.auth import login_required,required_spirit_plan,required_soul_plan,is_admin
from flor_blanca.postDb import save_message,get_db,tarot_query,live_query_save
from flask import render_template,session,request,redirect,url_for,flash,current_app
from flask_mail import Message
from flor_blanca.extensions import mail
from flor_blanca.auth  import increment_used_count,save_question_count,required_basic

  

def question_page():
    username = session.get('username')
    user_id = session.get('id')
    used_questions = session.get('used_questions')
    if user_id:
    
        remaining_question_count = 3 - int(used_questions) 

       
        return render_template('questions/index.html', username=username, remaining_question_count=remaining_question_count)
    else:
        return redirect(url_for('login'))


@bp.route('/questions', methods=['GET', 'POST'])
@login_required
@required_basic
def index():
        email= session.get('email')
        username = session.get('username')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT subscription_plan from users WHERE email = %s",(email,))
        plan = cursor.fetchone()

        if plan[0] is None  or plan[0]=='price_1Ng3CfAEZk4zaxmwMXEF9bfR':
            current_plan = "PERSONALIDAD"
        elif  plan[0] == 'price_1Ng3GzAEZk4zaxmwyZRkXBiW':
            current_plan = "ALMA"
        elif plan[0] == "price_1Ng3KKAEZk4zaxmwLuapT9kg":
            current_plan = "ESPÍRITU"

        if request.method == 'POST':
            user_id = session.get('user_id')
            try:
               
                email = session.get('email')
                name = request.form.get('name')
                subject = request.form.get('flexRadioDefault')
                question = request.form.get('question')
                age = request.form.get('ageGroup')
                other = request.form.get('another')
                country = request.form.get('country')
                city = request.form.get('city')
                gender = request.form.get('gender')

                media = []
                for key, value in request.form.items():
                    if value == 'on':
                        media.append(key)
                if other:
                        media.append(other)
                user_id = session.get('id')
            except Exception as e:
                 current_app.logger.error("An error occurred while processing the form submission: %s", str(e))
                 flash('Ha ocurrido un error procesando el formulario. Por favor pruebe más tarde.')
                 return redirect(url_for('questions.index'))

            if user_id:

                used_questions = session.get('used_questions')

                if used_questions < 3:
                    try:
                                                                                                            
                        save_message(email, name, subject, question, gender, age, media, country, city,current_plan)
                        
                        flash('Tu pregunta ha sido enviada correctamente.')                      
                        increment_used_count()
                        used_questions = session.get('used_questions')
                        save_question_count()
                        remaining_question_count = max(3 - used_questions, 0) 

                        msg = Message('Pregunta para La Flor Blanca!', sender='admin@thechicnoir.com',
                                  recipients=['alex.landin@hotmail.com','admin@thechicnoir.com'])
                        msg.body = f"Email: {email},\nPlan: {current_plan}\nName: {name},\nSubject: {subject},\nGender: {gender},\nQuestion: {question},\nHeard of us:{media},\nAge group: {age},\n{country},\n{city}"
                        mail.send(msg)
                        current_app.logger.info(" Question sent to admin")

                        flash(f'Tu pregunta ha sido enviada, gracias.    Preguntas restantes este mes {remaining_question_count}')
                       
                        return redirect(url_for('questions.index',remaining_question_count=remaining_question_count))
                    
                    except Exception as e:
                        current_app.logger.error("An error occurred while processing the form submission: %s", str(e))
                        flash('Ha ocurrido un error procesando el formulario. Por favor pruebe más tarde.')
                        return redirect(url_for('questions.index'))
                    
                else:
                    flash('Has usado el máximo de 3 preguntas por mes.')

        return question_page()


@bp.route('/questions/sent', methods=['GET', 'POST'])
@login_required
def message_sent():
    username = session.get('username')
    remaining_question_count = request.args.get('remaining_question_count')
    

    return render_template('questions/sent.html', remaining_question_count=remaining_question_count,username=username)



@bp.route('/questions/tarot', methods=['POST'])
@login_required
@required_soul_plan
def save_tarot_query():
        email= session.get('email')
        username = session.get('username')
        question = request.form.get('questionTarot')
        info = request.form.get('info')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT subscription_plan,tarot_used_questions from users WHERE email = %s",(email,))
        results = cursor.fetchone()
        tarot_used_questions = results[1]
        if results[0] is None  or results[0]=='price_1Ng3CfAEZk4zaxmwMXEF9bfR':
            current_plan = "PERSONALIDAD"
        elif  results[0] == 'price_1Ng3GzAEZk4zaxmwyZRkXBiW':
            current_plan = "ALMA"
        elif results[0] == "price_1Ng3KKAEZk4zaxmwLuapT9kg":
            current_plan = "SPÍRITU"

        if request.method == 'POST':
            if tarot_used_questions == 0:
                try:
                    tarot_query(question,info,current_plan,email)
                   
               
                    cursor.execute('UPDATE users SET tarot_used_questions=%s WHERE email=%s', (1,email)) 
                    remaining_question_count = 0

                    # SEND MAIL TO ADMIN
                    msg = Message('Pregunta TAROT para La Flor Blanca!', sender='admin@thechicnoir.com',
                                  recipients=['alex.landin@hotmail.com','admin@thechicnoir.com'])
                    msg.body = f"Email: {email},\nPlan: {current_plan},\nQuestion: {question},\nInfo: {info}"
                    mail.send(msg)
                    current_app.logger.info(" Question sent to admin")
                    
                    flash(f'Tu pregunta ha sido enviada, gracias.    Preguntas restantes este mes {remaining_question_count}')
                    

                    return redirect(url_for('answers.index',remaining_question_count=remaining_question_count))
                except Exception as e:
                        current_app.logger.error("An error occurred while processing the form submission: %s", str(e))
                        flash('Ha ocurrido un error procesando el formulario. Por favor pruebe más tarde.')
                        return redirect(url_for('questions.index'))
            
            else:

                flash("No te quedan preguntas de tarot este mes")

                return redirect(url_for('answers.index'))


@bp.route('/questions/live', methods=['POST','GET'])
@login_required
@required_spirit_plan
def live_query():
        email= session.get('email')
        question = request.form.get('questionLive')
        username = session.get('username')
        db = get_db()
        cursor = db.cursor()

        if request.method == 'POST':
          
            cursor.execute("SELECT subscription_plan,live_used_questions from users WHERE email = %s",(email,))
            results = cursor.fetchone()
            live_used_questions = results[1]
            if results[0] is None or results[0]=='price_1Ng3CfAEZk4zaxmwMXEF9bfR':
                current_plan = "PERSONALIDAD"
            elif  results[0] == 'price_1Ng3GzAEZk4zaxmwyZRkXBiW':
                current_plan = "ALMA"
            elif results[0] == "price_1Ng3KKAEZk4zaxmwLuapT9kg":
                current_plan = "ESPÍRITU"

            if live_used_questions == 0:
                try:
                    live_query_save(question,current_plan,email)
                    # * UPDATE LIVE COUNT FOR USER                
                    cursor.execute('UPDATE users SET live_used_questions=%s WHERE email=%s', (1,email)) 
                    remaining_question_count = 0

                    msg = Message('Pregunta LIVE para La Flor Blanca!', sender='admin@thechicnoir.com',
                                  recipients=['alex.landin@hotmail.com','admin@thechicnoir.com'])
                    msg.body = f"Email: {email},\nPlan: {current_plan},\nQuestion: {question}"
                    mail.send(msg)
                    current_app.logger.info(" Question sent to admin")

                    flash(f'Tu pregunta ha sido enviada, gracias.    Preguntas restantes este mes {remaining_question_count}')

                    return redirect(url_for('questions.live_query',remaining_question_count=remaining_question_count))
                except Exception as e:
                        current_app.logger.error("An error occurred while processing the form submission: %s", str(e))
                        flash('Ha ocurrido un error procesando el formulario. Por favor pruebe más tarde.')
                        return redirect(url_for('questions.index'))
            
            else:

                flash("No te quedan preguntas en directo este mes")

                return redirect(url_for('questions.live_query'))
            
        else:
            cursor.execute('SELECT *  FROM live_sessions')
            live_sessions = cursor.fetchall()
            print(live_sessions)
        
            return render_template('questions/live.html',live_sessions=live_sessions,username=username)
        


@bp.route('/add/live_session', methods=['POST'])
@login_required
@is_admin
def add_live_session():
    link = request.form.get('link')
    title = request.form.get('title')
    description = request.form.get('description')
    extra_info = request.form.get('extra_info')

    db = get_db()
    cursor= db.cursor()
    cursor.execute('INSERT INTO live_sessions(link,title,description,extra_info)VALUES(%s,%s,%s,%s) ',(link,title,description,extra_info))
    message = " Sesión guardada con éxito"
    flash(message)

    return redirect(url_for('questions.live_query'))




@bp.route('/delete/live_session', methods=['POST'])
@login_required
@is_admin
def delete_live_session(): 
    link = request.form.get('link_id')
    print(link)

    db = get_db()
    cursor= db.cursor()
    cursor.execute('DELETE FROM live_sessions WHERE id=%s',(link,))
    message = " Sesión eliminada con éxito"
    flash(message)

    return redirect(url_for('questions.live_query'))