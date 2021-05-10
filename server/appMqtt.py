import threading
import logging
from flask import *
import paho.mqtt.client as mqtt
import sqlite3

# Don't forget to change the variables for the MQTT broker!
mqtt_username = "iocProject"
mqtt_password = "rahimTT"
mqtt_topic_d = "display"
mqtt_topic_s = "sensor"
mqtt_broker_ip = "127.0.0.1"
client = mqtt.Client()
# Set the username and password for the MQTT client
client.username_pw_set(mqtt_username, mqtt_password)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        #TODO change :memory: to database.db and check if table exist
        db = g._database = sqlite3.connect(":memory:") 
        db.getMeta
    return db

    #TODO see how to use this 
# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()


def insert_val(db, val):
    with db:
        db.execute("INSERT INTO sensor (value) VALUES (?) ", (val,))

# These functions handle what happens when the MQTT client connects
# to the broker, and what happens then the topic receives a message
def on_connect(client, userdata, flags, rc):
    # rc is the error code returned when connecting to the broker
    print("Connected!"+ str(rc))
    
    # Once the client has connected to the broker, subscribe to the topic
    client.subscribe(mqtt_topic_s)
    
def on_message(client, userdata, msg):
    # This function is called everytime the topic is published to.
    # If you want to check each message, and do something depending on
    # the content, the code to do this should be run in this function
    
    print("Topic: "+ msg.topic + "\nMessage: " + str(msg.payload))


    
    # The message itself is stored in the msg variable
    # and details about who sent it are stored in userdata

# Here, we are telling the client which functions are to be run
# on connecting, and on receiving a message
client.on_connect = on_connect
client.on_message = on_message

# Once everything has been set up, we can (finally) connect to the broker
# 1883 is the listener port that the MQTT broker is using
client.connect(mqtt_broker_ip, 1883)
client.loop_start()



app = Flask(__name__)

messages = []

@app.route("/")
def index():
    name = request.args.get("name", "world")
    get_db()
    cursor = get_db().cursor()
    cursor.execute("CREATE TABLE sensor (id INTEGER PRIMARY KEY AUTOINCREMENT, value INTEGER)")  

    return render_template("index.html")

@app.route("/display", methods=["POST"])
def display():

    message = request.form.get("message")
    if not message:
        return "failure"
    client.publish(mqtt_topic_d, message)
    if message == "close":
        client.loop_stop(force=False)
        get_db().close()
        exit()
    messages.append(f"{message} at time")
    return render_template("display.html", messages = messages)

if __name__ == '__main__':
    # Create a server listening for external connections on the default
    # port 5000.  Enable debug mode for better error messages and live
    # reloading of the server on changes.  Also make the server threaded
    # so multiple connections can be processed at once (very important
    # for using server sent events).
    app.run(host='0.0.0.0', debug=True, threaded=True)
