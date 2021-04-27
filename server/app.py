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