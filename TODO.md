# TODO

* [x] rifare il makefile

## map engine
* [x] le deviazioni non funzionano
* [x] ricaricare il db togliendo le strade e i nodi di edifici (strade senza name, ref, alt_name)
* [x] fare funzione che ricava posizione nella mappa tramite coordinate (trova il nodo con le coordinate piu vicine)
* [x] migliorare prestazioni !!!IMPORTANTE

## dashboard
* [x] inserire due input per indicare partenza e destinazione
* [x] rendere la simulazione la dashboard stessa
* [x] integrare riconoscimento comandi vocali
* [x] capire come risolvere il fatto che con i comandi vocali non azzecca le lettere maiuscole e minuscole
* [x] non si attiva alert per velocita
* [x] non da le indicazioni stradali vocali

## simulatore di guida
* [x] aggiungere frecce per curve
* [x] mettere avanzamento percorso
* [x] crash quando finisce il percorso
* [x] aggiungere emoji mood attuale (in alto a dx)
* [x] non riconosce quando un path è terminato (nel get_wat considera un last_pos_index indietro)
* [x] crasha se si fa partire un secondo path

## rilevatore emozioni
* [x] creare modulo per rilevatore emozioni
* [x] migliorare prestazioni !!!IMPORTANTE

## storico
* [x] capire come salvare lo storico

## integrazione
* [x] integrare calcolo percorsi e simulatore di guida
* [x] integrare simulatore guida e raccolta emozioni
* [x] integrare simulatore guida con salvataggio nello storico

## emotion_route_selctor
* [x] da fare completamente

## comandi vocali
* [x] implementare completamente

## sperimentazione reale
* [x] con una sorgente non presente nel db non posso fare il get_path, cercare coordinate più vicine
* [x] attenzione a crash durante il cambio percorso in corsa
* [x] mettere un controllo che calcola quanto si è distanti dal nodo del path piu vicino, se troppo distante va richiesto il ricalcolo 
* [x] testare funzionamento con coordinate reali (da json)
* [ ] testare arduino + gps
* [x] adattare simulazione ad uso di GPS
* [ ] risolvere bug su velocità da coordinate gps reali (nei dati raccolti i timestamp non distano di 1s!)