# Note

* NON USARE MICROFONO TELECAMERA

## Installazione rasberry
* ricorda di installare flac (apt-get install flac) altrimenti non funzionerà il microfono
* per installare i requirements fare ' pip install -r requirements.txt --no-cache-dir'
* per avviare il client mettersi nella cartella del progetto e fare 'python3 -m Client.client'
* per ora pygame non funziona se il rasberry non è connesso ad uno schermo, provare a farlo funzionare con VNC
* installa espeak su linux ->  sudo apt update && sudo apt install espeak ffmpeg libespeak1


# virtualenv

* (il virtual environment viene creato nella cartella in cui ci si trova)
* creare il virtual env
* $virtualenv venv
* attivare il virtual environment
* $source venv/bin/activate
* disattivare il virtual environment
* $deactivate

--------------------------------

# start VNC server

systemctl start vncserver-x11-serviced.service
