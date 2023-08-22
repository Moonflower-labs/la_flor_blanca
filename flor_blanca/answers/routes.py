from flor_blanca.answers import bp
from flor_blanca.auth import login_required
from flask import render_template,session,request
from flor_blanca.postDb import get_links

@bp.route('/answers', methods=['GET'])
@login_required
def index():
    links = get_links()
    username = session.get('username')
   
    return render_template('answers/index.html', username=username, links=links)


@bp.route('/basic')
@login_required
def basic():


    return render_template('answers/basic.html')

@bp.route('/coming-soon')
def soon_view():
    return render_template('coming-soon.html')