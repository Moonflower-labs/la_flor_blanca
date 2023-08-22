from flor_blanca.admin import bp
from flor_blanca.auth import login_required
from flor_blanca.postDb import save_link, get_db
from flask import render_template,session,request,redirect,url_for,flash


@bp.route('/admin')
@login_required
def index():
    if session['role'] is not None:
        if session['role'] != 'admin':
            return redirect(url_for('auth.denied'))
        else:
            return render_template('admin/index.html')
        

@bp.route('/links/show')
def show_links():
    db = get_db()
    cursor = db.cursor()
    
    try:
                        
        cursor.execute("SELECT * FROM videos ORDER BY id DESC  ")
        results = cursor.fetchall()
       
        return render_template('admin/videos.html', results=results)
              
        
    except:
            pass
    
    return render_template('admin/videos.html')



@bp.route('/links/delete',methods=['POST'])
def delete_link():
      db = get_db()
      cursor = db.cursor()
      if request.method == 'POST':
        link_id = int(request.form['id'])

        try:
          cursor.execute("DELETE FROM videos WHERE id=%s ",(link_id,))
          db.commit()

       
          return redirect(url_for('admin.show_links')) 
              
        except:
            pass
    
      return render_template('admin/videos.html')



@bp.route('/uploads', methods=['GET','POST'])
@login_required
def upload():
    username = session.get('username')
    name = 'VIDEO'
    action = url_for('admin.upload')
    
    if request.method == 'POST':
        link = request.form.get('link')
        error = None
        if not link:
            error = "Debes de inserta un link válido"

        if error is not None:
            flash(error)  
        else:
            try:
                print(link)
                save_link(link)
                info = "link guardado con éxito!"
                flash(info)
                return redirect(url_for('admin.upload'))
            except:
                pass



    return render_template('admin/uploads.html', username=username,name=name,action=action)



# podcasts

@bp.route('/podcasts', methods=['GET','POST'])
@login_required
def podcast():
    username = session.get('username')
    name = 'PODCAST'
    action = url_for('admin.podcast')
   
    if request.method == 'POST':
        link = request.form.get('link')  
        error = None
        if not link:
            error = "Debes de inserta un link válido"

        if error is not None:
            flash(error)  
        else:
            try:
                  
                print(link)
                db = get_db()
                cursor = db.cursor()
                cursor.execute('INSERT INTO podcasts (link) VALUES (%s)',(link,))
                
                info = "link guardado con éxito!"
                flash(info)
                return redirect(url_for('admin.add_podcast',name=name))
            except:
                pass
   
    return render_template('admin/uploads.html', username=username,name=name,action=action)

@bp.route('/delete_podcast', methods=['POST'])
@login_required
def delete_podcast():
        

    if request.method == 'POST':
        link_id = int(request.form['id'])
        
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("DELETE FROM podcasts WHERE id=%s ",(link_id,))
            db.commit()
        
            info = "link borrado con éxito!"
            flash(info)

        except:
            pass
        return redirect(url_for('admin.view_podcasts'))



@bp.route('/view_podcasts')
@login_required
def view_podcasts():
     username = session.get('username')
     db = get_db()
     cursor = db.cursor()
     cursor.execute('SELECT * FROM podcasts ORDER BY id DESC')
     podcasts = cursor.fetchall()
    
     return render_template('admin/podcasts.html', podcasts=podcasts, username=username)

# Users
@bp.route('/view_users')
@login_required
def view_users():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users ')
    users = cursor.fetchall()
    return render_template('admin/users.html', users=users)

# Preguntas
    
@bp.route('/view_questions')
@login_required
def view_questions():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM questions')
    questions = cursor.fetchall()
    return render_template('admin/questions.html', questions=questions)

#   Borrar por ID

@bp.route('/question/delete',methods=['POST'])
def delete_question():
      db = get_db()
      cursor = db.cursor()
      if request.method == 'POST':
        question_id = int(request.form['id'])

        try:
          cursor.execute("DELETE FROM questions WHERE id=%s ",(question_id,))
          db.commit()
          

       
          return redirect(url_for('admin.view_questions')) 
              
        except:
            pass
    
      return redirect(url_for('admin.view_questions')) 

#  Borrar todas
@bp.route('/question/wipe',methods=['POST'])
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