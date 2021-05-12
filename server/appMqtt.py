import threading
import logging
from time import time, ctime
from flask import Flask, render_template, request
import paho.mqtt.client as mqtt
import sqlite3


def get_db():
    #db = getattr(g, '_database', None)
    #if db is None:
    db = sqlite3.connect("database.db") 
    return db

cursor = get_db().cursor()
cursor.execute("""
	SELECT COUNT(name) FROM sqlite_master WHERE type='table' AND name='sensor'
	""")
if cursor.fetchone()[0]==0 :
    cursor.execute("""
        CREATE TABLE sensor (id INTEGER PRIMARY KEY AUTOINCREMENT, value INTEGER)
        """)


# Don't forget to change the variables for the MQTT broker!
mqtt_username = "iocProject"
mqtt_password = "rahimTT"
mqtt_topic_d = "/display"
mqtt_topic_s = "/sensor"
mqtt_broker_ip = "127.0.0.1"
client = mqtt.Client()
# Set the username and password for the MQTT client
client.username_pw_set(mqtt_username, mqtt_password)

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
   if msg.topic==mqtt_topic_s:  
       # print("Topic: "+ msg.topic + "\nMessage: \n" )
        val = int(msg.payload.decode("utf-8"))
        db = get_db()
        db.execute("INSERT INTO sensor (value) VALUES (?) ", (val,))
        db.commit()
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
    cursor = get_db().cursor()
    clear = request.args.get("clear")
    if clear == "Clear":
        cursor.execute("DROP TABLE sensor")
        cursor.execute("""
        CREATE TABLE sensor (id INTEGER PRIMARY KEY AUTOINCREMENT, value INTEGER)
        """)
    cursor.execute("SELECT * FROM sensor")
    values = [list(val) for val in cursor.fetchall()]
    return render_template("index.html", values= values)

@app.route("/display", methods=["POST"])
def display():

    message = request.form.get("message")
    if not message:
        return "failure"
    client.publish(mqtt_topic_d, message)
    if message == "close":
        client.loop_stop(force=False)
    t = ctime(time())
    messages.append(f"[{t[11:19]}] {message}")
    return render_template("display.html", messages = messages)

if __name__ == '__main__':
    # Create a server listening for external connections on the default
    # port 5000.  Enable debug mode for better error messages and live
    # reloading of the server on changes.  Also make the server threaded
    # so multiple connections can be processed at once (very important
    # for using server sent events).
    app.run(host='0.0.0.0', debug=True, threaded=True)
