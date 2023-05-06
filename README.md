# Note

## Installazione rasberry
* ricorda di installare flac (apt-get install flac) altrimenti non funzionerà il microfono
* per installare i requirements fare ' pip install -r requirements.txt --no-cache-dir'
* per avviare il client mettersi nella cartella del progetto e fare 'python3 -m Client.client' (attenzione alla posizione dei file)
* per ora pygame non funziona se il rasberry non è connesso ad uno schermo, provare a farlo funzionare con VNC
* installa espeak su linux ->  sudo apt update && sudo apt install espeak ffmpeg libespeak1

# mic test

* per vedere i dispositivi
* $arecord --list-devices
* per registrare l'audio
* $arecord --format=S16_LE --rate=16000 --file-type=wav out.wav
* per ascoltare la registrazione
* $aplay out.wav

--------------------------------

# camera test

* scattare una foto
* $libcamera-still -r -o test.jpg
* per vedere cosa sta acquisendo la camera posso creare una nuova sorgente su vlc (vlc rtsp://<ip-addr-of-server>:8554/stream1)
* $libcamera-vid -t 0 --inline -o - | cvlc stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8554/stream1}' :demux=h264

--------------------------------

# virtualenv

* (il virtual environment viene creato nella cartella in cui ci si trova)
* creare il virtual env
* $virtualenv venv
* attivare il virtual environment
* $source venv/bin/activate
* disattivare il virtual environment
* $deactivate

--------------------------------
