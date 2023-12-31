from flor_blanca.admin import bp
from flor_blanca.auth import login_required, is_admin
from flor_blanca.postDb import save_link, get_db
from flask import render_template, session, request, redirect, url_for, flash


@bp.route('/admin')
@login_required
@is_admin
def index():
    if session['role'] is not None:
        if session['role'] != 'admin':
            return redirect(url_for('auth.denied'))
        else:
            username = session.get('username')

            return render_template('admin/index.html', username=username)


@bp.route('/links/show')
@login_required
@is_admin
def show_links():
    db = get_db()
    cursor = db.cursor()
    username = session.get('username')

    cursor.execute("SELECT * FROM videos_soul ORDER BY id DESC  ")
    results = cursor.fetchall()

    return render_template('admin/soul.html', results=results, username=username)


@bp.route('/links/delete', methods=['POST'])
@login_required
@is_admin
def delete_link():
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        link_id = int(request.form['id'])

        try:
            cursor.execute("DELETE FROM videos_soul WHERE id=%s ", (link_id,))
            db.commit()

            return redirect(url_for('admin.show_links'))

        except:
            pass

    return render_template('admin/soul.html')


@bp.route('/uploads', methods=['GET', 'POST'])
@login_required
@is_admin
def upload():
    username = session.get('username')
    name = 'VIDEO ALMA'
    action = url_for('admin.upload')

    if request.method == 'POST':
        link = request.form.get('link')
        title = request.form.get('title')
        comment = request.form.get('comment')
        error = None
        if not link:
            error = "Debes de inserta un link válido"

        if error is not None:
            flash((error, 'danger'))
        else:
            try:

                save_link(link, title, comment)
                info = "link guardado con éxito!"
                flash((info, 'success'))
                return redirect(url_for('admin.upload'))
            except:
                pass

    return render_template('admin/uploads.html', username=username, name=name, action=action)


# edit video link
@bp.route('/<int:id>/update/video/soul', methods=['GET', 'POST'])
@login_required
@is_admin
def update_video_soul(id):
    username = session.get('username')
    name = 'Alma'
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT link,title,comment FROM videos_soul WHERE id=%s', (id,))
    video = cursor.fetchone()
    if request.method == 'POST':
        link = request.form['link']
        title = request.form['title']
        comment = request.form['comment']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash((error, 'danger'))
        else:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                'UPDATE videos_soul SET link=%s,title =%s,comment=%s '
                ' WHERE id = %s',
                (link, title, comment, id)
            )
            info = "link editado con éxito!"
            flash(info, 'success')
            return redirect(url_for('admin.show_links'))

    return render_template('admin/updateLink.html', video=video, name=name, username=username)

# SPIRIT


@bp.route('/videos/spirit', methods=['GET', 'POST'])
@login_required
@is_admin
def videos_spirit():
    username = session.get('username')
    name = 'VIDEO ESPÍRITU'
    action = url_for('admin.videos_spirit')

    if request.method == 'POST':
        link = request.form.get('link')
        title = request.form.get('title')
        comment = request.form.get('comment')
        error = None
        if not link:
            error = "Debes de inserta un link válido"

        if error is not None:
            flash((error, 'danger'))
        else:
            try:

                print(link)
                db = get_db()
                cursor = db.cursor()
                cursor.execute(
                    'INSERT INTO videos_spirit (link,title,comment) VALUES (%s,%s, %s)', (link, title, comment))

                info = "link guardado con éxito!"
                flash(info, 'success')
                return redirect(url_for('admin.add_podcast', name=name))
            except:
                pass

    return render_template('admin/uploads.html', username=username, name=name, action=action)


@bp.route('/videos/spirit/delete', methods=['POST'])
@login_required
@is_admin
def delete_video_spirit():

    if request.method == 'POST':
        link_id = int(request.form['id'])

        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "DELETE FROM videos_spirit WHERE id=%s ", (link_id,))
            db.commit()

            info = "link borrado con éxito!"
            flash((info, 'success'))

        except:
            pass
        return redirect(url_for('admin.view_videos_spirit'))


@bp.route('/view/videos_spirit')
@login_required
@is_admin
def view_videos_spirit():
    username = session.get('username')
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM videos_spirit ORDER BY id DESC')
    videos = cursor.fetchall()

    return render_template('admin/spirit.html', videos=videos, username=username)

# edit video link


@bp.route('/<int:id>/update/video/spirit', methods=['GET', 'POST'])
@login_required
@is_admin
def update_video_spirit(id):
    username = session.get('username')
    name = 'Espíritu'
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT link,title,comment FROM videos_spirit WHERE id=%s', (id,))
    video = cursor.fetchone()
    if request.method == 'POST':
        link = request.form['link']
        title = request.form['title']
        comment = request.form['comment']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash((error, 'danger'))
        else:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                'UPDATE videos_spirit SET link=%s,title =%s,comment=%s '
                ' WHERE id = %s',
                (link, title, comment, id)
            )
            info = "link editado con éxito!"
            flash((info, 'success'))
            return redirect(url_for('admin.view_videos_spirit'))

    return render_template('admin/updateLink.html', video=video, name=name, username=username)

# Users


@bp.route('/view_users')
@login_required
@is_admin
def view_users():
    username = session.get('username')
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users ORDER BY id ASC')
    users = cursor.fetchall()
    return render_template('admin/users.html', users=users, username=username)

# Users by plan basic


@bp.route('/filtered_users/<key>')
@login_required
@is_admin
def filtered_users(key):
    username = session.get('username')
    subscription_plan = key
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id,username,email,customer_id,subscription_plan,subscription_status,used_questions,tarot_used_questions,live_used_questions FROM users WHERE subscription_plan=%s', (subscription_plan,))
    users = cursor.fetchall()

    return render_template('admin/filtered_users.html', users=users, username=username)


# Preguntas

@bp.route('/view_questions')
@login_required
@is_admin
def view_questions():
    username = session.get('username')
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT *, to_char(created, 'DD Mon YYYY, HH:MI:SS') AS formatted_date FROM questions ORDER BY id DESC;")
    questions = cursor.fetchall()
    return render_template('admin/questions.html', questions=questions, username=username)

#   Borrar por ID


@bp.route('/question/delete', methods=['POST'])
@login_required
@is_admin
def delete_question():
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        question_id = int(request.form['id'])

        try:
            cursor.execute(
                "DELETE FROM questions WHERE id=%s ", (question_id,))
            db.commit()

            return redirect(url_for('admin.view_questions'))

        except:
            pass

    return redirect(url_for('admin.view_questions'))

#  Borrar todas


@bp.route('/question/wipe', methods=['POST'])
@login_required
@is_admin
def wipe_questions():
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':

        try:
            cursor.execute("DELETE FROM questions WHERE id >= 1 ")
            db.commit()

            return redirect(url_for('admin.view_questions'))

        except:
            pass

    return redirect(url_for('admin.view_questions'))

#  Tarot


@bp.route('/view_tarot_questions')
@login_required
@is_admin
def view_tarot_questions():
    username = session.get('username')
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT *, to_char(created, 'DD Mon YYYY, HH:MI:SS') AS formatted_date FROM tarot;")
    questions = cursor.fetchall()
    return render_template('admin/tarot.html', questions=questions, username=username)


@bp.route('/question/tarot/delete', methods=['POST'])
@is_admin
def delete_tarot_question():
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        question_id = int(request.form['id'])

        try:
            cursor.execute("DELETE FROM tarot WHERE id=%s ", (question_id,))
            db.commit()
            flash(('Pregunta borrada con éxito.', 'success'))
            return redirect(url_for('admin.view_tarot_questions'))

        except:

            return str(e)

    return redirect(url_for('admin.view_tarot_questions'))


@bp.route('/question/live', methods=['POST', 'GET'])
@is_admin
def live_question():
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        question_id = int(request.form['id'])

        try:
            cursor.execute("DELETE FROM live WHERE id=%s ", (question_id,))
            db.commit()
            flash(('Pregunta borrada con éxito.', 'success'))
            return redirect(url_for('admin.live_question'))

        except Exception as e:

            return str(e)

    else:
        username = session.get('username')
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT *, to_char(created, 'DD Mon YYYY, HH:MI:SS') AS formatted_date FROM live;")
        questions = cursor.fetchall()

        return render_template('admin/live.html', questions=questions, username=username)
