# TODO

## importante
* [x] nATTENZIONE !   qunado prende il nearest point potrebbe prendre un punto di un edificio, e poi non trovare il path!
* [ ] sostituire mysql con mongo

## map engine
* [x] le deviazioni non funzionano
* [x] ricaricare il db togliendo le strade e i nodi di edifici (strade senza name, ref, alt_name)
* [x] fare funzione che ricava posizione nella mappa tramite coordinate (trova il nodo con le coordinate piu vicine)
* [ ] migliorare prestazioni !!!IMPORTANTE

## dashboard
* [x] inserire due input per indicare partenza e destinazione
* [x] rendere la simulazione la dashboard stessa
* [ ] integrare riconoscimento comandi vocali

## simulatore di guida
* [x] aggiungere frecce per curve
* [x] mettere avanzamento percorso
* [x] crash quando finisce il percorso
* [ ] aggiungere emoji mood attuale (in alto a dx)

## rilevatore emozioni
* [x] creare modulo per rilevatore emozioni
* [ ] migliorare prestazioni !!!IMPORTANTE

## storico
* [x] capire come salvare lo storico

## integrazione
* [x] integrare calcolo percorsi e simulatore di guida
* [x] integrare simulatore guida e raccolta emozioni
* [x] integrare simulatore guida con salvataggio nello storico

## emotion_route_selctor
* [x] da fare completamente

## comandi vocali
* [ ] implementare completamente

## sperimentazione reale
* [x] con una sorgente non presente nel db non posso fare il get_path, cercare coordinate più vicine
* [x] attenzione a crash durante il cambio percorso in corsa
* [ ] mettere un controllo che calcola quanto si è distanti dal nodo del path piu vicino, se troppo distante va richiesto il ricalcolo 
* [ ] testare arduino + gps
* [ ] adattare simulazione ad uso di GPS