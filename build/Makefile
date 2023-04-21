MONGO_IMAGE = mongo_smart_navigation
GRAPHHOPPER_IMAGE = graphhopper_smart_navigation
NOMINATIM_IMAGE = nominatim_smart_navigation

all: run

run:
	docker run --name ${MONGO_IMAGE} -d -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=password -p 27017:27017 mongo
	docker run --name ${GRAPHHOPPER_IMAGE} -d -p 8989:8989 israelhikingmap/graphhopper --url https://download.geofabrik.de/europe/italy/centro-latest.osm.pbf --host 0.0.0.0
	docker run --name ${NOMINATIM_IMAGE} -d -e PBF_URL=https://download.geofabrik.de/europe/italy/centro-latest.osm.pbf -p 8080:8080 mediagis/nominatim:4.2
	python3 initialization.py

start:
	docker start ${MONGO_IMAGE} ${GRAPHHOPPER_IMAGE} ${NOMINATIM_IMAGE}

stop:
	docker stop ${MONGO_IMAGE} ${GRAPHHOPPER_IMAGE} ${NOMINATIM_IMAGE}

clean:
	docker stop ${MONGO_IMAGE} ${GRAPHHOPPER_IMAGE} ${NOMINATIM_IMAGE}
	docker rm ${MONGO_IMAGE} ${GRAPHHOPPER_IMAGE} ${NOMINATIM_IMAGE}