from flor_blanca.answers import bp
from flor_blanca.auth import login_required
from flask import render_template,session,request
from flor_blanca.postDb import get_links, get_db

@bp.route('/answers', methods=['GET'])
@login_required
def index():
    links = get_links()
    username = session.get('username')
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT p.id, title, p.body, p.created, p.author_id, u.username '
        'FROM posts p '
        'JOIN users u ON p.author_id = u.id '
        # 'GROUP BY u.username '
        'ORDER BY p.created DESC'
    )
    posts = cursor.fetchall()
    username = session.get('username')
   
    return render_template('answers/tarot.html', username=username, links=links, posts=posts)


@bp.route('/basic')
@login_required
def basic():


    return render_template('answers/basic.html')

@bp.route('/coming-soon')
def soon_view():
    return render_template('coming-soon.html')





# from flask import(
#     Blueprint, flash, g, redirect, render_template,
#     request, url_for,session
# )
# from werkzeug.exceptions import abort

# from flor_blanca.auth import login_required
# from flor_blanca.db import get_db

# bp = Blueprint('blog', __name__)

# @bp.route('/posts')
# def posts():
#     posts = get_db().execute(
#         'SELECT p.id, title, p.body, p.created, p.author_id, u.username, r.body AS reply_body, r.created AS reply_created '
#         'FROM posts p '
#         'JOIN users u ON p.author_id = u.id '
#         'LEFT JOIN replies r ON r.post_id = p.id '  # Join the replies table on post_id
#         'GROUP BY p.id '
#         'ORDER BY p.created DESC, r.created DESC'
#     ).fetchall()
#     username = session.get('username')
    
#     return render_template('blog/posts.html', posts=posts, username=username)

# @bp.route('/create', methods=('GET', 'POST'))
# @login_required
# def create():
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
#                 'INSERT INTO posts (title, body, author_id)'
#                 ' VALUES (?, ?, ?)',
#                 (title, body, g.user['id'])
#             )
#             db.commit()
#             return redirect(url_for('blog.posts'))

#     return render_template('blog/create.html')

# def get_post(id, check_author=True):
#     post = get_db().execute(
#         'SELECT p.id, title, body, created, author_id, username'
#         ' FROM posts p JOIN users u ON p.author_id = u.id'
#         ' WHERE p.id = ?',
#         (id,)
#     ).fetchone()

#     if post is None:
#         abort(404, f"Post id {id} doesn't exist.")

#     if check_author and post['author_id'] != g.user['id']:
#         abort(403)

#     return post

# @bp.route('/reply',methods=('GET', 'POST'))
# @login_required
# def reply():
#     post_id = request.args.get('post_id',type=int)
#     db = get_db()
 
#     if request.method == 'POST':       
#         body = request.form['body']
#         error = None
#         if not body:
#            flash('Escribe una respuesta..')
#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 'INSERT INTO replies ( body, author_id, post_id)'
#                 ' VALUES (?, ?, ?)',
#                 ( body, g.user['id'],post_id)
#             )
#             db.commit()
#             return redirect(url_for('blog.posts'))
    
#     return render_template('blog/reply.html',post_id=post_id)

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


# @bp.route('/<int:id>/delete', methods=('POST',))
# @login_required
# def delete(id):
#     get_post(id)
#     db = get_db()
#     db.execute('DELETE FROM posts WHERE id = ?', (id,))
#     db.commit()
#     return redirect(url_for('blog.posts'))