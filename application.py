from flask import Flask, render_template, request
import logging
# import azure.functions as func
import config_cosmos
import pydocumentdb.document_client as document_client
import config_cosmos
app = Flask(__name__)

@app.route("/")
def homepage():
    # app = "<html><body><h1>Hello Xitang</h1><div>This is test!</div></body></html>"
    # return app
#    dict = {'phy':50,'che':60,'maths':70}
   return render_template('index.html')

@app.route("/user_data", methods=['POST'])
def user_data():
    data = request.form
    print("----sending user data---")
    print(data)
    get_data_from_cosmodb()
    return render_template('prediction.html', data=data)

def get_data_from_cosmodb():
    client = document_client.DocumentClient(config_cosmos.COSMOSDB_HOST, {'masterKey': config_cosmos.COSMOSDB_KEY})
    db_id = 'millksdata'
    db_query = "select * from r where r.id = '{0}'".format(db_id)
    db = list(client.QueryDatabases(db_query))[0]
    db_link = db['_self']

    coll_id = 'cowproduction'
    coll_query = "select * from r where r.id = '{0}'".format(coll_id)
    coll = list(client.QueryCollections(db_link, coll_query))[0]
    coll_link = coll['_self']

    # docs = client.ReadDocuments(coll_link)
    # print(list(docs))
    query = { 'query': 'SELECT * FROM server s WHERE s.AnimalID = 5' }    
    docs = client.QueryDocuments(coll_link, query)
    print(list(docs))

if __name__ == '__main__':
   app.run(debug = True)
