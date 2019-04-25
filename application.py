from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    app = "<html><body><h1>Hello Xitang</h1><div>This is test!</div></body></html>"
    return app