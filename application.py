from flask import Flask, render_template, request
import logging
# import azure.functions as func
import config_cosmos
import model
import pydocumentdb.document_client as document_client
import config_cosmos
import os
import urllib.request
import json
COW_FOLDER = os.path.join('static', 'cow')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = COW_FOLDER

client = document_client.DocumentClient(config_cosmos.COSMOSDB_HOST, {'masterKey': config_cosmos.COSMOSDB_KEY})
db_id = 'millksdata'
db_query = "select * from r where r.id = '{0}'".format(db_id)
db = list(client.QueryDatabases(db_query))[0]
db_link = db['_self']

#get cow production data from cosmoDB
coll_id = 'cowproduction'
coll_query = "select * from r where r.id = '{0}'".format(coll_id)
coll = list(client.QueryCollections(db_link, coll_query))[0]
coll_link = coll['_self']

#post machine learning model result into cosmoDB
# coll_post_id = ''
# coll_post_query = "select * from r where r.id = '{0}'".format(coll_post_id)
# coll_post = list(client.QueryCollections(db_link, coll_post_query))[0]
# coll_post_link = coll_post['_self']
# cow_data = None

@app.route("/")
def homepage():
    hello_cow = os.path.join(app.config['UPLOAD_FOLDER'], 'hello_cow.png')
    return render_template('index.html', cow_hello_image = hello_cow)

@app.route("/choices_data", methods=['POST'])
def choices_data():
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'cute_cow.png')
    data = request.form
    cowId = int(data.get('cowid'))
    print(data)
    return render_template('choices.html', cow_image = full_filename, cow_id = cowId)

@app.route("/current_data/<cowId>")
def current_data(cowId):
    cow_data = get_data_from_cosmodb(cowId)
    print(type(cow_data))
    return render_template('current.html', cow_data = cow_data)

@app.route("/prediction/<cowId>")
def prediction(cowId):
    # data = request.form
    print("----sending user data---")
    print(cowId)
    connection = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/weather?zip=14850,us&APPID=3f256d2258cc6fdb387c627fca21ec1e')
    res = connection.read().decode('utf-8')
    data = json.loads(res)
    print(data["main"]["temp"])
    print(data["main"]["humidity"])
    return render_template('prediction.html', cowId = cowId)

@app.route("/preresult/<cowId>", methods=['POST'])
def preresult(cowId):
    print("----preresult-----")
    print(cowId)
    data = request.form
    result = model.test()
    return render_template('preresult.html', data = result)

def get_data_from_cosmodb(cowId):
    # docs = client.ReadDocuments(coll_link)
    # print(list(docs))
    query = { 'query': 'SELECT * FROM server s WHERE s.AnimalID = {0}'.format(cowId) }    
    docs = client.QueryDocuments(coll_link, query)
    print(list(docs))
    return list(docs)

def post_data_to_cosmodb(cowId, data):
    query = { 'query': ''}

if __name__ == '__main__':
   app.run(debug = True)
