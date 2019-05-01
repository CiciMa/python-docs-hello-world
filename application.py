from flask import Flask, render_template, request
import logging
# import azure.functions as func
import config_cosmos
import pydocumentdb.document_client as document_client
import config_cosmos
import os
import urllib.request
import json

import sys
# sys.path.append('/models')
sys.path.insert(0,'models')
import model_prediction

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
    # print(sys.path.append('/models'))
    return render_template('index.html', cow_hello_image = hello_cow)

@app.route("/choices_data", methods=['POST'])
def choices_data():
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'cute_cow.png')
    data = request.form
    cowId = int(data.get('cowid'))
    #if cowId not in "model_stats".txt, direct to another template(html), and pass data ="not have a model"
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
    #check cowId's data less than 100 in "model_stats".txt, direct to another template(html), and pass data ="not have a cow"
    return render_template('prediction.html', cowId = cowId)

#prediciton result from user choice data
@app.route("/preresult_user/<cowId>", methods=['POST'])
def preresult_user(cowId):
    print("----preresult_user-----")
    print(cowId)    
    data = request.form
    temp = data.get('temp')
    humidity = data.get('humidity')
    print(temp, humidity)
    result = ml_model_result(cowId, float(temp), float(humidity))
    print(result)
    return render_template('preresult.html', data = result)

#prediciton result from real-time weather data
@app.route("/preresult_real/<cowId>")
def preresult_real(cowId):
    print("----preresult-----")
    print(cowId)
    connection = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/weather?zip=14850,us&APPID=3f256d2258cc6fdb387c627fca21ec1e')
    res = connection.read().decode('utf-8')
    data = json.loads(res)
    #temp connvert from Kevin to Celsius
    temp = data["main"]["temp"]
    temp -= 273.15
    humidity = data["main"]["humidity"]
    print(temp)
    print(humidity)
    result = ml_model_result(cowId, temp, humidity)
    print(result)
    return render_template('preresult.html', data = result)

def get_data_from_cosmodb(cowId):
    # docs = client.ReadDocuments(coll_link)
    # print(list(docs))
    query = { 'query': 'SELECT * FROM server s WHERE s.AnimalID = {0}'.format(cowId) }    
    docs = client.QueryDocuments(coll_link, query)
    print(list(docs))
    return list(docs)

def ml_model_result(cowId, temp, humidity):
    pred_result = model_prediction.GetModelAndPredict(cowId, temp, humidity)
    print(pred_result)
    if pred_result == None:
        result = {}
    else:
        #'yield', 'fat','protein','lactose'
        result = {'Yield(gr)' :round(pred_result[0], 2), "Fat(%)": round(pred_result[1], 2), 'Protein(%)': round(pred_result[2], 2), 'Lactose(%)': round(pred_result[3],2)}
    return result

def post_data_to_cosmodb(cowId, data):
    query = { 'query': ''}

if __name__ == '__main__':
   app.run(debug = True)
