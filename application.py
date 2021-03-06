from flask import Flask, render_template, request, Response
import logging
# import azure.functions as func
import config_cosmos
import pydocumentdb.document_client as document_client
import config_cosmos
import os
import urllib.request
import json
import time
import datetime
import sys
# sys.path.append('/models')
sys.path.insert(0,'models')
import model_prediction
os.system('pip install -U scikit-learn scipy matplotlib')

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

#post real-time environmental data into cosmoDB
coll_post_id = 'environdata'
coll_post_query = "select * from r where r.id = '{0}'".format(coll_post_id)
coll_post = list(client.QueryCollections(db_link, coll_post_query))[0]
coll_post_link = coll_post['_self']
# cow_data = None

MODEL_FOLDER = str(os.getcwd()) + "/models"
with open(MODEL_FOLDER + "/model_meta.txt", 'rb') as meta_file:
        data_limit = json.load(meta_file)['data_limit']
with open(MODEL_FOLDER + "/model_stats.txt", 'rb') as stats_file:
        data_stats = json.load(stats_file)

# time_end = False

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
    #if (len(get_data_from_cosmodb(cowId)) != 0):
    if str(cowId) in data_stats or len(get_data_from_cosmodb(cowId)) != 0:
        print(data)
        return render_template('choices.html', cow_image = full_filename, cow_id = cowId)
    else:
        return render_template('check.html', sad_cow_image = '/static/cow/sad_cow.png', error = "No cow in our database catches given cow id")

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
    if (str(cowId) not in data_stats) or (data_stats[str(cowId)] < data_limit):
        return render_template('check.html', sad_cow_image = '/static/cow/sad_cow.png', error = "We do not have enough data to produce a model for this cow")
    else:
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
    # print(cowId)
    connection = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/weather?zip=14850,us&APPID=3f256d2258cc6fdb387c627fca21ec1e')
    res = connection.read().decode('utf-8')
    data = json.loads(res)
    #temp connvert from Kevin to Celsius
    temp = data["main"]["temp"]
    temp -= 273.15
    humidity = data["main"]["humidity"]
    #get current date time
    date_time = str(datetime.datetime.now()).split(' ')
    #format current time
    time = date_time[1].split('.')[0]
    #format current date
    date = date_time[0].split('-')
    date_format = "/".join([date[1], date[2], date[0]])
    data = {'deviceId': '', 'barnId':'Real Time', 'date': date_format, 'time': time , 'humidity': humidity, 'temp': temp}
    post_data_to_cosmodb(cowId, data)
    result = ml_model_result(cowId, temp, humidity)
    print(result)
    return render_template('preresult.html', data = result)

#progress bar
@app.route('/progress')
def progress():
    def generate():
        x = 0
        while x <= 100:
            yield "data:" + str(x) + "\n\n"
            x = x + 10
            time.sleep(0.5)
        # time_end = True
    return Response(generate(), mimetype='text/event-stream')

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
        result = { 'Fat(%)': round(pred_result[0], 2), 'Protein(%)': round(pred_result[1], 2), 'Lactose(%)': round(pred_result[2],2)}
    return result

def post_data_to_cosmodb(cowId, data):
    document = client.CreateDocument(coll_post_link, data)
    print("succesfully post")
    print(list(document))
    return list(document)

if __name__ == '__main__':
   app.run(debug = True)
