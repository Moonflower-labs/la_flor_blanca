from flor_blanca.questions import bp
from flor_blanca.auth import login_required
from flor_blanca.postDb import save_message,get_db,tarot_query
from flask import render_template,session,request,redirect,url_for,flash
from flask_mail import Message
from flor_blanca.extensions import mail
from flor_blanca.auth  import increment_used_count,save_question_count

  

def question_page():
    username = session.get('username')
    user_id = session.get('id')
    used_questions = session.get('used_questions')
    if user_id:
        # remaining_question_count = max(3 - used_questions, 0) 
        remaining_question_count = 3 - int(used_questions) 

       
        return render_template('questions/index.html', username=username, remaining_question_count=remaining_question_count)
    else:
        return redirect(url_for('login'))


@bp.route('/questions', methods=['GET', 'POST'])
@login_required
def index():
        email= session.get('email')
        username = session.get('username')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT subscription_plan from users WHERE email = %s",(email,))
        plan = cursor.fetchone()

        if plan[0] is None:
            current_plan = "PERSONALIDAD"
        elif  plan[0] == 'price_1Ng3GzAEZk4zaxmwyZRkXBiW':
            current_plan = "ALMA"
        elif plan[0] == "price_1Ng3KKAEZk4zaxmwLuapT9kg":
            current_plan = "SPÍRITU"

        if request.method == 'POST':
            try:
                email = session.get('email')
                name = request.form.get('name')
                subject = request.form.get('flexRadioDefault')
                question = request.form.get('question')
                subscribe = request.form.get('subscribe')

                age = request.form.get('ageGroup')
                other = request.form.get('other')
                country = request.form.get('country')
                city = request.form.get('city')
                gender = request.form.get('gender')

                media = []
                for key, value in request.form.items():
                    if value == 'on':
                        media.append(key)
                        user_id = session.get('id')
            except Exception as e:
                return str(e)

            if user_id:

                used_questions = session.get('used_questions')

                if used_questions < 3:
                    try:
                        msg = Message('Hola de la Flor Blanca!', sender='laflorBlanca',
                                  recipients=['alex.landin@hotmail.com'])
                        msg.body = f"email: {email},\nname: {name},\nsubject: {subject},\ngender: {gender},\nquestion: {question},\nsubscribe: {subscribe},\nheard of us:{media},\nage group: {age},\nother: {other},\n{country},\n{city}"
                        mail.send(msg)

                        save_message(email, name, subject, question, gender, age, media, country, city, subscribe,current_plan)
                        
                        flash('Tu pregunta ha sido enviada correctamente.')                      
                        increment_used_count()
                        used_questions = session.get('used_questions')
                        save_question_count()
                        remaining_question_count = max(3 - used_questions, 0) 
                       
                        return redirect(url_for('questions.message_sent',remaining_question_count=remaining_question_count))
                    
                    except Exception as e:
                        return str(e)
                    
                else:
                    flash('Has usado el máximo de 3 preguntas por mes.')

        return question_page()


@bp.route('/questions/sent', methods=['GET', 'POST'])
@login_required
def message_sent():

    remaining_question_count = request.args.get('remaining_question_count')
    

    return render_template('questions/sent.html', remaining_question_count=remaining_question_count)



@bp.route('/questions/tarot', methods=['POST'])
def save_tarot_query():
        email= session.get('email')
        username = session.get('username')
        question = request.form.get('questionTarot')
        info = request.form.get('info')
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT subscription_plan from users WHERE email = %s",(email,))
        plan = cursor.fetchone()

        if plan[0] is None:
            current_plan = "PERSONALIDAD"
        elif  plan[0] == 'price_1Ng3GzAEZk4zaxmwyZRkXBiW':
            current_plan = "ALMA"
        elif plan[0] == "price_1Ng3KKAEZk4zaxmwLuapT9kg":
            current_plan = "SPÍRITU"

        if request.method == 'POST':
            try:
                tarot_query(question,info,current_plan)

                return redirect(url_for('questions.message_sent'))
            except Exception as e:
                return str(e)



