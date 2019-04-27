from flask import Flask, render_template, request
import logging
# import azure.functions as func
import config_cosmos
import pydocumentdb.document_client as document_client
import config_cosmos
import os
COW_FOLDER = os.path.join('static', 'cow')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = COW_FOLDER

client = document_client.DocumentClient(config_cosmos.COSMOSDB_HOST, {'masterKey': config_cosmos.COSMOSDB_KEY})
db_id = 'millksdata'
db_query = "select * from r where r.id = '{0}'".format(db_id)
db = list(client.QueryDatabases(db_query))[0]
db_link = db['_self']

coll_id = 'cowproduction'
coll_query = "select * from r where r.id = '{0}'".format(coll_id)
coll = list(client.QueryCollections(db_link, coll_query))[0]
coll_link = coll['_self']
cow_data = None

@app.route("/")
def homepage():
    # app = "<html><body><h1>Hello Xitang</h1><div>This is test!</div></body></html>"
    # return app
#    dict = {'phy':50,'che':60,'maths':70}
    hello_cow = os.path.join(app.config['UPLOAD_FOLDER'], 'hello_cow.png')
    return render_template('index.html', cow_hello_image = hello_cow)

@app.route("/user_data", methods=['POST'])
def user_data():
    data = request.form
    print("----sending user data---")
    print(data)
    # get_data_from_cosmodb()
    return render_template('prediction.html', data=data)

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
    

def get_data_from_cosmodb(cowId):
    # docs = client.ReadDocuments(coll_link)
    # print(list(docs))
    query = { 'query': 'SELECT * FROM server s WHERE s.AnimalID = {0}'.format(cowId) }    
    docs = client.QueryDocuments(coll_link, query)
    print(list(docs))
    return list(docs)

if __name__ == '__main__':
   app.run(debug = True)
