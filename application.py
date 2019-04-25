from flask import Flask, render_template, request
import config_cosmos
import pydocumentdb.document_client as document_client
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
    return render_template('prediction.html', data=data)
if __name__ == '__main__':
   app.run(debug = True)