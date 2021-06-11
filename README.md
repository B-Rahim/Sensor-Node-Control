# **Sensor node Control**

---
## Introduction
In this project  we implement a web application to control a sensor node based on ESP32_TTGO_OLED board. The web app displays the evolution of luminosity over time from the values ​​read from the photoresistor that is connected to the board and it enables the user to send messages that will be printed on the screen of the board.

To do this, we implement in the RPi (the gateway) an HTTP server using **Flask** framework. The data is transferred between the ESP32 board and the RPi through the MQTT protocol. For this we define two MQTT topics `/sensor`and `/display`  

Where:



|   topic  |publisher| subscriber|
|----------|:-------:|:---------:|
| /display | RPi     |ESP32      |
| /sensor  |ESP32    |RPi        |


A `SQLite` database has been implemented to store the data (sensor value) in memory.

To display the graph, we used a popular tool called  `Google Charts` 
## Configuration of the RPi
### 1- Installation and Configuration of Raspbian
* We download *Raspbian* from the [official site] (https: / /www.raspberrypi.org/software/operating-systems/#raspberry-pi-os-32-bit) and install it on the SD card. (On Windows you can use Rufus)

 *Optional - to check the integrity of the downloaded file:*

  `sha256sum <downloaded file> | grep <file hash> `

to activate wifi and automatically connect to the access point:
* We activate SSH communication:
In the drive **boot** we create an empty file called ssh (without extension)` touch ssh `

* In the **wpa_supplicant.conf** file we add
```
country = FR
add`ctrl_interface = DIR = / var / run / wpa_supplicant GROUP = netdev
update_config = 1
network = {
scan_ssid = 1
ssid =" your_wifi_ssid "
psk =" your_wifi_password "
}
```
* Insert the SD card into the Rpi and supply power. Then check that it is well connected to the access point and that the * SSH * connection is working.

### 2- Installation and test of the Mosquitto MQTT broker

* We install Mosquitto
```
sudo apt update
sudo apt install -y mosquitto mosquitto-clients
```
* We stop mosquitto to configure it:

    `sudo stop mosquitto`

* We create the file containing the password with the username:
  * short version: *

  `sudo mosquitto_passwd -c / etc / mosquitto / pwfile <mqtt_username>`

  And we are asked to enter the password and confirm it.

  * long version: *
 
  `` `  
  echo" <mqtt_username>: <mqtt_passwd> "> pwfile
  mosquitto_passwd -U pwfile
  sudo mv pwfile / etc / mosquitto /
  ` ``

* In the file `/ etc / mosquitto / mosquitto.conf` we add these two lines:

  ```
  log ...
  ---> allow_anonymos false
  ---> password_file / etc / mosquitto / pwfile
  include ...
  ```
* We restart the broker

  `mosquitto -c / etc / mosquitto / mosquitto.conf`

  or

  `sudo /etc/init.d/mosquitto restart`

To test if it has installed well we open two terminals where the first would be the **subscriber** and the second would be the **publisher**:

Terminal 1:

` mosquitto_sub - d -u <username> -P <password> -t <topic> `
 
 We can also replace \ <topic> by "#" to receive all thepublished messages

Terminal 2:

`mosquitto_pub -d -u <username> -P <password> -t <topic> -m <message>`

If everything works fine , the message sent should be displayed in terminal 1. Otherwise restart and retest.

## 3. Create virtual environment and install packages

1. Create virtual environment:
  * install python3 (for Flask):

    `sudo apt install python3`

  * install package manager pip:

    `sudo apt install pip`

  * create virtual environment named *ioc* then activate it (in the project folder):
```
    python3 -m venv ioc

    source ioc / bin / activate

    which python
```
 
 *(last command to check that is correctly installed)*

  * install flask, sqlite3 and paho-mqtt:

    `pip install flask`

    `pip install sqlite3`

    `pip install paho-mqtt`

## Configure the esp32-TTGO-OLED board

The libraries to install:
1. **Adafruit_BusIO**: a helper library to abstract away I2C & SPI transactions and registers.
2. **Adafruit-GFX-Library**: the core graphics library for all our displays, providing a common set of graphics primitives (points, lines, circles, etc.).
3. **Adafruit_SSD1306**: a library for the Monochrome OLEDs based on SSD1306 drivers.
4. **WiFiClientSecure**: The WiFiClientSecure class implements support for secure connections using TLS (SSL). It inherits from WiFiClient and thus implements a superset of that class' interface.

5. **PubSubClien**: This library provides a client for doing simple publish / subscribe messaging with a server that supports MQTT.

## To be changed in the app.py and node.ino code
* wifi: ssid and password
* mqtt: mqtt_broker (IP address of RPi), mqtt_username and mqtt_password

## Run server
`python3 app.py`
Or just `flask run`

*note: if the name of the file is not app.py we must:
`export FLASK_APP = <name>.py`*


