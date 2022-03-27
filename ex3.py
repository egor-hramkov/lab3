from flask import Flask, url_for, render_template, request, send_from_directory, g, abort
from werkzeug.utils import redirect, secure_filename
from werkzeug.security import generate_password_hash
import requests
import sqlite3
import os
import uuid

from FDataBase import FDataBase


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

UPLOAD_FOLDER = 'static/photos'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
DATABASE = 'flsite.db'
DEBUG = True
SECRET_KEY = '&8\xa2|\x11\x0f\xcf\xe8\xc2\xa6\x85"\xfd~\x0c#\x06{>T\xb7\xe9\xd8\xc9'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    db=connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()

@app.route('/')
def index():
    return redirect(url_for('register'))

@app.route('/registration/', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        create_db()
        file = request.files['photo']
        if file and allowed_file(file.filename):
            s = uuid.uuid4()
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(s) + '.jpg'))
            filename2db = str(s) + '.jpg'

            db = get_db()
            dbase = FDataBase(db)
            dbase.adduser(request.form.get('named'), request.form.get('surname'), request.form.get('email'),
                          request.form.get('age'),
                          request.form.get('work'), request.form.get('position'),
                          generate_password_hash(request.form.get('password')), filename2db)
            return redirect(url_for('users')+'?page=0')


@app.route('/uploads/<name>')
def download_file(name):
    #return send_from_directory(app.config["UPLOAD_FOLDER"], name)
    redirect(url_for('users')+'?page=1')

@app.route('/users/')
def users():
    db = get_db()
    dbase = FDataBase(db)

    curr_page = int(request.args.get('page'))
    pgcount = 1
    remainder = 0
    all_users = dbase.getAllUsers()
    pgcount = len(all_users) // 4 + 1
    if curr_page >= pgcount:
        abort(404)
    if pgcount % 4 > 0:
        remainder = len(all_users) % 4
    class pgstore:
        value = pgcount
    match curr_page:
        case 0:
            a = all_users[:4]
        case pgstore.value:
            a = all_users[pgcount - 1:remainder]
        case _:
            a = all_users[curr_page * 4:curr_page * 4 + 4]
    return render_template('users.html', users=a, curr_page=curr_page, pagecount=pgcount)


@app.errorhandler(404)
@app.errorhandler(403)
@app.errorhandler(410)
@app.errorhandler(500)
def page_not_found(e):
    return render_template('404.html')

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
