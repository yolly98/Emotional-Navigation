# Emotional Navigation

University project for "Industrial Applications" course (MSc Computer Engineering @ University of Pisa).

## Overview

Implemented in Python as a client-server system system with the goal of providing directions while driving and building a unique user experience based on emotions.
Specifically, the requirements and functionality of the application are as follows.

 * Must be able to **geolocate** the user on the road and **provide directions** if a destination has been set
 * The route is **automatically recalculated** whenever the user deviates from the route that was established
 * The client module is activated after detecting a face through a **face detection** service
 * the client module recognizes users through a **face recognition** service, if the user is unknown a new user profile is created
 * Each user has a **profile** consisting of username, face image for authentication, and an emotional history
 * The system periodically detects the user's emotions and associates them with the stretch of road being traveled, these tuples (emotion, road, timestamp) will compose the user's **emotional history**
 * Whenever a path has to be constructed from the current location to a destination, that path has to be **evaluated through the emotional history**, if the route is evaluated negatively (because it is composed of roads not liked by the user) a better rated path is chosen that does not bring too much delay
 * The client module must **interact** with the user **vocally**
 * The system initiates speech recognition if the user presses a specially designed button

## Getting Started

Install all libraries

```bash
pip install -r requirements.txt
```

Initialize the server

```bash
cd build
make
python3 initialization.py
```

Run the Server

```bash
python3 -m Server.server
```

Run the Client

```bash
python3 -m Cleint.client
```

### Note: 
* modify the config.json file in Client/Resource to prepare your client
* install ffmpeg
* install flac on Linux
* use 'pip install -r requirements.txt --no-cache-dir' if the process crash during the installation

## Project Architecture

```
Emotional Navigation
├── README.md
├── arduino_module.ino
├── build
│   ├── Makefile
│   └── initialization.py
├── requirements.txt
├── Client
│   ├── Dashboard
│   │   ├── View
│   │   │   ├── alert.py
│   │   │   ├── arrow.py
│   │   │   ├── car.py
│   │   │   ├── face.py
│   │   │   ├── path_progress.py
│   │   │   └── terminal.py
│   │   └── dashboard.py
│   ├── InOutModules
│   │   ├── Test
│   │   │   ├── gps_collector_test.py
│   │   │   └── gps_module_sim.py
│   │   ├── arduino_button_module.py
│   │   ├── face_processing_module.py
│   │   ├── gps_external_module.py
│   │   ├── gps_manager.py
│   │   └── vocal_inout_module.py
│   ├── Monitor
│   │   └── monitor.py
│   ├── Resources
│   │   ├── MonitorData
│   │   ├── MonitorSignal
│   │   ├── UserImages
│   │   ├── bip.wav
│   │   ├── config.json
│   │   ├── gps-test.json
│   │   └── temp.mp3
│   ├── client.py
│   ├── communication_manager.py
│   └── state_manager.py
└── Server
    ├── Core
    │   ├── emotional_route_selector.py
    │   └── map_engine.py
    ├── Persistence
    │   ├── map_manager.py
    │   └── user_data_manager.py
    ├── listener.py
    └── server.py

```

## Author

Gianluca Gemini, g.gemini@studenti.unipi.it


