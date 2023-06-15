DATASET = https://download.geofabrik.de/europe/italy/centro-latest.osm.pbf
MONGO_IMAGE = mongo_emotional_navigation
GRAPHHOPPER_IMAGE = graphhopper_emotional_navigation
NOMINATIM_IMAGE = nominatim_emotional_navigation

all: run

run:
	docker run --name ${MONGO_IMAGE} -d -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=password -p 27017:27017 mongo
	docker run --name ${GRAPHHOPPER_IMAGE} -d -p 8989:8989 israelhikingmap/graphhopper --url ${DATASET} --host 0.0.0.0
	docker run --name ${NOMINATIM_IMAGE} -d -e PBF_URL=${DATASET} -p 8080:8080 mediagis/nominatim:4.2
	python3 initialization.py

start:
	docker start ${MONGO_IMAGE} ${GRAPHHOPPER_IMAGE} ${NOMINATIM_IMAGE}

stop:
	docker stop ${MONGO_IMAGE} ${GRAPHHOPPER_IMAGE} ${NOMINATIM_IMAGE}

clean:
	docker stop ${MONGO_IMAGE} ${GRAPHHOPPER_IMAGE} ${NOMINATIM_IMAGE}
	docker rm ${MONGO_IMAGE} ${GRAPHHOPPER_IMAGE} ${NOMINATIM_IMAGE}