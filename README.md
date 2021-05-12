#**Rapport Projet IOC**

---
## Introduction
Ce projet consiste à implémenter une application web pour contrôler la carte ESP32_TTGO_OLED. L'objectif c'est d'afficher sur un graphe de luminosité au cours du temps à partir des valeurs lu de la photorésistance, et de d'afficher les message de l'utilisateur dans l'ecran de la carte.

Pour ce faire on implémente dans la RPi (le gateway) un serveur HTTP avec le framework **Flask**. Les données transférées entre la carte ESP32 et la RPi à l'aide du protocole MQTT, on aura deux topics `/display` et `/sensor`

Ou:

|   topic  |publisher| subscriber|
|----------|:-------:|:---------:|
| /display | RPi     |ESP32      |
| /sensor  |ESP32    |RPi        |

Une base de données `SQLite` a été implémentée pour sauvegarder les données (valeur du capteur) en mémoire.

Pour l'affichage du graphe on utiliser l'outil fourni par google `Google Charts`

## Configuration de la RPi
### 1- Installation et Configuration du Raspbian
* On télécharge *Raspbian* depuis le [site officiel](https://www.raspberrypi.org/software/operating-systems/#raspberry-pi-os-32-bit) et on l'installe  sur la carte SD. (Sur Windows on peut utiliser Rufus)

  *Facultatif-- pour vérifier l'intégrité du fichier téléchargé:*

  `sha256sum <fichier téléchargé> | grep <hash du fichier>`

pour activer le wifi et connecter automatiquement au point d'accès:
* On active la communication en SSH:
Dans le drive **boot** on crée un fichier vide appelée ssh (sans extension) `touch ssh`

* Dans le fichier  **wpa_supplicant.conf** on rajoute
```
country=FR
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
network={
scan_ssid=1
ssid="your_wifi_ssid"
psk="your_wifi_password"
}
```
* Insérer la carte SD dans la Rpi et alimenter. Puis vérifier qu'elle bien connecté au point d'accès et que la connection *SSH* marche bien.

### 2- Installation et test du Mosquitto MQTT broker

* On installe Mosquitto
```
sudo apt update
sudo apt install -y mosquitto mosquitto-clients
```
* On arrête mosquitto pour le configurer:

    `sudo stop mosquitto`

* On crée le fichier contenant le mot de passe avec le nom d'utilisateur:
  *short version:*

  `sudo mosquitto_passwd -c /etc/mosquitto/pwfile <mqtt_username>`

  Et on nous demande d'entrer le mot de passe et de le confirmer.

  *long version:*
 
  ```  
  echo "<mqtt_username>:<mqtt_passwd>" > pwfile
  mosquitto_passwd -U pwfile
  sudo mv pwfile /etc/mosquitto/
  ```

* Dans le fichier `/etc/mosquitto/mosquitto.conf` on ajoute ces deux lignes:

  ```
  log...
  ---> allow_anonymos false
  ---> password_file /etc/mosquitto/pwfile
  include...
  ```
* On redémare le broker

  `mosquitto -c /etc/mosquitto/mosquitto.conf`

  ou

  `sudo /etc/init.d/mosquitto restart`

Pour tester si ça a bien installé on ouvre deux terminaux ou le premier serait le **subscriber** et le second serait le **publisher**:

Terminal 1:

`mosquitto_sub -d -u <username> -P <password> -t <topic>`
 
 On peut également remplacer \<topic> par "#" pour recevoire tous les messages publier

Terminal 2:

`mosquitto_pub -d -u <username> -P <password> -t <topic> -m <message>`

Si tout marche bien, le message envoyé doit s'afficher dans le terminal 1. Sinon redémarrer et retester.

## 3. Créer un environnement virtuel et installation des packages

1. Create virtual environment:
  * installer python3 (pour Flask):

    `sudo apt install python3`

  * installer package manager pip:

    `sudo apt install pip`

  * créer un environnement virtuel nommé *ioc*  puis l'activer(dans le dossier du projet):

    `python3 -m venv ioc`

    `source ioc/bin/activate`

    `which python`    *(pour vérifier)*

  * installer flask, sqlite3 et paho-mqtt:

    `pip install flask`

    `pip install sqlite3`

    `pip install paho-mqtt`

## Configurer la carte esp32-TTGO-OLED

Les libraries à installer:
1. **Adafruit_BusIO** :a helper library to abstract away I2C & SPI transactions and registers.
2. **Adafruit-GFX-Library** : the core graphics library for all our displays, providing a common set of graphics primitives (points, lines, circles, etc.).
3. **Adafruit_SSD1306**:  a library for the Monochrome OLEDs based on SSD1306 drivers.
4. **WiFiClientSecure**: The WiFiClientSecure class implements support for secure connections using TLS (SSL). It inherits from WiFiClient and thus implements a superset of that class' interface.
5. **PubSubClien**: This library provides a client for doing simple publish/subscribe messaging with a server that supports MQTT.

## A changer dans le code app.py et node.ino
* wifi: ssid et password
* mqtt: mqtt_broker (IP address of RPi), mqtt_username et mqtt_password

## Run server
`python3 app.py`
ou encore
`flask run`

*note: si le nom du fichier n'est pas app.py on doit:
`export FLASK_APP=<nom>.py`*

