from flor_blanca.answers import bp
from flor_blanca.auth import login_required,required_spirit_plan,required_soul_plan
from flask import render_template,session,request,flash,redirect,url_for,abort
from flor_blanca.postDb import get_links, get_db,get_videos

@bp.route('/answers', methods=['GET'])
@login_required
@required_soul_plan
def index():
    links = get_links()
    username = session.get('username')
   
     
    return render_template('answers/tarot.html', username=username, links=links)


@bp.route('/basic')
@login_required
def basic():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT * FROM posts ORDER BY created DESC'
        
    )
    posts = cursor.fetchall()

    return render_template('answers/basic.html', posts=posts)


@bp.route('/medium')
@required_soul_plan
def soul_view():
    links = get_links()
    username = session.get('username')
    return render_template('answers/soul.html',links=links,username=username)


@bp.route('/premium')
@required_spirit_plan
def spirit_view():
    links = get_videos()
    username = session.get('username')
    return render_template('answers/spirit.html',links=links,username=username)

@bp.route('/coming-soon')
@required_spirit_plan
def soon_view():
    return render_template('coming-soon.html')

@bp.route('/create-post', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        author_id = session.get('id')
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO posts (title, body, author_id)'
                ' VALUES (%s, %s, %s)',
                (title, body, author_id)
            )
            db.commit()
            return redirect(url_for('answers.basic'))

    return render_template('answers/create.html')

def get_post(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT * FROM posts WHERE id = %s',(id,)
    )
    post = cursor.fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")
  
    return post



@bp.route('/<int:id>/delete')
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM posts WHERE id = %s', (id,))
   
    return redirect(url_for('answers.basic'))




# @bp.route('/<int:id>/update', methods=('GET', 'POST'))
# @login_required
# def update(id):
#     post = get_post(id)   
#     if request.method == 'POST':
#         title = request.form['title']
#         body = request.form['body']
#         error = None

#         if not title:
#             error = 'Title is required.'

#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 'UPDATE posts SET title = ?, body = ?'
#                 ' WHERE id = ?',
#                 (title, body, id)
#             )
#             db.commit()
#             return redirect(url_for('blog.index'))
    
#     return render_template('blog/update.html', post=post)

