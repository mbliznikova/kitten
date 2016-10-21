from flask import Flask
from flask import request
app = Flask(__name__)


@app.route('/', methods=['HEAD'])
def health_check():
    return ''

@app.route("/")
def hello():
    return "Server is running on %s" % request.environ['SERVER_PORT']


@app.route('/hello/<name>')
def hello_name(name):
    #import ipdb; ipdb.set_trace()
    return 'Hello, %s' % name

if __name__ == "__main__":
    app.run()
