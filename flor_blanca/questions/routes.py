from flor_blanca.questions import bp
from flor_blanca.auth import login_required
from flor_blanca.postDb import save_message
from flask import render_template,session,request,redirect,url_for,flash
from flask_mail import Message
from flor_blanca.extensions import mail
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

current_month = datetime.datetime.now().month


scheduler = BackgroundScheduler()

def reset_question_count():
     session['question_count'] = 0

# Schedule job to run at the start of each month
scheduler.add_job(reset_question_count, 'cron', month='*', day=1, hour=0, minute=0)

# Start the scheduler
scheduler.start()


def question_page():
    username = session.get('username')
    user_id = session.get('id')
    count = session.get('question_count',0)  
    if user_id:
        remaining_question_count = max(3 - count, 0)  
        return render_template('questions/index.html', username=username, remaining_question_count=remaining_question_count)
    else:
        return redirect(url_for('login'))

def increment_question_count():
    current_month = datetime.datetime.now().month
    if 'question_count_month' not in session or session['question_count_month'] != current_month:
        session['question_count'] = 1
        session['question_count_month'] = current_month
    else:
        session['question_count'] = session.get('question_count', 0)
        session['question_count'] = session['question_count'] + 1 if session['question_count'] is not None else 1
    session.permanent = True

@bp.route('/questions', methods=('GET', 'POST'))
@login_required
def index():
        username = session.get('username')

        if request.method == 'POST':
            email = request.form.get('email')
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

            if user_id:
                session['question_count'] = session.get('question_count', 0)

                if session['question_count'] < 3:
                    
                        msg = Message('Hello from the other side!', sender='laflorBlanca',
                                  recipients=['alex.landin@hotmail.com'])
                        msg.body = f"email: {email},\nname: {name},\nsubject: {subject},\ngender: {gender},\nquestion: {question},\nsubscribe: {subscribe},\nheard of us:{media},\nage group: {age},\nother: {other},\n{country},\n{city}"
                        mail.send(msg)

                        save_message(email, name, subject, question, gender, age, media, country, city, subscribe)
                        increment_question_count()
                        flash('Question submitted successfully.')
                        count = session.get('question_count',0) 
                        remaining_question_count = max(3 - count, 0)  
                        return redirect(url_for('questions.message_sent',remaining_question_count=remaining_question_count))
                    
                else:
                    flash('You have reached the maximum limit of 3 questions per month.')

        return question_page()


@bp.route('/questions/sent', methods=('GET', 'POST'))
@login_required
def message_sent():

    remaining_question_count = request.args.get('remaining_question_count')
    

    return render_template('questions/sent.html', remaining_question_count=remaining_question_count)






# @bp.route('/questions', methods=('GET','POST'))
# @login_required
# def index():
#     username = session.get('username')

#     def question_page():
#         user_id = session.get('id') 
#         count = session.get('question_count')
#         if user_id:
#             remaining_question_count = max(3 - count, 0)
#             return render_template('questions/index.html',username=username, remaining_question_count=remaining_question_count)
#         else:
#             return redirect(url_for('login'))

#     if request.method == 'POST':
#         email = request.form.get('email')
#         name = request.form.get('name')
#         subject = request.form.get('flexRadioDefault')
#         question = request.form.get('question')
#         subscribe = request.form.get('subscribe')
        
#         age = request.form.get('ageGroup')
#         other = request.form.get('other')
#         country = request.form.get('country')
#         city = request.form.get('city')
#         gender = request.form.get('gender')

#         media = []
#         for key, value in request.form.items():
#             if value == 'on':
#                 media.append(key)
#         user_id = session.get('id')
        
#         if user_id:
#             session['question_count'] = session.get('question_count', 0)

#             if session['question_count'] < 3:
#                 try:
#                     msg = Message('Hello from the other side!', sender='laflorBlanca', recipients=['alex.landin@hotmail.com'])
#                     msg.body = f"email: {email},\nname: {name},\nsubject: {subject},\ngender: {gender},\nquestion: {question},\nsubscribe: {subscribe},\nheard of us:{media},\nage group: {age},\nother: {other},\n{country},\n{city}"
#                     mail.send(msg)
            
#                     save_message(email, name, subject, question, gender, age, media, country, city, subscribe)
#                     increment_question_count()
#                     flash('Question submitted successfully.')
        
#                     return redirect(url_for('questions.message_sent'))
#                 except:
#                     pass
#         else:
#             flash('You have reached the maximum limit of 3 questions per month.')

#     return question_page()



# @bp.route('/questions/sent', methods=('GET','POST'))
# @login_required
# def message_sent():

#     return render_template ('questions/sent.html')



# def increment_question_count():
#     current_month = datetime.datetime.now().month
#     if 'question_count_month' not in session or session['question_count_month'] != current_month:
#         session['question_count'] = 1
#         session['question_count_month'] = current_month
#     else:
#         session['question_count'] = session.get('question_count', 0)
#         session['question_count'] = session['question_count'] + 1 if session['question_count'] is not None else 1
#     session.permanent = True



