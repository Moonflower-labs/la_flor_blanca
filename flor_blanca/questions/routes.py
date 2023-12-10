from flor_blanca.questions import bp
from flor_blanca.auth import login_required, required_spirit_plan, required_soul_plan, is_admin
from flor_blanca.postDb import save_message, get_db, tarot_query, live_query_save
from flask import render_template, session, request, redirect, url_for, flash, current_app, jsonify
from flask_mail import Message
from flor_blanca.extensions import mail
from flor_blanca.auth import save_question_count, required_basic


def question_page():
    username = session.get('username')
    user_id = session.get('id')
    db = get_db().cursor()
    db.execute('SELECT used_questions FROM users WHERE username =%s', (username,))
    used_questions = db.fetchone()

    if user_id:

        remaining_question_count = max(3 - int(used_questions[0]), 0)

        return render_template('questions/index.html', username=username, remaining_question_count=remaining_question_count)
    else:
        return redirect(url_for('login'))


@bp.route('/questions', methods=['GET', 'POST'])
@login_required
@required_basic
def index():
    email = session.get('email')
    username = session.get('username')
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT subscription_plan from users WHERE email = %s", (email,))
    plan = cursor.fetchone()

    if plan[0] is None or plan[0] == 'price_1Nk5XdAEZk4zaxmwo8ZFYOEv':
        current_plan = "PERSONALIDAD"
    elif plan[0] == 'price_1Nk5YMAEZk4zaxmws0AhQfIs':
        current_plan = "ALMA"
    elif plan[0] == "price_1Nk5YdAEZk4zaxmwEqqHWSS2":
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
            current_app.logger.error(
                "An error occurred while processing the form submission: %s", str(e))
            return jsonify({'message': 'Ha ocurrido un error y tu pregunta no se ha podido enviar.', 'error': str(e)}), 500

        if user_id:
            db = get_db().cursor()
            db.execute(
                'SELECT used_questions FROM users WHERE username =%s', (username,))
            results = db.fetchone()
            used_questions = int(results[0])

            try:

                save_message(email, name, subject, question, gender,
                             age, media, country, city, current_plan)

                used_questions += 1
                save_question_count(used_questions)
                remaining_question_count = max(3 - used_questions, 0)

                msg = Message('Pregunta para La Flor Blanca!', sender='admin@thechicnoir.com',
                              recipients=['alex.landin@hotmail.com', 'admin@thechicnoir.com'])
                msg.body = f"Email: {email}\nPlan: {current_plan}\nName: {name}\nSubject: {subject}\nGender: {gender}\nQuestion: {question}\nHeard of us:{media}\nAge group: {age}\nCountry: {country}\nCity: {city}"
                mail.send(msg)
                current_app.logger.info(" Question sent to admin")

                return jsonify({'message': f'Tu pregunta ha sido enviada, gracias.    Preguntas restantes este mes {remaining_question_count}', 'count': remaining_question_count}), 200

            except Exception as e:
                current_app.logger.error(
                    "An error occurred while processing the form submission: %s", str(e))

                return jsonify({'message': 'Ha ocurrido un error procesando el formulario. Por favor pruebe más tarde.', 'error': str(e)}), 500

    return question_page()


@bp.route('/questions/count', methods=['GET', 'POST'])
def questions_test():
    username = session.get('username')
    db = get_db().cursor()
    questionType = request.args.get('questionType')
    if questionType == 'basic':
        db.execute(
            'SELECT used_questions FROM users WHERE username =%s', (username,))
        count = db.fetchone()
        if count is not None:
            remainingCount = max((3 - int(count[0])), 0)
        else:
            remainingCount = 0

        return jsonify({'count': remainingCount, 'message': 'Count for plan Basic fetched correctly.'}), 200

    elif questionType == 'tarot':
        db.execute(
            'SELECT tarot_used_questions FROM users WHERE username =%s', (username,))
        count = db.fetchone()
        if count is not None:
            remainingCount = 1 - int(count[0])
        else:
            remainingCount = 0

        return jsonify({'count': remainingCount, 'message': 'Count for tarot fetched correctly.'}), 200

    elif questionType == 'live':
        db.execute(
            'SELECT live_used_questions FROM users WHERE username =%s', (username,))
        count = db.fetchone()
        if count is not None:
            remainingCount = 1 - int(count[0])
        else:
            remainingCount = 0

        return jsonify({'count': remainingCount, 'message': 'Count for live fetched correctly.'}), 200


@bp.route('/questions/tarot', methods=['POST'])
@login_required
@required_soul_plan
def save_tarot_query():
    email = session.get('email')
    username = session.get('username')
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT subscription_plan,tarot_used_questions from users WHERE email = %s", (email,))
    results = cursor.fetchone()

    if results[0] is None or results[0] == 'price_1Nk5XdAEZk4zaxmwo8ZFYOEv':
        current_plan = "PERSONALIDAD"
    elif results[0] == 'price_1Nk5YMAEZk4zaxmws0AhQfIs':
        current_plan = "ALMA"
    elif results[0] == "price_1Nk5YdAEZk4zaxmwEqqHWSS2":
        current_plan = "SPÍRITU"

    if request.method == 'POST':

        question = request.form.get('questionTarot')
        info = request.form.get('info')
        try:
            tarot_query(question, info, current_plan, email)

            cursor.execute(
                'UPDATE users SET tarot_used_questions=%s WHERE email=%s', (1, email))
            remaining_question_count = 0

            # SEND MAIL TO ADMIN
            msg = Message('Pregunta TAROT para La Flor Blanca!', sender='admin@thechicnoir.com',
                          recipients=['alex.landin@hotmail.com', 'admin@thechicnoir.com'])
            msg.body = f"Email: {email}\nPlan: {current_plan}\nQuestion: {question}\nInfo: {info}"
            mail.send(msg)
            current_app.logger.info(" Question sent to admin")

            return jsonify({'message': f'Tu pregunta ha sido enviada, gracias.    Preguntas restantes este mes {remaining_question_count}', 'count': remaining_question_count}), 200
        except Exception as e:
            current_app.logger.error(
                "An error occurred while processing the form submission: %s", str(e))
            return jsonify({'message': 'Ha ocurrido un error y tu pregunta no se ha podido enviar.', 'error': str(e)}), 500

    else:

        return redirect(url_for('answers.index'))


@bp.route('/questions/live', methods=['POST', 'GET'])
@login_required
@required_spirit_plan
def live_query():
    email = session.get('email')
    question = request.form.get('questionLive')
    username = session.get('username')
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT live_used_questions FROM users WHERE username=%s', (username,))
    used_questions = cursor.fetchone()

    if request.method == 'POST':

        cursor.execute(
            "SELECT subscription_plan,live_used_questions from users WHERE email = %s", (email,))
        results = cursor.fetchone()

        if results[0] is None or results[0] == 'price_1Nk5XdAEZk4zaxmwo8ZFYOEv':
            current_plan = "PERSONALIDAD"
        elif results[0] == 'price_1Nk5YMAEZk4zaxmws0AhQfIs':
            current_plan = "ALMA"
        elif results[0] == "price_1Nk5YdAEZk4zaxmwEqqHWSS2":
            current_plan = "ESPÍRITU"

        try:
            live_query_save(question, current_plan, email)
            cursor.execute(
                'UPDATE users SET live_used_questions=%s WHERE email=%s', (1, email))
            remaining_question_count = 0

            msg = Message('Pregunta LIVE para La Flor Blanca!', sender='admin@thechicnoir.com',
                          recipients=['alex.landin@hotmail.com', 'admin@thechicnoir.com'])
            msg.body = f"Email: {email}\nPlan: {current_plan}\nQuestion: {question}"
            mail.send(msg)
            current_app.logger.info(" Question sent to admin")

            return jsonify({'message': f'Tu pregunta ha sido enviada, gracias.    Preguntas restantes este mes {remaining_question_count}', 'count': remaining_question_count}), 200

        except Exception as e:

            current_app.logger.error(
                "An error occurred while processing the form submission: %s", str(e))
            return jsonify({'message': 'Ha ocurrido un error y tu pregunta no se ha podido enviar.', 'error': str(e)}), 500

    else:
        cursor.execute('SELECT *  FROM live_sessions')
        live_sessions = cursor.fetchall()

        remaining_question_count = 1 - int(used_questions[0])

        return render_template('questions/live.html', live_sessions=live_sessions, username=username, remaining_question_count=remaining_question_count)


@bp.route('/add/live_session', methods=['POST'])
@login_required
@is_admin
def add_live_session():
    link = request.form.get('link')
    title = request.form.get('title')
    description = request.form.get('description')
    extra_info = request.form.get('extra_info')

    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO live_sessions(link,title,description,extra_info)VALUES(%s,%s,%s,%s) ',
                   (link, title, description, extra_info))
    message = " Sesión guardada con éxito"
    flash((message, 'info'))

    return redirect(url_for('questions.live_query'))


@bp.route('/delete/live_session', methods=['POST'])
@login_required
@is_admin
def delete_live_session():
    link = request.form.get('link_id')

    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM live_sessions WHERE id=%s', (link,))
    message = " Sesión eliminada con éxito"
    flash((message, 'primary'))

    return redirect(url_for('questions.live_query'))
