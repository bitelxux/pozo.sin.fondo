#!/usr/bin/python3

import json
import pymysql as mysql
import pickle

from flask import abort
from flask import Flask
from flask import request

app = Flask(__name__)
db = None

def normalize_text(what):
    translations = {
        'km': 'kilómetros',
        'tv': 'televisión',
        'tengo': 'tienes'
    }

    for abrev, word in translations.items():
        what = what.replace(abrev, word)

    return what

def get_singular_and_plural(word):

    if word[-3:] == 'ces':
        plural = word
        singular = "%sz" % word[:-3]
    elif word[-2:] == 'es':
        singular = word[:-2]
        plural = word
    elif word[-1] in ['s']:
        singular = word[:-1]
        plural = word
    elif word[-1] == 'z':
        singular = word
        plural = "%sces" % word[:-1]
    elif word[-1] in ['n', 'r']:
        singular = word
        plural = "%ses" % word
    else:
        singular = word
        plural = "%ss" % word

    return singular, plural


class MySQLConnector():
    host='127.0.0.1'
    port=3306
    user=''
    password=''
    database=''

    cursor=None
    db=None

    def __init__(self, **kw):

        self.host = kw.get('host', '127.0.0.1')
        self.port = kw.get('host', 3306)
        self.user = kw.get('user')
        self.password = kw.get('password')
        self.database = kw.get('database')

    def execute(self, sql):
        self.db = mysql.connect(self.host, self.user, self.password, self.database)
        self.cursor = self.db.cursor(mysql.cursors.DictCursor)
        self.cursor.execute("USE %s" % self.database)
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        self.db.close()
        return rows

    def execute_and_commit(self, sql):
        self.db = mysql.connect(self.host, self.user, self.password, self.database)
        self.cursor = self.db.cursor(mysql.cursors.DictCursor)
        self.cursor.execute("USE %s" % self.database)
        self.cursor.execute(sql)
        self.db.commit()
        self.db.close()


@app.route("/")
def hello():
    return "Hello World!"

@app.route("/tables")
def tables():
    tables = db.execute("SHOW columns FROM memories")
    return json.dumps(tables)

@app.route("/new_memory", methods=['GET'])
def new_memory():
    memory = request.args.get('memory')
    memory = normalize_text(memory).replace('%20', ' ')
    user_id = request.args.get('user_id')
    person_id = request.args.get('person_id')
    category = request.args.get('type', 'generic')

    # If category is one word, we keep the singular
    if len(category.split()) == 1:
        catetory = get_singular_and_plural(category)[0]

    sql = "INSERT INTO memories VALUES (NULL, now(), '%s', '%s', '%s', '%s');" % (category, user_id, person_id, memory)
    db.execute_and_commit(sql)
    return memory

@app.route("/query_memory", methods=['GET'])
def query_memory():
    user_id = request.args.get('user_id')
    cosa = request.args.get('cosa').replace('%20', ' ')

    singular, plural = get_singular_and_plural(cosa)

    sql = f"SELECT * FROM memories WHERE what LIKE '%{singular}%' OR what LIKE '%{plural}%'"
    results = db.execute(sql)
    payload = {}
    for result in results:
        payload[result['id']] = {'what': result['what']}
    return payload

@app.route("/get_from_categories/<string:cat>", methods=['GET'])
def get_from_categories(cat):
    user_id = request.args.get('user_id')
    cat = cat.replace('%20', ' ')

    singular, plural = get_singular_and_plural(cat)

    sql = f"SELECT * FROM memories WHERE type LIKE '%{singular}%' OR type LIKE '%{plural}%'"
    results = db.execute(sql)
    payload = {}
    for result in results:
        payload[result['id']] = {'what': result['what']}
    return payload

@app.route("/delete_memory/<int:id>")
def delete_memory(id):
    user_id = request.args.get('user_id')
    sql = "DELETE FROM memories WHERE id = %d" % id
    db.execute_and_commit(sql)
    return "OK"

@app.route("/get_name/<string:hash>")
def get_name(hash):
    user_id = request.args.get('user_id')
    sql = "SELECT persons.name FROM persons WHERE persons.id = '%s'" % hash
    result = db.execute(sql)
    if result:
        return result[0]['name']
    else:
        return abort(404, description="Resource not found")

@app.route("/set_name/<string:hash>/<string:name>")
def set_name(hash, name):
    user_id = request.args.get('user_id')
    sql = """
          INSERT INTO persons
          VALUES ('%s', '%s')
          ON DUPLICATE KEY UPDATE name='%s'
          """ % (hash, name, name)
    db.execute_and_commit(sql)
    return "OK"

@app.route("/count")
def count():
    user_id = request.args.get('user_id')
    sql = "select count(*) as total from memories"
    result = db.execute(sql)[0]['total']
    return str(result)

if __name__ == "__main__":


    db = MySQLConnector(host="127.0.0.1",
                        port=3306,
                        user='root',
                        password='changeme',
                        database='alexa')

    app.run(host='0.0.0.0', port=9999, threaded=True)

