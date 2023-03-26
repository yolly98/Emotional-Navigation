# TODO

## map engine
* [x] le deviazioni non funzionano
* [ ] ricaricare il db togliendo le strade e i nodi di edifici (strade senza name, ref, alt_name)
* [x] fare funzione che ricava posizione nella mappa tramite coordinate (trova il nodo con le coordinate piu vicine)

## dashboard
* [x] inserire due input per indicare partenza e destinazione
* [x] rendere la simulazione la dashboard stessa

## simulatore di guida
* [x] aggiungere frecce per curve
* [x] mettere avanzamento percorso

## rilevatore emozioni
* [x] creare modulo per rilevatore emozioni

## storico
* [ ] capire come salvare lo storico

## integrazione
* [x] integrare calcolo percorsi e simulatore di guida
* [ ] integrare simulatore guida e raccolta emozioni
* [ ] integrare simulatore guida con salvataggio nello storico

## sperimentazione reale
* [x] con una sorgente non presente nel db non posso fare il get_path, cercare coordinate più vicine
* [ ] attenzione a crash durante il cambio percorso in corsa
* [ ] mettere un controllo che calcola quanto si è distanti dal nodo del path piu vicino, se troppo distante va richiesto il ricalcolo 
* [ ] testare arduino + gps
* [ ] adattare simulazione ad uso di GPS