#! /usr/bin/python
#all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
        abort, render_template, flash, make_response
from contextlib import closing
import os, datetime, random   
#configuration
DATABASE = './flaskr.db'
DEBUG = False
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

#create our little application :)
app = Flask(__name__)
app.config.from_object (__name__)


def connect_db():
    return sqlite3.connect (app.config['DATABASE'])
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()
@app.before_request
def before_request():
    g.db = connect_db()
@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route('/blogs')
@app.route ('/')
@app.route ('/index')
def show_entries():
    cur = g.db.execute('select title, text, id from entries order by id desc')
    entries = [dict(title = row[0], text = row[1], id = row[2]) for row in cur.fetchall()]
    return render_template ('show_entries.html', entries = entries)
@app.route('/add', methods = ['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort (401)
    g.db.execute ('insert into entries (title, text) values (?, ?)',
            [request.form['title'], request.form['content2']])
    g.db.commit()
    return redirect(url_for('show_entries'))

@app.route ('/admin', methods = ['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
            return render_template('login.html', error = error)
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
            return render_template('login.html', error = error)
        else:
            session['logged_in'] = True
            flash('You were logged in')
    return render_template('login.html', error = error)

@app.route('/author')
def about_me():
    return render_template('author.html')

@app.route('/logout')
def logout():
    session.pop ('logged_in', None)
    flash('You have logged out')
    return redirect(url_for('show_entries'))
@app.errorhandler(404)
def not_found():
    return render_template('404.html')
@app.route('/write')
def write_blog():
    return render_template('write.html')
@app.route('/blogs/<id>/', methods=['POST', 'GET'])
def detail(id):
    cmd =  'select title, text from entries where id=%s' % id
    cur = g.db.execute(cmd)
    res = cur.fetchone()
    if res:
        blog = dict(title = res[0], text = res[1], bid = id)
    else:
        return not_found()
    return render_template ('blog.html', entry = blog)
@app.route('/edit/<id>/', methods=['POST', 'GET'])
def edit(id):
    cmd =  'select title, text from entries where id=%s' % id
    cur = g.db.execute(cmd)
    res = cur.fetchone()
    if res:
        blog = dict(title = res[0], text = res[1], bid = id)
    else:
        return not_found()
    return render_template ('write.html', entry = blog)

@app.route('/delete/<id>/')
def delete(id):
    cmd =  'delete from entries where id=%s' % id
    g.db.execute(cmd)
    g.db.commit()
    return  redirect(url_for('show_entries'))
@app.route('/update', methods=['POST', 'GET'])
def update():
    cmd = "update entries set title='%s'"% request.form['title'] 
    cmd += ",text='%s'" % request.form['content0']
    cmd += " where id='%s'" %  request.form['id']
    g.db.execute (cmd)
    g.db.commit()
    return redirect(url_for('show_entries'))
def gen_rnd_filename():
    filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))

@app.route('/upload/', methods=['POST'])
def ckupload():
    """CKEditor file upload"""
    error = ''
    url = ''
    callback = request.args.get("CKEditorFuncNum")
    if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        rnd_name = '%s%s' % (gen_rnd_filename(), fext)
        filepath = os.path.join(app.static_folder, 'uploads', rnd_name)
    
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                error = 'ERROR_CREATE_DIR'
        elif not os.access(dirname, os.W_OK):
            error = 'ERROR_DIR_NOT_WRITEABLE'
        if not error:
            fileobj.save(filepath)
            url = url_for('static', filename='%s/%s' % ('upload', rnd_name))
    else:
        error = 'post error'
    res = """

<script type="text/javascript">
  window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
</script>

""" % (callback, url, error)
    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response
if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=8000)
