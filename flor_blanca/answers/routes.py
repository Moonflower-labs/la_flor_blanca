from flor_blanca.answers import bp
from flor_blanca.auth import login_required,required_spirit_plan,required_soul_plan,required_basic,is_admin
from flask import render_template,session,request,flash,redirect,url_for,abort,current_app
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
@required_basic
def basic():
    username = session.get('username')
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'SELECT * FROM posts ORDER BY created DESC'
        
    )
    posts = cursor.fetchall()

    cursor.execute('SELECT SUM(rating),count(rating),post_id FROM post_rating GROUP BY post_id;')
    results = cursor.fetchall()
    scores=[]
    for result in results:
        scoreTotal = result[0]
        scoreCount = result[1]
        scorePost = result[2]
       
        result={"scoreTotal":scoreTotal,"scoreCount":scoreCount,"scorePost":scorePost}
        scores.append(result)
   


    return render_template('answers/basic.html', posts=posts,scores=scores,username=username)


@bp.route('/rating', methods=['POST'])
def rating():
    if request.method == 'POST':
        rating = request.form['result']
        print(rating)
        username = session.get('username')
        post_id = request.args.get('post_id')

        db = get_db()
        cursor = db.cursor()
        if rating and username:
              cursor.execute('INSERT INTO post_rating(rating,username,post_id) VALUES (%s,%s,%s)',(rating,username,post_id))
              current_app.logger.info(" Rating saved successfully.")



        return   redirect(url_for('answers.basic'))


@bp.route('/medium')
@login_required
@required_soul_plan
def soul_view():
    links = get_links()
    username = session.get('username')
    return render_template('answers/soul.html',links=links,username=username)


@bp.route('/premium')
@login_required
@required_spirit_plan
def spirit_view():
    links = get_videos()
    username = session.get('username')
    return render_template('answers/spirit.html',links=links,username=username)



@bp.route('/coming-soon')
def soon_view():
    return render_template('coming-soon.html')

@bp.route('/create-post', methods=('GET', 'POST'))
@login_required
@is_admin
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
        'SELECT title,body FROM posts WHERE id = %s',(id,)
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




@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
@is_admin
def update(id):
    post = get_post(id)   
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                'UPDATE posts SET title = %s, body = %s'
                ' WHERE id = %s',
                (title, body, id)
            )

            return redirect(url_for('answers.basic'))
    
    return render_template('answers/update.html', post=post)

