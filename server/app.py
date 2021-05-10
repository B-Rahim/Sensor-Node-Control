from flask import Flask, render_template, request

app = Flask(__name__)

messages = []

@app.route("/")
def index():
    name = request.args.get("name", "world")
    return render_template("index.html")

@app.route("/display", methods=["POST"])
def display():

    message = request.form.get("message")
    if not message:
        return "failure"
    messages.append(f"{message} at time")
    return render_template("display.html", messages = messages)
    
if __name__ == '__main__':
    # Create a server listening for external connections on the default
    # port 5000.  Enable debug mode for better error messages and live
    # reloading of the server on changes.  Also make the server threaded
    # so multiple connections can be processed at once (very important
    # for using server sent events).
    app.run(host='0.0.0.0', debug=True, threaded=True)
