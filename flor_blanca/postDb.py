
import psycopg2
import click
from flask import current_app, g
"""g is a special object that is unique for each request. 
It is used to store data that might be accessed by multiple functions during the request.
 The connection is stored and reused instead of creating a new connection if get_db is
   called a second time in the same request."""

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            current_app.config['DATABASE'],
        )
        g.db.autocommit = True

    return g.db



def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()



def init_db():
    db = get_db()
    cursor = db.cursor()

    with current_app.open_resource('schema.sql') as f:
        sql_code = f.read().decode('utf8')
        cursor.execute(sql_code)

    # db.commit()
    cursor.close()

       
       

@click.command('init-db') # defines a new command line command
def init_db_command():
    #  Clear the existing data and create new tables.
    init_db()
    click.echo('Initialized the database.')



def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def save_link(link):
     db = get_db()
     cursor = db.cursor()
     cursor.execute(  'INSERT INTO videos (link) VALUES (%s)',
                (link,))
  
     print('link saved')

def get_links():
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT link, created FROM videos ORDER BY created DESC LIMIT 20')
    results = cursor.fetchall() if cursor else []
    links = [{'link': row[0], 'created': row[1]} for row in results]

    if links:
        return links
    else:
        return []


def get_user_by_email(email):
    db = get_db()
    cursor = db.cursor()
    user = cursor.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    
    if user is None:
        return None
    
    return dict(user)

# Retrieve customer_id from stripe and save to db

def save_customer_id(customer_id, email):
        db = get_db()
        cursor = db.cursor()
        if customer_id is not None:

            cursor.execute('UPDATE users SET customer_id = %s WHERE email = %s', (customer_id, email))
            # db.commit()
            print(f"Customer ID {customer_id} has been saved ")
           
        
        else:
        # Handle the case where the customer_id is None
        # print a message or raise an exception
            print("Customer ID is None. Cannot save.")


def save_message(*args):
    db = get_db()
    cursor = db.cursor()
    # Convert the media list to a string
    media = ','.join(args[6])

    cursor.execute("""
        INSERT INTO questions (email, name, subject, question, gender, age_group, media_choice, country, city, subscribe)
        VALUES (%s, %s, %s, %s , %s, %s, %s, %s, %s, %s)
    """, (args[0], args[1], args[2], args[3], args[4], args[5], media, args[7], args[8], args[9]))
    
    # db.commit()
    print("Message correctly daved to questions table")

  

    # run 'flask --app flor_blanca init-db' to initialize db